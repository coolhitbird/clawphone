# SkillHub 发布表单 - ClawPhone (v1.0.0)

**填写平台**: https://skillhub.tencent.com  
**提交时间**: 2026-03-13  
**维护者**: ClawMesh Team

---

## 基础信息

| 字段 | 内容 |
|------|------|
| **Skill ID** | `clawphone` |
| **名称** | `ClawPhone` |
| **版本** | `1.0.0` |
| **描述** | 为 OpenClaw Agent 提供类似 ICQ 的即时通讯能力——注册 13 位数字号码、呼叫、实时接收通知 |
| **分类** | Communication / Instant Messaging / Agent Collaboration |
| **作者/团队** | ClawMesh Team |
| **联系邮箱** | (可选，待补充) |
| **主页/仓库** | https://github.com/coolhitbird/clawphone |
| **许可证** | Apache-2.0 |
| **标签** | `communication` `instant-messaging` `agent-collaboration` |

---

## 依赖与要求

**必需依赖**:
- `clawmesh >= 1.0.0` (底层 P2P 网络)

**可选依赖**:
- 无

**系统要求**:
- OpenClaw 运行环境
- Python 3.10+
- (Direct P2P 模式) 可用 WebSocket 端口

---

## 能力清单 (Capabilities)

| 能力名称 | 描述 | 输入参数 | 输出参数 |
|----------|------|----------|----------|
| `register` | 注册新号码（自动生成 13 位随机数字） | `alias: string` | `phone_id: string` |
| `call` | 呼叫另一个号码，发送消息 | `target: string` (号码), `message: string` | `success: bool` |
| `lookup` | 根据号码查询别名(node_id) | `phone_id: string` | `node_id: string` |
| `set_status` | 设置在线状态 | `status: "online"/"away"/"offline"` | `ok: bool` |
| `on_message` | 消息回调（事件） | 无（回调函数） | 无 |

---

## 快速开始示例

```python
# 初始化 Skill
from skills.clawphone.adapter import ClawPhone

phone = ClawPhone()
await phone.start_direct_mode()  # 启动内置 WebSocket 服务器
my_number = phone.register("alice")
print(f"我的号码: {my_number}")

# 设置回调
phone.on_message = lambda msg: print(f"收到 {msg['from']}: {msg['content']}")

# 呼叫 Bob（需先通过 add_contact 绑定地址）
phone.call("9900778313722", "Hello Bob!")
```

---

## 安装说明

```bash
# 方式 1: SkillHub 一键安装
skillhub install clawphone

# 方式 2: 手动克隆
git clone https://github.com/coolhitbird/clawphone.git ~/.openclaw/workspace/skills/clawphone
```

---

## 风险与安全声明

| 评估项 | 说明 |
|--------|------|
| **来源** | 独立开发，ClawMesh Team |
| **版本** | 1.0.0 (初始稳定版) |
| **安全风险** | 低 - 消息通过 ClawMesh 端到端加密（或本地 Direct P2P） |
| **隐私风险** | 低 - 号码簿本地 SQLite 存储，不传云端 |
| **稳定性** | 中 - Core 功能稳定，Phase 2 规划中 |
| **已知限制** | 无离线消息缓存，不支持群聊（Phase 2 规划） |

**风险信号**: 无

---

## 附加信息

- **测试报告**: `PUBLISH_REPORT.md` (包含 `test_p2p_simple.py` 结果)
- **发布包**: `clawphone-v1.0.0.zip`
- **文档**: `README.md`, `SKILL.md`
- **示例**: `examples/quick_demo.py`, `examples/direct_demo.py`

---

## 确认

- [x] 我已阅读并同意 SkillHub 发布条款
- [x] 本 Skill 不包含恶意代码或隐私侵犯行为
- [x] 我已测试核心功能，运行稳定
- [x] 提供了清晰的安装和使用文档
- [x] 标注了所有依赖项

**提交日期**: 2026-03-13  
**联系方式**: (待补充)
