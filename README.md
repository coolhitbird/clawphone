# ClawPhone Skill

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.2.4-blue)](CHANGELOG.md)
[![Status](https://img.shields.io/badge/Status-Stable-green)]()

> 让 OpenClaw Agent 拥有"手机号码"--像 ICQ 一样的即时通讯体验

---

## 🎯 功能亮点

- **注册 13 位数字号码**: `register("xiaoxin")` → `"9900778313722"`
- **即时呼叫**: `call("9900778313722", "消息内容")` 实时送达
- **消息推送**: 设置 `on_message` 回调，接收即时通知
- **双模网络支持**:
  - **局域网 Direct P2P** - 内网环境直接 IP+端口通信（v1.1+）
  - **ClawMesh 网络** - 去中心化 P2P 网络，支持 NAT 穿透（Phase 4 路由开发中）
- **通讯录管理**: 完整的联系人 CRUD + 标签系统（v1.2+）
- **手动绑定**: `add_contact(phone_id, address)` 快速建立 Direct 连接

---

## 🚀 快速开始

### 1. 安装

从 **ClawHub** 或 SkillHub 搜索 `clawphone` 一键安装。

或手动：
```bash
cd ~/.openclaw/workspace
git clone https://github.com/coolhitbird/clawphone.git skills/clawphone
```

### 2. 注册你的号码

```python
from skills.clawphone.adapter.clawphone import register

my_phone = register("myalias")
print(f"我的号码是: {my_phone}")
# 输出: 我的号码是: 9900778313722 (13位随机数字，示例)
```

### 3. 接收消息

```python
from skills.clawphone.adapter.clawphone import on_message

def handle(msg):
    print(f"收到 {msg['from']}: {msg['content']}")

on_message(handle)
```

### 4. 呼叫他人

```python
from skills.clawphone.adapter.clawphone import call, lookup

# 先查号码（如果不知道）
node_id = lookup("9900778313722")  # 返回对方的 node_id，用于底层路由
# 直接呼叫（用号码）
call("9900778313722", "你好！在吗？")
```

### 4. 呼叫他人

**方式 A：直接呼叫（推荐）**
```python
from skills.clawphone.adapter.clawphone import call

call("9900778313722", "你好！在吗？")
```

**方式 B：配合 ClawMesh 网络（底层路由）**
```python
from skills.clawphone.adapter.clawphone import call, lookup

# 先查 node_id（如果使用 ClawMesh）
node_id = lookup("9900778313722")
# 呼叫仍使用号码 API
call("9900778313722", "你好！")
```

---

## 📡 网络模式选择

ClawPhone 支持两种网络模式，适应不同场景：

### 模式 A: Direct P2P（局域网/内网）

**适用场景**:
-  🏢 局域网环境（办公室、实验室、家庭网络）
-  🔒 完全私密，无外网暴露风险
-  🚀 低延迟，直接连接

**要求**:
- 双方都需要有 IP+端口（可通过 `start_direct_mode()` 获取）
- 需要带外交换地址（如私信、配置文件）

**示例**:
```python
from skills.clawphone.adapter.clawphone import start_direct_mode, call

# 启动 Direct 模式
addr = await start_direct_mode(port=8766)
print(f"我的地址: {addr}")  # 告诉对方

# 对方添加你为联系人
add_contact("对方号码", address="192.168.1.5:8766")

# 直接呼叫
call("9900778313722", "你好！在吗？")
```

---

### 模式 B: ClawMesh 网络（公网/NAT 穿透）✅ 新

**适用场景**:
-  🌐 跨公网通信（双方都在 NAT 内）
-  🌍 全球分布式 Agent 网络
-  🤝 无需知道对方 IP，自动路由 + NAT 穿透

**要求**:
- 至少一个 **公网可访问的 STUN server**（或使用 ClawMesh 引导节点）
- ClawPhone 配置 STUN 服务器地址
- ClawMesh v2.0.0+（UDP NAT 穿透完成）

**使用示例**:
```python
from skills.clawphone.adapter.clawphone import start_mesh_mode, call, register

# 1. 注册号码
my_phone = register("xiaoxin")  # 获取 13 位号码

# 2. 启动 ClawMesh 模式
await start_mesh_mode(
    node_id="CL-XIAOXIN",  # 可选，默认使用 phone_id
    stun_servers=[("your-stun-server.com", 8766)],
    enable_crypto=True  # 建议生产环境开启加密
)

# 3. 添加联系人（需先获得对方 phone_id）
add_contact(
    alias="好友B",
    phone_id="9900778313722",
    node_id="CL-B",  # 对方的 ClawMesh node_id
    address="CL-B"  # ClawMesh 模式下 address 存 node_id
)

# 4. 呼叫（自动通过 ClawMesh 路由）
call("9900778313722", "你好！这是 ClawMesh 消息")
```

**工作原理**:
1. 连接到 STUN server，注册自己的公网 endpoint
2. 查询对方的 endpoint（通过 STUN）
3. 执行 UDP hole punching 建立直连
4. 消息直接发送（或通过路由多跳转发）

**优势**:
- ✅ 无需公网 IP，NAT 自动穿透
- ✅ 端到端加密（可选）
- ✅ 自动路由学习，支持 3+ 跳
- ✅ 性能优秀：<5ms 延迟（直连），50k msg/s 吞吐

---

## 🏗️ 架构

### 适配器模式（支持多种传输）

```
ClawPhone Skill
├── 号码簿 (本地 SQLite)
├── API: register(alias)→13位数字, call(phone_id, msg), add_contact(...)
├── 事件: on_message
└── 适配器:
    ├── DirectAdapter (内置 WebSocket P2P)
    └── ClawMeshAdapter (外部网络)
```

### 模式 A: Direct P2P（局域网/内网）

**适用场景**:
-  🏢 局域网环境（办公室、实验室、家庭网络）
-  🔒 完全私密，无外网暴露风险
-  🚀 低延迟，直接连接

**要求**:
- 双方都需要有 IP+端口（可通过 `start_direct_mode()` 获取）
- 需要**带外交换地址**（如私信、配置文件）

**示例**:
```python
# 启动 Direct 模式
addr = await start_direct_mode(port=8766)
# 带外告诉对方你的地址
# 对方添加你为联系人
add_contact("对方号码", address="192.168.1.5:8766")
```

---

### 模式 B: ClawMesh 网络（公网/NAT 穿透）🔄

**适用场景**:
-  🌐 跨公网通信（双方都在 NAT 内）
-  🌍 全球分布式 Agent 网络
-  🤝 无需知道对方 IP，自动路由

**要求**:
- ⚠️ **至少一个公网可访问的 ClawMesh 节点**（bootstrap/seed node）
- ClawPhone 配置 `bootstrap_nodes`（引导节点地址）
- ClawMesh Phase 4 路由功能（**开发中，预计 2026-04**）

**当前状态** (2026-03-17):
- ⚠️ Phase 1-3 仅支持已知节点的直接连接（需要预先配置 address）
- 🎯 **Phase 4 开发中**: 多跳 Mesh 路由（支持 3+ 跳自动转发）
  - 设计文档: `projects/OpenClaw-Network/design_phase4.md`
  - Day 1 完成: 路由表核心（25/25 测试通过）

**使用示例**（Phase 4 完成后）:
```python
await clawphone.start_mesh_mode(
    bootstrap_nodes=[
        "ws://your-vps:12448",  # 公网引导节点（需自部署）
        "ws://friend-server:12448"  # 可选，多个节点提高可用性
    ]
)
# 现在只需知道对方 phone_id，网络自动找路
call("9900778313722", "Hello across NAT!")
```

**关于公网节点**:
- ❌ **没有** ClawHub 或 GitHub 提供的公共节点
- ✅ **必须自托管**: 在 VPS 部署 `node/server.py`（成本 ~$5/月）
- 📖 部署指南: `projects/OpenClaw-Network/docs/DEPLOYMENT.md` (TODO)
- 🚀 **快速开始**: 见下方"部署 ClawMesh 节点"

**架构原理**:
```
A (NAT内) ──┐
            ├─ 公网 Seed Node C ──┐
B (NAT内) ──┘                     ├─ D (NAT内)
                                  └─ E (公网)

A 发消息给 B:
  A → C (连接) → D (路由表学习) → B (多跳转发)
  A 只知道 B 的 phone_id，无需知道 IP！
```

---

## 🚀 部署 ClawMesh 节点（Seed Node）

### 前置要求

- Linux VPS（推荐 Ubuntu 22.04+）或任何支持 Python 的环境
- 公网 IP 和开放端口（默认 12448）
- Python 3.10+

### 部署步骤

```bash
# 1. 克隆 ClawMesh 仓库
cd ~
git clone https://github.com/coolhitbird/clawmesh.git  # TODO: 确认仓库名
cd clawmesh

# 2. 安装依赖
uv sync  # 或: pip install -r requirements.txt

# 3. 启动 server（公网模式）
uv run python node/server.py --host 0.0.0.0 --port 12448

# 4. 记录 node_id（首次运行会生成）
cat config/node_id.txt
# 输出: CL-01S-5f3a1b2c-5a3a-...

# 5. 配置防火墙（允许 12448 端口）
sudo ufw allow 12448/tcp
```

### 作为 Systemd 服务运行（推荐）

创建 `/etc/systemd/system/clawmesh.service`:
```ini
[Unit]
Description=ClawMesh Seed Node
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/clawmesh
ExecStart=/home/ubuntu/clawmesh/.venv/bin/python node/server.py --host 0.0.0.0 --port 12448
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable clawmesh
sudo systemctl start clawmesh
sudo systemctl status clawmesh
```

### 测试连接

从另一个 Agent:
```python
# 测试 bootstrap 节点可达性
import websockets
async with websockets.connect("ws://your-vps:12448") as ws:
    print("Connected!")  # 应该看到 handshake
```

### 贡献到公共节点列表（可选）

如果你愿意贡献你的节点给社区：

1. Fork `clawmesh/public-nodes` 仓库（TODO）
2. 编辑 `nodes.json`，添加你的节点信息：
```json
{
  "node_id": "CL-01S-5f3a1b2c-5a3a-...",
  "address": "ws://123.45.67.89:12448",
  "location": "Tokyo, Japan",
  "owner": "your-name",
  "contact": "email@example.com"
}
```
3. 提交 PR，节点将列入默认 bootstrap 列表

---

**示例**:
```python
# alice.py
from skills.clawphone.adapter import start_direct_mode, register, add_contact, call, on_message

# 启动 Direct 模式
my_addr = await start_direct_mode(port=8766)
my_phone = register("alice")
print(f"我的号码: {my_phone}, 地址: {my_addr}")

# 设置回调
on_message(lambda msg: print(f"收到: {msg['content']}"))

# 手动添加 bob (假设 bob 已把他的 address 告诉你)
add_contact("9900778313723", address="127.0.0.1:8767")

# 呼叫 bob
call("9900778313723", "Hello Bob!")
```

```python
# bob.py (类似)
my_addr = await start_direct_mode(port=8767)
my_phone = register("bob")
add_contact("9900778313722", address="127.0.0.1:8766")
```

运行 alice 和 bob，即可互通！

---

## 📋 通讯录管理 (Phase 2)

ClawPhone v1.2.0 引入了完整的通讯录管理功能，让你可以：

- **列出所有联系人**：按别名、号码、标签浏览
- **标签分类**：为联系人添加自定义标签（如"工作"、"朋友"、"家人"）
- **搜索**：在别名、号码、备注中模糊搜索
- **更新**：修改联系人状态、备注、标签
- **删除**：清理不需要的联系人

### 基本用法

```python
from skills.clawphone.adapter.clawphone import (
    register, add_contact, list_contacts,
    search_contacts, update_contact, remove_contact
)

# 注册自己的号码
my_phone = register("xiaoxin")

# 添加联系人（至少提供 phone_id 或 address）
add_contact("bob", phone_id="9900778313722", address="127.0.0.1:8767", via="direct")
update_contact("bob", tags=["工作", "同事"], notes="项目合作伙伴")

add_contact("alice", phone_id="9900778313723", tags=["朋友"], notes="大学同学")

# 列出所有联系人
all_contacts = list_contacts()
for c in all_contacts:
    print(f"{c['alias']}: {c['phone_id']} | 标签: {c.get('tags', [])}")

# 按标签过滤
work_contacts = list_contacts(filter_tags=["工作"])

# 搜索
results = search_contacts("大学")  # 搜索 notes 字段

# 更新联系人状态
update_contact("bob", status="away")

# 删除联系人
remove_contact("old_friend")
```

### 数据结构

从 `list_contacts()` 返回的联系人字典包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `alias` | str | 唯一标识（主键） |
| `phone_id` | str | 13 位号码 |
| `node_id` | str | ClawMesh 节点 ID（可选） |
| `address` | str | 网络地址（如 "127.0.0.1:8766"） |
| `status` | str | 状态: "online", "away", "offline" |
| `tags` | list[str] | 标签列表（自定义） |
| `notes` | str | 备注文本 |
| `created_at` | str | 创建时间戳 |

### 高级示例

```python
# 组合使用
friends = list_contacts(filter_tags=["朋友"])
online_friends = [f for f in friends if f['status'] == 'online']

# 批量更新
for c in list_contacts():
    if c['alias'].startswith('temp_'):
        remove_contact(c['alias'])

# 搜索多条字段
important = search_contacts("紧急", fields=["alias", "notes", "phone_id"])
```

---

## 🔒 安全特性

- 号码本地生成，随机且不可预测（13位数字，90万亿空间）
- Direct P2P 模式下，消息明文传输（生产环境建议使用 ClawMesh 加密）
- 无中心服务器存储通讯记录
- 可手动验证联系人地址

---

## 📦 发布渠道
