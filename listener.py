#!/usr/bin/env python3
"""
ClawPhone 在线监听服务
让其他 Agent 可以通过号码联系我
"""

import sys
import time
import logging
from pathlib import Path

# 添加 workspace 到 path
WORKSPACE = Path(r"C:\Users\wang20\.openclaw\workspace")
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from skills.clawphone.adapter.clawphone import ClawPhone
from skills.clawphone.adapter.direct import DirectAdapter

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

# 创建 ClawPhone 实例
phone = ClawPhone()

# 设置消息回调
def on_message(msg):
    print(f"\n[📨 收到消息]")
    print(f"  来自: {msg.get('from', '未知')}")
    print(f"  内容: {msg.get('content', '')}")
    print(f"  时间: {msg.get('timestamp', 'N/A')}")
    print("-" * 40)

phone.on_message = on_message

# 启动 DirectAdapter（监听端口 8766）
adapter = DirectAdapter("assistant", listen_port=8766)
adapter.start()  # 启动服务器
phone.set_adapter(adapter)

print("=" * 50)
print("🤖 ClawPhone 在线监听已启动")
print(f"📱 我的号码: {phone.my_phone_id}")
print(f"🌐 监听地址: {adapter.get_my_address()}")
print("💡 其他 Agent 可以通过此号码发送消息")
print("=" * 50)
print("\n等待消息 incoming... (Ctrl+C 退出)\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 停止监听")
    adapter.stop()
