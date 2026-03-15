#!/usr/bin/env python3
"""ClawPhone Phase 2: 通讯录管理单元测试"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from adapter.clawphone import (
    register,
    list_contacts,
    search_contacts,
    add_contact,
    remove_contact,
    update_contact,
    _phone,
)
import sqlite3

DB_PATH = Path.home() / ".openclaw" / "skills" / "clawphone" / "phonebook.db"


def clear_db():
    """清空测试数据库（保留表结构）"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM phones")
    conn.commit()
    conn.close()


def test_list_contacts_empty():
    print("测试: list_contacts 空数据库...")
    clear_db()
    contacts = list_contacts()
    assert isinstance(contacts, list), "应返回 list"
    assert len(contacts) == 0, "应为空"
    print("  [OK] 空数据库返回 []")


def test_add_and_list():
    print("测试: add_contact 和 list_contacts...")
    clear_db()
    # 添加两个联系人
    ok1 = add_contact("alice", phone_id="9900778313721", address="127.0.0.1:8766", via="direct")
    ok2 = add_contact("bob", phone_id="9900778313722", address="127.0.0.1:8767", via="direct")
    assert ok1 and ok2, "添加应成功"

    contacts = list_contacts()
    assert len(contacts) == 2, f"应有 2 个联系人，实际 {len(contacts)}"
    aliases = {c['alias'] for c in contacts}
    assert 'alice' in aliases and 'bob' in aliases, "联系人应在列表中"
    print("  [OK] 添加和列表正常")


def test_update_contact():
    print("测试: update_contact...")
    clear_db()
    add_contact("charlie", phone_id="9900778313723")

    # 更新状态和备注
    ok = update_contact("charlie", status="away", notes="测试备注")
    assert ok, "更新应成功"

    contacts = list_contacts()
    charlie = [c for c in contacts if c['alias'] == 'charlie'][0]
    assert charlie['status'] == 'away', "状态应更新"
    assert charlie.get('notes') == "测试备注", "备注应更新"
    print("  [OK] 更新联系人正常")


def test_tags_handling():
    print("测试: tags 字段...")
    clear_db()
    add_contact("dave", phone_id="9900778313724")
    # 设置 tags (list)
    ok = update_contact("dave", tags=["工作", "紧急"])
    assert ok, "设置 tags 应成功"

    contacts = list_contacts()
    dave = [c for c in contacts if c['alias'] == 'dave'][0]
    tags = dave.get('tags', [])
    assert isinstance(tags, list), "tags 应为 list"
    assert "工作" in tags and "紧急" in tags, "tags 内容应正确"
    print("  [OK] tags 处理正常")


def test_filter_by_tags():
    print("测试: list_contacts 按标签过滤...")
    clear_db()
    add_contact("eve", phone_id="9900778313725")
    update_contact("eve", tags=["朋友"])
    add_contact("frank", phone_id="9900778313726")
    update_contact("frank", tags=["工作"])

    work_only = list_contacts(filter_tags=["工作"])
    assert len(work_only) == 1, "应只找到 1 个工作标签"
    assert work_only[0]['alias'] == 'frank', "应为 frank"
    print("  [OK] 单标签过滤正常")

    multi = list_contacts(filter_tags=["工作", "紧急"])  # 无匹配
    assert len(multi) == 0, "应无匹配"

    # 测试 AND 逻辑
    add_contact("grace", phone_id="9900778313727")
    update_contact("grace", tags=["工作", "紧急"])
    multi2 = list_contacts(filter_tags=["工作", "紧急"])
    assert len(multi2) == 1 and multi2[0]['alias'] == 'grace', "应匹配同时有工作和紧急标签"
    print("  [OK] 多标签 AND 过滤正常")


def test_search_contacts():
    print("测试: search_contacts...")
    clear_db()
    add_contact("henry", phone_id="9900778313728")
    update_contact("henry", notes="这是一个测试笔记", status="online")
    add_contact("ivy", phone_id="9900778313729")
    update_contact("ivy", notes="另一个测试", status="offline")

    # 搜索 notes
    results = search_contacts("测试")
    assert len(results) >= 1, "应找到至少 1 个"
    aliases = {r['alias'] for r in results}
    assert 'henry' in aliases, "应找到 henry"
    print("  [OK] 搜索 notes 正常")

    # 搜索 alias
    results2 = search_contacts("hen")
    assert any(r['alias'] == 'henry' for r in results2), "按 alias 应找到 henry"
    print("  [OK] 搜索 alias 正常")

    # 搜索 phone_id
    results3 = search_contacts("9900778313728")
    assert any(r['phone_id'] == '9900778313728' for r in results3), "按 phone_id 应找到"
    print("  [OK] 搜索 phone_id 正常")


def test_remove_contact():
    print("测试: remove_contact...")
    clear_db()
    add_contact("jack", phone_id="9900778313730")

    removed = remove_contact("jack")
    assert removed, "删除应成功"

    contacts = list_contacts()
    assert not any(c['alias'] == 'jack' for c in contacts), "jack 不应再存在"
    print("  [OK] 删除联系人正常")

    # 删除不存在的
    removed2 = remove_contact("nonexistent")
    assert not removed2, "删除不存在应返回 False"
    print("  [OK] 删除不存在的返回 False 正常")


def test_update_nonexistent():
    print("测试: update_contact 对不存在联系人...")
    clear_db()
    ok = update_contact("nobody", status="away")
    assert not ok, "更新不存在应失败"
    print("  [OK] 更新不存在的返回 False 正常")


if __name__ == "__main__":
    print("=== ClawPhone 通讯录测试 ===\n")
    try:
        test_list_contacts_empty()
        test_add_and_list()
        test_update_contact()
        test_tags_handling()
        test_filter_by_tags()
        test_search_contacts()
        test_remove_contact()
        test_update_nonexistent()
        print("\n[OK] 所有测试通过！")
    except AssertionError as e:
        print(f"\n[FAIL] 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] 意外错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)