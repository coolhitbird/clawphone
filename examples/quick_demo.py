#!/usr/bin/env python3
"""
ClawPhone 快速演示
用法: uv run python examples/quick_demo.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.clawphone.adapter.clawphone import (
    register,
    call,
    lookup,
    on_message,
    set_network
)


# 模拟网络（实际应该连接 ClawMesh）
class MockNetwork:
    """模拟网络适配器（实际会替换为 ClawMesh send）"""

    def __init__(self, my_node_id: str):
        self.my_node_id = my_node_id
        self.peers = {}  # phone_id -> node_id

    def send(self, node_id: str, data: str):
        print(f"[NETWORK] 发送到 {node_id}: {data[:50]}...")
        # 模拟立即收到回复
        if "ping" in data.lower():
            response = {
                "type": "call",
                "from": "@claw_brother_3f9",
                "to": "??",
                "content": "pong! 我在线。",
                "timestamp": 1234567890
            }
            # 触发回调
            from skills.clawphone.adapter.clawphone import _phone
            if _phone.on_message:
                _phone.on_message(response)


async def main():
    print("=== ClawPhone 快速演示 ===\n")

    # 1️⃣ 初始化网络（这里用模拟器）
    my_node_id = "CL-01S-SERVER-001"  # 示例 node_id
    net = MockNetwork(my_node_id)
    set_network(net)

    # 2️⃣ 注册号码
    print("1. 注册我的号码...")
    my_phone = register("xiaoxin")
    print(f"   ✅ 我的号码: {my_phone}\n")

    # 3️⃣ 查询对方号码
    print("2. 查询好友号码...")
    brother_node = lookup("@claw_brother_3f9") or "CL-01S-CLIENT-999"
    print(f"   ✅ 对方的 node_id: {brother_node}\n")

    # 4️⃣ 设置消息回调
    print("3. 设置消息接收回调...")
    def my_callback(msg):
        print(f"\n🔔 收到新消息 from {msg['from']}: {msg['content']}\n")

    on_message(my_callback)

    # 5️⃣ 发送呼叫
    print("4. 发送测试呼叫...")
    success = call("@claw_brother_3f9", "ping - 你在吗？")
    print(f"   {'✅' if success else '❌'} 发送状态: {success}\n")

    # 6️⃣ 等待响应
    print("5. 等待响应 (3秒)...")
    await asyncio.sleep(3)

    print("\n=== 演示结束 ===")


if __name__ == "__main__":
    asyncio.run(main())
