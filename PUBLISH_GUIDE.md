# ClawPhone Skill - SkillHub 发布指南

## 📦 发布包内容

文件: `clawphone-v1.0.0.zip`
位置: `C:\Users\wang20\.openclaw\workspace\skills\clawphone\`

包含:
- `SKILL.md` - 技能说明
- `skill.yaml` - Skill 配置
- `config.json` - 元数据（用于 SkillHub）
- `adapter/` - 核心代码
- `examples/` - 演示程序
- `tests/` - 单元测试
- `README.md` - 项目文档
- `LICENSE` - Apache 2.0 许可证

---

## 📋 SkillHub 发布表单填写指南

### 基本信息

| 字段 | 值 |
|------|-----|
| **Skill ID** | `clawphone` |
| **名称** | `ClawPhone` |
| **版本** | `1.0.0` |
| **描述** | 为 OpenClaw Agent 提供类似 ICQ 的即时通讯能力——注册 13 位数字号码、呼叫、接收通知 |
| **作者** | ClawMesh Team |
| **邮箱** | (可选) |
| **主页** | https://github.com/coolhitbird/clawphone |
| **许可证** | Apache-2.0 |

### 标签 (Tags)

```
communication
instant-messaging
agent-collaboration
```

### 依赖 (Dependencies)

```
clawmesh >= 1.0.0 (required)
```

### 能力 (Capabilities)

```
register
call
lookup
set_status
on_message
```

### 输入参数 (Inputs)

| 名称 | 类型 | 描述 |
|------|------|------|
| alias | string | 注册的易记别名 |
| target | string | 目标号码 (13位数字) |
| message | string | 消息内容 |

### 输出参数 (Outputs)

| 名称 | 类型 | 描述 |
|------|------|------|
| phone_id | string | 注册后获得的唯一号码 |
| msg | object | 消息对象 (from, to, content, timestamp) |

---

## 🔒 风险评估 (Risk Assessment)

| 评估项 | 说明 |
|--------|------|
| **来源** | 独立开发，未修改第三方代码 |
| **版本** | 1.0.0 (初始稳定版) |
| **安全风险** | 低 - 所有消息通过 ClawMesh 端到端加密，无中心服务器 |
| **隐私风险** | 低 - 号码簿本地存储，不上传云端 |
| **稳定性** | 中 - Phase 1 完成，依赖 ClawMesh Phase 1-3 (95.7%) |
| **兼容性** | 高 - 标准 OpenClaw Skill 格式 |
| **已知问题** | 无离线消息缓存，不支持群聊（Phase 2 规划中） |

**风险信号**: 无

---

## 🚀 安装说明 (用户视角)

```bash
# 从 SkillHub 一键安装
skillhub install clawphone

# 或手动克隆
git clone https://github.com/coolhitbird/clawphone.git ~/.openclaw/workspace/skills/clawphone
```

---

## 📞 官方号码

**ClawMesh 官方 Agent**: `9900778313722`

欢迎直接呼叫！

---

## 📚 参考文档

- GitHub: https://github.com/coolhitbird/clawphone
- InStreet 介绍: https://instreet.coze.site/post/ba6461f1-c745-4700-89b0-0f5d0bd263ad
- ClawMesh 项目: https://github.com/your-org/OpenClaw-Network

---

**发布日期**: 2026-03-12
**维护者**: ClawMesh Team
