#!/usr/bin/env python3
"""
ClawPhone + ClawMesh 直连模式集成测试（绕过 STUN）

测试场景:
1. 两个 ClawPhone 实例 A 和 B
2. 直接创建 UdpDirectTransport（不依赖 STUN query）
3. 手动交换 endpoint 并添加到 connection pool
4. A → B 消息直达，验证闭环

要求: 无（STUN server 可选）
"""

import asyncio
import logging
import sys
import tempfile
from pathlib import Path

# Setup paths
workspace_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(workspace_root))
sys.path.insert(0, str(workspace_root / "projects" / "OpenClaw-Network"))

from skills.clawphone.adapter.clawphone import ClawPhone
from p2p.transport.udp_direct import UdpDirectTransport
from p2p.config import UdpTransportConfig, StunConfig, PunchHoleConfig
from adapter.message import Message, MessagePayload, MessageRouting, MessageMeta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class TestResults:
    def __init__(self):
        self.received = []
    
    def record(self, source, sender, content):
        self.received.append((source, sender, content))

async def run_integration_test():
    """运行集成测试"""
    results = TestResults()
    
    # 临时数据库
    db_a = tempfile.NamedTemporaryFile(delete=False, suffix=".db", prefix="phone_a_")
    db_b = tempfile.NamedTemporaryFile(delete=False, suffix=".db", prefix="phone_b_")
    db_a.close()
    db_b.close()
    
    # 配置（无 STUN）
    config = UdpTransportConfig(
        stun=StunConfig(servers=[]),  # 禁用 STUN
        punch_hole=PunchHoleConfig(timeout=5.0),
        enable_crypto=False
    )
    
    try:
        # === 创建 Phone A ===
        logger.info("=== Creating Phone A ===")
        phone_a = ClawPhone(db_path=db_a.name)
        phone_a_id = "CL-ALICE"
        phone_a._my_node_id = phone_a_id
        phone_a.set_status("online")
        phone_a._my_phone_id = phone_a.register("alice")
        logger.info(f"Phone A: node_id={phone_a_id}, phone_id={phone_a._my_phone_id}")
        
        # 创建 Transport A
        transport_a = UdpDirectTransport(
            config=config,
            node_id=phone_a_id,
            message_handler=lambda msg, sender: results.record('A', sender, msg.payload.content)
        )
        await transport_a.start()
        addr_a = transport_a.local_endpoint
        logger.info(f"Transport A bound to {addr_a}")
        
        # === 创建 Phone B ===
        logger.info("=== Creating Phone B ===")
        phone_b = ClawPhone(db_path=db_b.name)
        phone_b_id = "CL-BOB"
        phone_b._my_node_id = phone_b_id
        phone_b.set_status("online")
        phone_b._my_phone_id = phone_b.register("bob")
        logger.info(f"Phone B: node_id={phone_b_id}, phone_id={phone_b._my_phone_id}")
        
        # 创建 Transport B
        transport_b = UdpDirectTransport(
            config=config,
            node_id=phone_b_id,
            message_handler=lambda msg, sender: results.record('B', sender, msg.payload.content)
        )
        await transport_b.start()
        addr_b = transport_b.local_endpoint
        logger.info(f"Transport B bound to {addr_b}")
        
        # === 手动交换 endpoint 并添加到 connection pool ===
        logger.info("=== Exchanging endpoints manually ===")
        
        # 使用 127.0.0.1 替换 0.0.0.0 作为目标地址
        addr_a_fixed = ('127.0.0.1', addr_a[1])
        addr_b_fixed = ('127.0.0.1', addr_b[1])
        
        # A 添加 B 的 endpoint
        await transport_a.connection_pool.add(phone_b_id, addr_b_fixed)
        logger.info(f"A added B endpoint: {addr_b_fixed}")
        
        # B 添加 A 的 endpoint
        await transport_b.connection_pool.add(phone_a_id, addr_a_fixed)
        logger.info(f"B added A endpoint: {addr_a_fixed}")
        
        # 手动添加路由条目（下一跳就是目标本身）
        await transport_a.routing.add(phone_b_id, phone_b_id, metric=1, source="manual")
        await transport_b.routing.add(phone_a_id, phone_a_id, metric=1, source="manual")
        logger.info("Routes added manually")
        
        await asyncio.sleep(0.5)
        
        # === 测试: A -> B ===
        logger.info("--- Test: A sends to B ---")
        msg_a2b = Message(
            meta=MessageMeta(
                node_id=phone_a_id,
                timestamp=int(asyncio.get_event_loop().time()),
                protocol_version="1.0"
            ),
            payload=MessagePayload(
                type="text",
                content="Hello Bob from Alice!"
            ),
            routing=MessageRouting(
                to=phone_b_id,
                hops=[],
                ttl=10,
                route_required=True
            )
        )
        
        success = await transport_a.send(msg_a2b, phone_b_id)
        logger.info(f"A->B send result: {success}")
        assert success, "A -> B send should succeed"
        
        await asyncio.sleep(1.0)
        
        # 验证 B 收到
        b_msgs = [r for r in results.received if r[0] == 'B']
        assert len(b_msgs) >= 1, "B should receive message from A"
        logger.info(f"✅ B received: {b_msgs[0][2]}")
        
        # === 测试: B -> A ===
        logger.info("--- Test: B sends to A ---")
        msg_b2a = Message(
            meta=MessageMeta(
                node_id=phone_b_id,
                timestamp=int(asyncio.get_event_loop().time()),
                protocol_version="1.0"
            ),
            payload=MessagePayload(
                type="text",
                content="Hi Alice! This is Bob."
            ),
            routing=MessageRouting(
                to=phone_a_id,
                hops=[],
                ttl=10,
                route_required=True
            )
        )
        
        success = await transport_b.send(msg_b2a, phone_a_id)
        logger.info(f"B->A send result: {success}")
        assert success, "B -> A send should succeed"
        
        await asyncio.sleep(1.0)
        
        a_msgs = [r for r in results.received if r[0] == 'A']
        assert len(a_msgs) >= 1, "A should receive message from B"
        logger.info(f"✅ A received: {a_msgs[0][2]}")
        
        # === 结论 ===
        logger.info("=" * 60)
        logger.info("DIRECT INTEGRATION TEST PASSED")
        logger.info(f"Total messages received: {len(results.received)}")
        logger.info("=" * 60)
        return True
        
    except AssertionError as e:
        logger.error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False
    finally:
        # Cleanup
        logger.info("Cleaning up...")
        for t in [transport_a, transport_b]:
            try:
                await t.stop()
            except:
                pass
        try:
            Path(db_a.name).unlink(missing_ok=True)
            Path(db_b.name).unlink(missing_ok=True)
        except:
            pass
        logger.info("Cleanup done")

async def main():
    try:
        success = await run_integration_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
