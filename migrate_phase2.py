#!/usr/bin/env python3
"""
ClawPhone Phase 2: 通讯录管理增强
- 数据库迁移：添加 tags, notes 字段
- 新增 API: list_contacts, search_contacts, remove_contact, update_contact
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path.home() / ".openclaw" / "skills" / "clawphone" / "phonebook.db"


def migrate_db():
    """数据库迁移：添加缺失的列"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. 检查现有列
    cur.execute("PRAGMA table_info(phones)")
    existing_cols = {row[1] for row in cur.fetchall()}

    # 2. 添加 tags 列（如果缺失）
    if "tags" not in existing_cols:
        cur.execute("ALTER TABLE phones ADD COLUMN tags TEXT")
        print("[MIGRATION] Added column: tags")
        # 为现有数据初始化 tags 为空数组
        cur.execute("UPDATE phones SET tags = '[]' WHERE tags IS NULL")
        print("[MIGRATION] Initialized tags to '[]' for existing rows")

    # 3. 添加 notes 列（如果缺失）
    if "notes" not in existing_cols:
        cur.execute("ALTER TABLE phones ADD COLUMN notes TEXT")
        print("[MIGRATION] Added column: notes")

    conn.commit()
    conn.close()
    print("[MIGRATION] Database migration completed.")


# 执行迁移
if __name__ == "__main__":
    migrate_db()