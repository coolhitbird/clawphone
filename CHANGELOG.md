# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-03-16 (紧急修复)

### Fixed
- **Critical Bug**: `set_adapter()` 方法错误覆盖 `DirectAdapter.on_message` 导致消息全部丢失
  - 修复条件：`if hasattr(adapter, 'on_message') and not hasattr(adapter, 'get_my_address')`
  - 现在正确区分 ClawMesh 适配器和 DirectAdapter，DirectAdapter 回调不再被覆盖
  - 消息接收恢复正常，5/5 测试用例全部通过

---

## [1.2.0] - 2026-03-15

### Added
- **通讯录管理 API**:
  - `list_contacts(filter_tags=None)` - 列出所有联系人，支持按标签过滤
  - `search_contacts(query, fields=None)` - 模糊搜索（别名、号码、备注）
  - `update_contact(alias, **kwargs)` - 更新联系人（状态、备注、标签）
  - `remove_contact(alias)` - 删除联系人
- **标签系统** - 为联系人添加自定义标签（JSON 数组存储）
- **备注字段** - `notes` 列用于保存额外信息
- **数据库迁移** - `migrate_phase2.py` 自动添加 `tags` 和 `notes` 字段
- **演示脚本** - `examples/address_book_demo.py` 展示通讯录功能
- **单元测试** - `tests/test_address_book.py`（10 个测试用例）

### Changed
- 数据库 `phones` 表新增 `tags` (TEXT, JSON) 和 `notes` (TEXT) 列
- 所有联系人操作使用原子事务，保证数据一致性

---

## [1.1.0] - 2026-03-13

### Added
- **Direct P2P 模式** - 内置 WebSocket 服务器，无需 ClawMesh 即可通信
- **适配器模式** - 支持多网络层（ClawMesh / Direct），运行时切换
- **号码簿数据库** - SQLite 本地存储，支持 alias → phone_id → address 映射
- **自动号码生成** - 13 位随机数字（1000000000000-9999999999999）
- **事件回调机制** - `on_message` 事件驱动接收
- **状态管理** - `set_status("online"/"away"/"offline")`
- **完整示例** - `examples/direct_demo.py` 和 `examples/quick_demo.py`
- **单元测试** - `tests/test_clawphone.py`, `tests/test_p2p_simple.py`

### Changed
- 升级 ClawMesh 依赖到 >= 1.0.0（Phase 1-3 完成）
- 数据库结构扩展，增加 `address` 字段用于 Direct 模式

### Fixed
- DirectAdapter 发送回调同步问题（call() 不再返回 coroutine）
- 早期版本的手動綁定 API 标准化

### Known Issues
- 无离线消息缓存（Phase 2 规划）
- 无群聊支持（Phase 2 规划）
- 无自动号码发现（Phase 2 规划）

---

## [1.0.0-beta] - 2026-03-10

### Added
- 初始发布
- 基础 ClawMesh 适配（依赖外部网络）
- register(), call(), lookup() 核心功能
