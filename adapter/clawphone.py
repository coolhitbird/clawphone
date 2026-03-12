"""
ClawPhone Skill - 让 Agent 拥有"号码"，实现即时通讯
类似 ICQ/AOL 的简洁通知系统
"""

import sqlite3
import random
import json
import time
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import logging

logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = Path.home() / ".openclaw" / "skills" / "clawphone" / "phonebook.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _init_db():
    """初始化 SQLite 数据库"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS phones (
            alias TEXT PRIMARY KEY,
            phone_id TEXT UNIQUE,
            node_id TEXT,
            public_key TEXT,
            status TEXT DEFAULT 'offline',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS call_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_phone TEXT,
            to_phone TEXT,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


class ClawPhone:
    """ClawPhone 核心类"""

    def __init__(self):
        self._on_message: Optional[Callable[[Dict[str, Any]], None]] = None
        self._my_phone_id: Optional[str] = None
        self._my_node_id: Optional[str] = None
        self._status = "offline"
        self._network = None  # 将在 connect 中注入
        _init_db()

    def set_network(self, network):
        """注入网络适配器（ClawMesh）"""
        self._network = network
        # 自动恢复已注册号码
        self._restore_registration()

    def register(self, alias: str) -> str:
        """
        注册一个 13 位纯数字号码
        格式: 随机 13 位数字 (1000000000000 - 9999999999999)
        例: register("xiaoxin") → "9900778313722"
        """
        if not alias or not alias.replace('_', '').isalnum():
            raise ValueError("alias 必须为字母数字组合（可含下划线）")

        # 检查是否已注册（同一 alias 返回已有号码）
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT phone_id FROM phones WHERE alias = ?", (alias,))
        row = cur.fetchone()
        if row:
            conn.close()
            return row[0]  # 已存在，返回已有号码

        # 生成唯一 13 位数字号码
        for _ in range(100):  # 尝试100次避免冲突
            phone_id = str(random.randint(1000000000000, 9999999999999))
            cur.execute("SELECT 1 FROM phones WHERE phone_id = ?", (phone_id,))
            if not cur.fetchone():
                break
        else:
            raise RuntimeError("无法生成唯一号码，请重试")

        # 保存注册记录
        cur.execute(
            "INSERT INTO phones (alias, phone_id, node_id, status) VALUES (?, ?, ?, ?)",
            (alias, phone_id, self._my_node_id, self._status)
        )
        conn.commit()
        conn.close()

        self._my_phone_id = phone_id
        logger.info(f"注册成功: {phone_id}")
        return phone_id

    def lookup(self, target: str) -> Optional[str]:
        """
        查询目标号码对应的 node_id
        target 可以是:
        - 13 位数字号码: "9900778313722"
        - alias (注册时的别名): "xiaoxin"
        """
        target = target.strip()

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # 先尝试 phone_id (13位数字)
        if target.isdigit() and len(target) == 13:
            cur.execute("SELECT node_id FROM phones WHERE phone_id = ?", (target,))
            row = cur.fetchone()
            if row and row[0]:
                conn.close()
                return row[0]

        # 尝试 alias
        cur.execute("SELECT node_id FROM phones WHERE alias = ?", (target,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    def call(self, target: str, message: str) -> bool:
        """
        呼叫对方并发送消息
        返回: 是否发送成功
        """
        if not self._network:
            logger.warning("网络未就绪，请确保 ClawMesh 已连接并调用 set_network()")
            return False

        node_id = self.lookup(target)
        if not node_id:
            logger.warning(f"找不到目标: {target}")
            return False

        # 构造消息
        msg = {
            "type": "call",
            "from": self._my_phone_id,
            "to": target,
            "content": message,
            "timestamp": time.time()
        }

        try:
            self._network.send(node_id, json.dumps(msg))
            # 记录日志
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO call_log (from_phone, to_phone, message) VALUES (?, ?, ?)",
                (self._my_phone_id, target, message)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"发送失败: {e}")
            return False

    def set_status(self, status: str):
        """设置在线状态: online/away/offline"""
        if status not in ("online", "away", "offline"):
            raise ValueError("状态必须是 online/away/offline")
        self._status = status
        # TODO: 广播状态更新给好友

    @property
    def on_message(self) -> Optional[Callable]:
        return self._on_message

    @on_message.setter
    def on_message(self, callback: Callable[[Dict[str, Any]], None]):
        """设置消息接收回调"""
        self._on_message = callback

    def _handle_incoming(self, raw_message: str):
        """内部：处理收到的消息"""
        try:
            msg = json.loads(raw_message)
            if msg.get("type") == "call" and self._on_message:
                self._on_message(msg)
        except Exception as e:
            logger.error(f"消息解析失败: {e}")

    def _restore_registration(self):
        """自动恢复上次注册的号码（如果存在）"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT phone_id FROM phones WHERE node_id = ? ORDER BY created_at DESC LIMIT 1", (self._my_node_id,))
        row = cur.fetchone()
        if row:
            self._my_phone_id = row[0]
            logger.info(f"恢复号码: {self._my_phone_id}")
        conn.close()

    def get_my_phone(self) -> Optional[str]:
        """获取当前注册的号码"""
        return self._my_phone_id


# 全局实例
_phone = ClawPhone()


# Skill API 入口
def skill_main(**kwargs):
    """
    Skill 主入口，OpenClaw 会调用此函数
    返回: { "phone_id": str, "capabilities": [...] }
    """
    return {
        "phone_id": _phone.get_my_phone(),
        "capabilities": ["register", "call", "lookup", "set_status", "on_message"]
    }


def register(alias: str) -> str:
    """注册号码"""
    return _phone.register(alias)


def lookup(target: str) -> Optional[str]:
    """查询 node_id"""
    return _phone.lookup(target)


def call(target: str, message: str) -> bool:
    """呼叫"""
    return _phone.call(target, message)


def set_status(status: str):
    """设置状态"""
    _phone.set_status(status)


def on_message(callback: Callable[[Dict[str, Any]], None]):
    """设置回调"""
    _phone.on_message = callback


def set_network(network):
    """注入网络适配器（系统内部调用）"""
    _phone.set_network(network)
