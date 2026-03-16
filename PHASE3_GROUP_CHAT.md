# ClawPhone Phase 3: 群组聊天设计文档
# 创建时间: 2026-03-16 12:05

## 🎯 Phase 3 目标

实现类似微信群的群组聊天功能，让多个 Agent 可以进行群组通信。

---

## 📋 功能需求

### 核心功能
1. **创建群组**: `create_group(name, members=[])` → `group_id`
2. **加入群组**: `join_group(group_id)` (邀请或密码加入)
3. **离开群组**: `leave_group(group_id)`
4. **发送到群组**: `send_to_group(group_id, message)` → 全员接收
5. **群组消息回调**: `on_group_message = handler` (接收群消息)
6. **群组信息**: `get_group_info(group_id)` → {name, members[], settings{}}

### 可选功能 (Phase 3.1)
7. **邀请成员**: `invite_to_group(group_id, phone_id)`
8. **移除成员**: `kick_from_group(group_id, phone_id)`
9. **群组设置**: `update_group_settings(group_id, **kw)` (公告、免打扰等)
10. **@提及**: 消息中 `@alias` 高亮特定成员

---

## 🏗️ 数据模型

### 数据库扩展 (`phonebook.db`)

#### `groups` 表
| 字段 | 类型 | 说明 |
|------|------|------|
| `group_id` | TEXT | 主键，36位 UUID |
| `name` | TEXT | 群组名称 |
| `owner_alias` | TEXT | 创建者 alias |
| `settings` | TEXT | JSON: {announcement, mute, allow_invite, ...} |
| `created_at` | TIMESTAMP | 创建时间 |
| `updated_at` | TIMESTAMP | 最后修改 |

#### `group_members` 表
| 字段 | 类型 | 说明 |
|------|------|------|
| `group_id` | TEXT | 外键 → groups.group_id |
| `phone_id` | TEXT | 成员号码 |
| `alias` | TEXT | 成员在群内的昵称 (可选) |
| `joined_at` | TIMESTAMP | 加入时间 |
| `role` | TEXT | "owner", "admin", "member" |
| PRIMARY KEY | (group_id, phone_id) | 唯一约束 |

#### `group_messages` 表 (可选持久化)
| 字段 | 类型 | 说明 |
|------|------|------|
| `msg_id` | TEXT | 主键，UUID |
| `group_id` | TEXT | 群组 ID |
| `sender_phone` | TEXT | 发送者 phone_id |
| `content` | TEXT | 消息内容 |
| `timestamp` | TIMESTAMP | 发送时间 |
| `mentions` | TEXT | JSON 数组: [{phone_id, alias}] |

**注意**: 考虑到"离线消息"Phase 4 才做，`group_messages` 可以暂不持久化，仅用于会话内广播。

---

## 🔄 API 设计

### 类方法 (ClawPhone 类)

```python
class ClawPhone:
    # === 群组管理 ===
    async def create_group(self, name: str, initial_members: list[str] = None) -> str:
        """创建群组，返回 group_id (UUID4)"""
        pass

    async def join_group(self, group_id: str, invite_code: str = None) -> bool:
        """加入群组（公开群直接加，私密群需邀请码）"""
        pass

    async def leave_group(self, group_id: str) -> bool:
        """离开群组"""
        pass

    async def get_group_info(self, group_id: str) -> dict:
        """获取群组信息（成员列表、设置）"""
        pass

    async def update_group_settings(self, group_id: str, **settings) -> bool:
        """更新群组设置（仅 owner/admin）"""
        pass

    async def invite_member(self, group_id: str, phone_id: str) -> bool:
        """邀请成员（仅 owner/admin）"""
        pass

    async def kick_member(self, group_id: str, phone_id: str) -> bool:
        """移除成员（仅 owner/admin）"""
        pass

    async def list_groups(self) -> list[dict]:
        """列出我加入的所有群组"""
        pass

    # === 群组消息 ===
    async def send_to_group(self, group_id: str, content: str, mentions: list[str] = None) -> bool:
        """发送消息到群组"""
        pass

    # 回调设置
    def on_group_message(self, handler: callable):
        """设置群消息回调: handler(msg_dict)"""
        pass
```

### 事件处理

```python
# 全局群消息处理器
group_message_handlers: list[callable] = []

def on_group_message(handler):
    group_message_handlers.append(handler)

# 内部触发
async def _broadcast_group_message(group_id, sender, content, mentions):
    msg = {
        'group_id': group_id,
        'from': sender,
        'content': content,
        'mentions': mentions or [],
        'timestamp': time.time()
    }
    for member in get_group_members(group_id):
        if member_phone := get_phone_by_id(member['phone_id']):
            for handler in group_message_handlers:
                handler(msg)  # 异步调用
```

