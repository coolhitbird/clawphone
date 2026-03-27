#!/usr/bin/env python3
"""
ClawPhone + ClawMesh 集成测试（单实例验证版）

测试场景:
1. 单个 ClawPhone 实例
2. 启动 ClawMesh 模式
3. 通过 on_message 回调接收消息
4. 验证自己发送给自己（loopback）成功

要求: STUN server 运行在 127.0.0.1:8766
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup paths
workspace_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(workspace_root))
sys.path.insert(0, str(workspace_root / "projects" / "OpenClaw-Network"))

from skills.clawphone.adapter.clawphone import (
    _phone, start_mesh_mode, call, on_message, register
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
    
    # 启动 STUN server
    logger.info("Starting STUN server...")
    stun_server = StunServer(host='127.0.0.1', port=8766)
    stun_task = asyncio.create_task(stun_server.run())
    await asyncio.sleep(0.5)
    
    try:
        # === 注册并设置 ===
        logger.info("=== Setting up ClawPhone ===")
        my_number = register("testuser")
        logger.info(f"My number: {my_number}")
        
        # 设置消息回调
        def handle_msg(msg):
            sender = msg.get('from', 'unknown')
            content = msg.get('content', '')
            logger.info(f"[RECV] from {sender}: {content}")
            results.record(msg)
        on_message(handle_msg)
        
        # 启动 ClawMesh
        await start_mesh_mode(
            node_id="CL-TESTUSER",
            stun_servers=[("127.0.0.1", 8766)],
            enable_crypto=False
        )
        await asyncio.sleep(2.0)
        logger.info("ClawPhone ready with ClawMesh")
        
        # === 添加一个自环触点 ===
        # 将自己添加为联系人（node_id 相同）
        from skills.clawphone.adapter.clawphone import add_contact
        add_contact(
            alias="self",
            phone_id=my_number,
            node_id="CL-TESTUSER",
            address="CL-TESTUSER"
        )
        
        # === 测试: 发送消息给自己 ===
        logger.info("--- Test: loopback call ---")
        success = call(my_number, "Hello myself! This is a loopback test.")
        logger.info(f"Call result: {success}")
        assert success, "Loopback call should succeed"
        
        await asyncio.sleep(2.0)
        
        # 验证收到
        assert len(results.received) >= 1, "Should receive at least one message"
        received = results.received[-1]
        logger.info(f"✅ Received: from={received.get('from')}, content={received.get('content')}")
        assert received.get('content') == "Hello myself! This is a loopback test."
        
        # === 结论 ===
        logger.info("=" * 60)
        logger.info("INTEGRATION TEST PASSED")
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
