#!/usr/bin/env python3
"""注册官方号码"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.clawphone.adapter.clawphone import _phone, register

# 设置 node_id (模拟)
_phone._my_node_id = "CL-01S-MASTER-001"

# 注册
num = register("clawmesh_official")
print(f"✅ 官方号码已注册: {num}")
print(f"📝 请记录此号码，用于社区发布和联系方式")