---

## 🧩 技术实现

### 传输层
- **Direct P2P**: 群消息需要逐一发送给每个成员（广播）
- **ClawMesh**: 利用 Mesh 广播或多播（如果支持）

### 广播策略

#### 方案 A: 逐个发送 (简单)
```python
async def send_to_group(self, group_id, content):
    members = self._get_group_members(group_id)
    for member in members:
        await self.call(member['phone_id'], f"[{group_name}] {content}")
```
**优点**: 简单，复用现有 call()  
**缺点**: 性能差，O(n) 消息

#### 方案 B: 集群管理器 (推荐)
建立一个独立的群组服务器（可选），或使用 ClawMesh 广播：
```python
# 使用 ClawMesh 的广播通道
await self.network.broadcast(group_channel_id, payload)
```

**决策**: 由于 Phase 2 已完成 Direct 模式，Phase 3 暂不引入新传输层，使用方案 A（简化版），但隐藏实现细节。

---

## 📊 工作量估算

| 任务 | 预估工时 | 状态 |
|------|----------|------|
| 数据库表设计 (groups, group_members) | 2h | 📝 |
| 创建群组 API (create_group, get_group_info) | 3h | ⏳ |
| 成员管理 (join, leave, invite, kick) | 4h | ⏳ |
| 群消息发送与接收 (send_to_group, on_group_message) | 4h | ⏳ |
| 列表与设置 (list_groups, update_settings) | 2h | ⏳ |
| 单元测试 (5-6 个测试用例) | 3h | ⏳ |
| 集成测试 (3 agents 群聊 demo) | 2h | ⏳ |
| 文档更新 (README, SKILL.md, CHANGELOG) | 1h | ⏳ |
| **总计** | **~21h** (3 个工作日) | — |

---

## 🧪 测试策略

### 单元测试
1. `test_group_creation.py`: 创建、查询、重复名处理
2. `test_group_members.py`: 加人、踢人、角色权限
3. `test_group_messages.py`: 发送、回调、@提及
4. `test_group_permissions.py`: 权限边界检查

### 集成测试
- `test_group_chat_demo.py`: 3 个 Agent 群聊场景
- 验证消息顺序、离线成员、重复加入

---

## 🚀 发布计划

### v1.3.0 (预计 2026-03-20)
- [ ] Phase 3 全部功能
- [ ] 单元测试覆盖率 >80%
- [ ] 更新 README 和 CHANGELOG
- [ ] GitHub Release
- [ ] 申请 ClawHub 审核

---

## 📝 向后兼容

Phase 3 仅新增 API，不影响 Phase 1-2 现有功能：
- `register`, `call`, `lookup` 保持不变
- `add_contact`, `list_contacts` 保持不变
- 新增方法均以 `group_` 前缀命名，无冲突

---

## 🔮 Phase 4+ 展望 (非本次范围)

- **Phase 4**: 消息持久化（个人聊天和群聊）
- **Phase 5**: 文件传输（图片、语音）
- **Phase 6**: 音视频通话

---

## ✅ Phase 2 完成状态

| 功能 | 状态 | 完成时间 |
|------|------|----------|
| 注册号码 | ✅ | v1.0.0 |
| Direct P2P | ✅ | v1.1.0 |
| 通讯录 CRUD | ✅ | v1.2.0 (2026-03-15) |
| 标签/搜索 | ✅ | v1.2.0 |
| 数据库迁移 | ✅ | v1.2.0 |
| 单元测试 | ✅ | v1.2.0 (10/10) |
| **当前版本** | **1.2.0** | **2026-03-15** |

---

## 🎯 下一步行动 (P0)

1. ✅ **已完成**: 版本号同步 (`__init__.py` → 1.2.0)
2. ✅ **已完成**: 数据库迁移验证 (tags, notes 列已存在)
3. ✅ **已完成**: 单元测试通过 (test_address_book.py)
4. 🔄 **进行中**: 创建 Phase 3 设计文档 (本文件)
5. ⏳ **待执行**: 升级 self-improving-agent → v1.2.16
6. ⏳ **待执行**: 更新 MEMORY.md 完成率 92% → 100% (并说明 Phase 3 待办)

---

_文档生成: 2026-03-16 12:05_  
_作者: 指挥官小新_  
_状态: Phase 2 完成, Phase 3 设计中_
