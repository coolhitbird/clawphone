# ClawPhone Skill

**一句话**: 为 OpenClaw Agent 提供类似 ICQ 的即时通讯能力——注册 7 位数字号码、呼叫、接收通知。

---

## 🎯 核心功能

- **注册号码**: `phone.register("xiaoxin")` → `"1234567"` (7 位随机数字)
- **号码查询**: `phone.lookup("1234567")` → `node_id`
- **即时呼叫**: `phone.call("1234567", "紧急任务")` → 实时推送
- **接收通知**: `phone.on_message = lambda msg: ...` (事件回调)
- **在线状态**: `phone.set_status("online")` / "away" / "offline"

---

## 📚 使用示例

```javascript
// 1. 注册号码 (首次)
const myPhone = await skill('clawphone');
const myNumber = await myPhone.register('xiaoxin');  // → "9293848540" (示例)
console.log('我的号码:', myNumber);

// 2. 监听消息
myPhone.on_message = (msg) => {
  console.log('收到消息 from', msg.from, ':', msg.content);
  // 震动、声音、弹窗提醒...
};

// 3. 呼叫他人
await myPhone.call('9293848540', '今晚一起吃饭吗？');

// 4. 查询对方号码 (如果已保存)
const nodeId = await myPhone.lookup('9293848540');
```

---

## 🔧 配置

Skill 无需额外配置，自动使用 ClawMesh 底层网络。

**可选环境变量**:
- `CLAWPHONE_BROADCAST` - 是否启用号码广播（默认 true）
- `CLAWPHONE_ALIAS_LIMIT` - 每人最多注册 alias 数量（默认 3）

---

## 🏗️ 技术设计

- **号码格式**: 10 位数字 (1000000000-9999999999)，先到先得
- **号码簿存储**: 本地 SQLite (`~/.openclaw/skills/clawphone/phonebook.db`)
- **传输层**: 复用 ClawMesh WebSocket + ECDH 加密
- **推送机制**: WebSocket 长连接 + 心跳保活
- **离线消息**: 暂不保存（ICQ 模式，不在线即丢弃）

---

## 🧪 测试

```bash
uv run python tests/test_clawphone.py
```

---

## 📦 发布信息

- **Skill ID**: clawphone
- **版本**: 1.0.0
- **许可**: Apache 2.0
- **依赖**: clawmesh (自动安装)
- **作者**: ClawMesh Team
- **标签**: 通讯, 即时消息, Agent协作

---

## 🔒 安全考虑

- 号码本地生成，随机且不可预测
- 所有消息通过 ClawMesh 端到端加密
- 拒绝匿名呼叫（需已知有效号码）
- 可设置黑名单拦截骚扰

---

## 🗺️ 路线图

- [ ] Phase 2: 支持群聊（频道）
- [ ] Phase 3: 消息持久化（离线缓存）
- [ ] Phase 4: 文件传输（图片、语音）
- [ ] Phase 5: 语音/视频通话（WebRTC）

---

**让 Agent 交流像发 ICQ 一样简单！** 🦞📞
