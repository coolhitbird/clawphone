"""
ClawPhone Skill - 让 Agent 拥有"手机号码"
类似 ICQ 的即时通讯系统
"""

from .clawphone import (
    _phone,
    register,
    lookup,
    call,
    set_status,
    on_message,
    set_network,
    skill_main
)

__all__ = [
    "register",
    "lookup",
    "call",
    "set_status",
    "on_message",
    "skill_main"
]
