# ClawPhone v1.2.0 Release Notes

** release date**: 2026-03-15  
**Branch**: main  
**Git tag**: v1.2.0

---

## ✨ 新增功能

### 📋 通讯录管理 (Phase 2)

完整的联系人管理 API：

- **`list_contacts(filter_tags=None)`** - 列出所有联系人，支持按标签 AND 过滤
- **`search_contacts(query, fields=None)`** - 模糊搜索（alias, phone_id, notes）
- **`add_contact(alias, phone_id, address, via)`** - 添加联系人
- **`update_contact(alias, **kwargs)`** - 更新联系人（status, notes, tags, address）
- **`remove_contact(alias)`** - 删除联系人

### 🏷️ 标签系统

- 为联系人添加自定义标签（JSON 数组存储）
- 支持多标签过滤（AND 逻辑）
- 示例: `tags=["工作", "紧急"]`

### 📝 备注字段

- 新增 `notes` 列，用于保存额外信息
- 支持搜索和展示

### 🧪 测试覆盖

新增 `tests/test_address_book.py`，10 个测试用例：
- 列表、添加、更新、删除
- 标签处理、过滤搜索
- 边界情况

---

## 🔧 技术改动

### 数据库迁移

- 新增 `tags` (TEXT, JSON) 和 `notes` (TEXT) 列
- 自动迁移脚本: `migrate_phase2.py`
- 向后兼容：旧数据库会自动添加缺失列

### API 变更

**无破坏性变更** - 所有新增功能均为可选使用

---

## 📚 文档更新

- **README.md**: 新增"📋 通讯录管理 (Phase 2)"完整章节
- **CHANGELOG.md**: v1.2.0 条目
- **SKILL.md**: 更新核心功能列表和路线图
- **skill.yaml**: 版本 1.2.0，新增 4 个 capabilities

---

## 🧪 测试结果

```bash
$ uv run python examples/address_book_demo.py
[OK] 演示完成（含增删改查、过滤、搜索）

$ uv run python tests/test_address_book.py
[OK] 所有测试通过！ (10/10)
```

---

## 🔄 升级指南

### 从 v1.1.0 升级

1. **更新代码**:
   ```bash
   cd skills/clawphone
   git pull origin main  # 或替换为新zip
   ```

2. **迁移数据库** (首次运行自动执行):
   ```python
   from adapter.clawphone import register  # 会自动检查并迁移
   phone_id = register("myalias")
   ```

3. **使用新 API**:
   ```python
   from adapter.clawphone import list_contacts, add_contact, update_contact

   # 列出所有联系人
   contacts = list_contacts()

   # 添加带标签的联系人
   add_contact("bob", phone_id="9900778313722")
   update_contact("bob", tags=["工作"], notes="合作伙伴")
   ```

---

## 🐛 已修复

- 无重大 bug 修复（v1.1.0 稳定性良好）

---

## 📦 文件清单

```
clawphone-v1.2.0-clean.zip
├── README.md
├── CHANGELOG.md
├── SKILL.md
├── skill.yaml
├── LICENSE
├── adapter/
│   ├── clawphone.py     (更新: +200 行)
│   └── direct.py
├── core/
│   ├── phone.py
│   ├── database.py
│   └── models.py
├── examples/
│   ├── quick_demo.py
│   ├── direct_demo.py
│   └── address_book_demo.py  (NEW)
├── tests/
│   ├── test_clawphone.py
│   ├── test_p2p_simple.py
│   └── test_address_book.py  (NEW)
└── migrate_phase2.py      (NEW)
```

---

## 🎯 下一步

- **v1.3.0 规划**: Phase 3 - 群组聊天（房间、频道）
- **v2.0.0 规划**: 消息持久化 + 端到端加密升级

---

**Full Changelog**: https://github.com/coolhitbird/clawphone/compare/v1.1.0...v1.2.0