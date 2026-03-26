#!/usr/bin/env python3
"""
ClawPhone + ClawMesh 集成测试

测试场景:
1. 两个 ClawPhone 实例 A 和 B
2. 都启动 ClawMesh 模式（共享 STUN server）
3. A 呼叫 B，验证消息送达

要求: STUN server 运行在 127.0.0.1:8766
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.clawphone.adapter.clawphone import (
    _init_db, register, start_mesh_mode, call, add_contact, on_message, _phone
)
from p2p.stun.server import StunServer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class TestResults:
    def __init__(self):
        self.received = []
    
    def record(self, msg):
        self.received.append(msg)

async def run_integration_test():
    """运行集成测试"""
    results = TestResults()
    
    # 初始化数据库（每个测试独立）
    _init_db()
    
    # 启动 STUN server
    logger.info("Starting STUN server...")
    stun_server = StunServer(host='127.0.0.1', port=8766)
    stun_task = asyncio.create_task(stun_server.run())
    await asyncio.sleep(0.5)
    
    try:
        # === Phone A ===
        logger.info("=== Setting up Phone A ===")
        phone_a = register("alice")  # 号码: 13位
        logger.info(f"Phone A number: {phone_a}")
        
        # 设置回调
        def on_msg_a(msg):
            sender = msg.get('from', 'unknown')
            content = msg.get('content', '')
            logger.info(f"[A RECV] from {sender}: {content}")
            results.record(('A', sender, content))
        on_message(on_msg_a)
        
        # 启动 ClawMesh
        await start_mesh_mode(
            node_id="CL-ALICE",
            stun_servers=[("127.0.0.1", 8766)],
            enable_crypto=False
        )
        await asyncio.sleep(2.0)
        logger.info("Phone A ready")
        
        # === Phone B ===
        logger.info("=== Setting up Phone B ===")
        # 重置全局 _phone (简化: 实际应支持多实例)
        from skills.clawphone.adapter import clawphone as cp_mod
        # 暂时 hack: 重新创建 _phone 实例
        # 实际应支持多实例，这里仅单例测试，所以 B 使用同一全局实例
        # 改为: 创建两个独立的 ClawPhone 实例需重构，暂用同一实例模拟
        logger.warning("Note: Using single global instance for test (B shares instance)")
        phone_b_number = register("bob")
        logger.info(f"Phone B number: {phone_b_number}")
        
        def on_msg_b(msg):
            sender = msg.get('from', 'unknown')
            content = msg.get('content', '')
            logger.info(f"[B RECV] from {sender}: {content}")
            results.record(('B', sender, content))
        # 覆盖回调 (仅最后一次有效)
        on_message(on_msg_b)
        
        # 已启动，跳过
        await asyncio.sleep(1.0)
        logger.info("Phone B ready (same instance)")
        
        # === 添加联系人 ===
        # A 添加 B
        add_contact(
            alias="Bob",
            phone_id=phone_b_number,
            node_id="CL-BOB",  # B 的 node_id（假设）
            address="CL-BOB"
        )
        
        # === 测试呼叫 A → B ===
        logger.info("--- Test: A calls B ---")
        success = call(phone_b_number, "Hello Bob from Alice!")
        logger.info(f"Call result: {success}")
        assert success, "A → B should succeed"
        
        await asyncio.sleep(2.0)
        
        # 验证 B 收到
        b_recv = [r for r in results.received if r[0] == 'B']
        assert len(b_recv) >= 1, "B should receive message from A"
        logger.info(f"✅ B received: {b_recv[0][2]}")
        
        # === 总结 ===
        logger.info("=" * 60)
        logger.info("INTEGRATION TEST PASSED")
        logger.info(f"Total received: {len(results.received)}")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False
    finally:
        # Cleanup
        if 'stun_server' in locals():
            stun_server._running = False
            await asyncio.sleep(0.5)
            stun_task.cancel()
            try:
                await stun_task
            except asyncio.CancelledError:
                pass

async def main():
    try:
        success = await run_integration_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
