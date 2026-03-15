# ClawPhone Skill - ClawHub 发布摘要

**Skill ID**: clawphone  
**版本**: 1.1.0  
**发布日期**: 2026-03-13  
**维护者**: ClawMesh Team  
**仓库**: https://github.com/coolhitbird/clawphone  
**Release**: https://github.com/coolhitbird/clawphone/releases/tag/v1.1.0

---

## 📦 发布包
- `clawphone-v1.1.0.zip` (75KB)
- SHA256: (待计算)
- 包含：SOURCE + DOCS + EXAMPLES + TESTS

---

## 🎯 核心能力
- `register` - 注册 13 位号码
- `call` - 即时呼叫
- `lookup` - 号码查询
- `add_contact` - 手动绑定联系人
- `set_status` - 设置状态
- `on_message` - 消息回调
- `start_direct_mode` - 启动 Direct P2P 服务器

---

## 🔗 配置

ClawHub 自动读取 `clawhub.yaml`。核心字段：

```yaml
name: clawphone
version: 1.1.0
dependencies:
  - name: clawmesh
    version: ">=1.0.0"
    required: true
```

---

## 📝 下一步

1. 在 ClawHub 控制台上传 `clawphone-v1.1.0.zip`
2. 填写 metadata（可从 `clawhub.yaml` 复制）
3. 提交审核（通常自动）
4. 用户即可 `clawhub install clawphone`

---

**注意**: ClawHub 为公共 registry，不强制审核，建议保留 `risk_assessment` 字段。
