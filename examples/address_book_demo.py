#!/usr/bin/env python3
"""
ClawPhone 通讯录管理演示

展示：
1. 注册自己的号码
2. 添加联系人（带标签）
3. 列出所有联系人
4. 搜索联系人
5. 更新联系人信息
6. 删除联系人
"""

import sys
from pathlib import Path

# 添加 skill 根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapter.clawphone import (
    register,
    list_contacts,
    search_contacts,
    add_contact,
    remove_contact,
    update_contact,
    on_message,
    call,
)


def print_separator(title=""):
    if title:
        print(f"\n{'='*50}")
        print(f"  {title}")
        print('='*50)
    else:
        print('='*50)


def demo_address_book():
    print_separator("ClawPhone 通讯录管理演示")

    # 1. 注册自己的号码（如果尚未注册）
    print("\n1. 注册自己的号码...")
    my_phone = register("xiaoxin_demo")
    print(f"   我的号码: {my_phone}")

    # 2. 添加一些示例联系人
    print("\n2. 添加联系人...")

    # 添加 Bob（工作伙伴）
    add_contact(
        alias="bob",
        phone_id="9900778313722",
        address="127.0.0.1:8767",
        via="direct"
    )
    # 手动设置 tags（通过 update）
    update_contact("bob", tags=["工作", "同事"])
    print("   [OK] 添加了 bob (工作伙伴)")

    # 添加 Alice（朋友）
    add_contact(
        alias="alice",
        phone_id="9900778313723",
        address="127.0.0.1:8768",
        via="direct"
    )
    update_contact("alice", tags=["朋友"], notes="大学同学")
    print("   [OK] 添加了 alice (朋友)")

    # 添加 Charlie（家人，不提供地址，仅保存号码）
    add_contact(alias="charlie", phone_id="9900778313724")
    update_contact("charlie", tags=["家人"], notes="老爸")
    print("   [OK] 添加了 charlie (家人)")

    # 3. 列出所有联系人
    print_separator("3. 所有联系人")
    contacts = list_contacts()
    print(f"   总计: {len(contacts)} 个")
    for c in contacts:
        tags = ", ".join(c.get('tags', [])) or "无标签"
        notes = c.get('notes', "")[:20]
        print(f"   - {c['alias']:10} | {c['phone_id']} | 标签: [{tags}] | 备注: {notes}")

    # 4. 按标签过滤
    print_separator("4. 过滤：只显示 '工作' 标签")
    work_contacts = list_contacts(filter_tags=["工作"])
    for c in work_contacts:
        print(f"   - {c['alias']}: {c['phone_id']}")
    print(f"   找到 {len(work_contacts)} 个")

    # 5. 搜索联系人
    print_separator("5. 搜索 '大学' 关键字")
    results = search_contacts("大学")
    for c in results:
        print(f"   - {c['alias']}: {c.get('notes', '')}")
    print(f"   找到 {len(results)} 个")

    # 6. 更新联系人
    print_separator("6. 更新 bob 的状态为 'away' 并添加备注")
    update_contact("bob", status="away", notes="最近在休假")
    updated = list_contacts()
    bob = [c for c in updated if c['alias'] == 'bob'][0]
    print(f"   bob 新状态: {bob['status']}")
    print(f"   bob 新备注: {bob.get('notes', '')}")

    # 7. 删除联系人（清理）
    print_separator("7. 删除 charlie（清理演示数据）")
    removed = remove_contact("charlie")
    print(f"   删除结果: {'成功' if removed else '失败'}")
    remaining = list_contacts()
    print(f"   剩余联系人: {len(remaining)} 个")

    # 8. 最终联系人列表
    print_separator("8. 最终联系人列表")
    final_contacts = list_contacts()
    for c in final_contacts:
        tags = ", ".join(c.get('tags', []))
        print(f"   {c['alias']:10} | {c['phone_id']} | {c['status']:6} | [{tags}]")

    print_separator()
    print("[OK] 演示完成！")
    print("\n你可以将这些代码集成到你的 Agent 中：")
    print("  from skills.clawphone.adapter.clawphone import list_contacts, add_contact, ...")
    print("\n详细 API 参考 README.md")


if __name__ == "__main__":
    demo_address_book()