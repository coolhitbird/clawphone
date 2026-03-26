#!/usr/bin/env python3
"""
ClawPhone + ClawMesh 集成示例

演示如何使用 ClawMesh 网络进行跨 NAT 通信。
"""

import asyncio
import logging
from skills.clawphone.adapter.clawphone import (
    register, start_mesh_mode, call, add_contact, on_message
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """主函数：演示 ClawPhone + ClawMesh 使用"""
    
    # 1. 注册号码（只需一次）
    my_phone = register("xiaoxin")
    logger.info(f"我的号码: {my_phone}")
    
    # 2. 设置消息回调
    def handle_incoming(msg):
        sender = msg.get('from', 'unknown')
        content = msg.get('content', '')
        logger.info(f"📨 收到来自 {sender} 的消息: {content}")
    
    on_message(handle_incoming)
    
    # 3. 启动 ClawMesh 网络模式
    # 假设你已经有一个 STUN server 运行在 127.0.0.1:8766
    my_node_id = "CL-XIAOXIN"  # 自定义 node_id，或留空使用 phone_id
    await start_mesh_mode(
        node_id=my_node_id,
        stun_servers=[("127.0.0.1", 8766)],
        enable_crypto=False  # 测试时可关闭加密
    )
    logger.info("ClawMesh 网络已启动")
    
    # 4. 添加联系人（需要对方的 phone_id 和 node_id）
    # 假设对方的 phone_id 是 9900778313722，node_id 是 "CL-B"
    add_contact(
        alias="好友B",
        phone_id="9900778313722",
        node_id="CL-B",
        address="CL-B"  # ClawMesh 模式下 address 存 node_id
    )
    
    # 5. 发送消息
    logger.info("发送消息给好友B...")
    success = call("9900778313722", "你好！这是通过 ClawMesh 发送的消息。")
    if success:
        logger.info("✅ 消息发送成功")
    else:
        logger.error("❌ 消息发送失败")
    
    # 6. 保持运行
    logger.info("按 Ctrl+C 退出")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("退出中...")

if __name__ == "__main__":
    asyncio.run(main())
