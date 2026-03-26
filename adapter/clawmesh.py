"""
ClawMeshAdapter - ClawPhone 的 ClawMesh 网络适配器

将 ClawMesh UDP 传输封装为 ClawPhone 期望的同步适配器接口。

设计：
- 内部运行 asyncio 事件循环（独立线程）
- 通过线程安全的 queue 处理回调和 send 请求
- address = node_id（ClawMesh 节点标识）
"""

import asyncio
import logging
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger(__name__)

# Import Phase 5 components
try:
    from p2p.transport.udp_direct import UdpDirectTransport
    from p2p.config import UdpTransportConfig, StunConfig, PunchHoleConfig
    from adapter.message import Message, MessagePayload, MessageRouting, MessageMeta
    PHASE5_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ClawMesh dependencies not available: {e}")
    PHASE5_AVAILABLE = False

class ClawMeshAdapter:
    """ClawPhone 到 ClawMesh 的适配器（同步接口）"""
    
    def __init__(
        self,
        node_id: str,
        stun_servers: list = None,
        bootstrap_nodes: list = None,
        enable_crypto: bool = False
    ):
        """
        初始化适配器。
        
        Args:
            node_id: ClawMesh 节点 ID（应与 ClawPhone phone_id 关联）
            stun_servers: STUN server 列表 [(host, port), ...]
            bootstrap_nodes: 引导节点地址（用于初始路由发现），可选
            enable_crypto: 是否启用加密（测试时可关）
        """
        self.node_id = node_id
        self.stun_servers = stun_servers or [("127.0.0.1", 8766)]
        self.bootstrap_nodes = bootstrap_nodes or []
        self.enable_crypto = enable_crypto
        
        # 线程间通信
        self._command_queue = queue.Queue()
        self._event_loop_thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._transport: Optional[UdpDirectTransport] = None
        self._stopped = threading.Event()
        
        self._address: Optional[str] = None
        self._on_message_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        
        logger.info(f"[ClawMeshAdapter] init: node_id={node_id}, stun={stun_servers}")
    
    def start(self) -> str:
        """
        启动适配器（同步方法，内部启动 asyncio 线程）。
        
        Returns:
            address (node_id)
        """
        if not PHASE5_AVAILABLE:
            raise RuntimeError("ClawMesh components not available")
        
        # 启动事件循环线程
        self._event_loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self._event_loop_thread.start()
        
        # 等待启动完成
        while self._address is None and not self._stopped.is_set():
            time.sleep(0.1)
        
        if self._stopped.is_set():
            raise RuntimeError("Adapter failed to start")
        
        logger.info(f"[ClawMeshAdapter] started, address={self._address}")
        return self._address
    
    def _run_loop(self):
        """在独立线程中运行 asyncio 事件循环"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        self._loop = asyncio.get_event_loop()
        
        try:
            # 创建 transport 协程并运行
            self._transport = self._loop.run_until_complete(self._create_transport())
            self._address = self.node_id
            
            # 处理命令队列（send 请求）
            self._loop.run_forever()
        except Exception as e:
            logger.error(f"[ClawMeshAdapter] loop error: {e}")
            self._stopped.set()
        finally:
            self._loop.close()
    
    async def _create_transport(self) -> UdpDirectTransport:
        """创建并启动 UdpDirectTransport"""
        config = UdpTransportConfig(
            stun=StunConfig(servers=self.stun_servers),
            punch_hole=PunchHoleConfig(timeout=15.0),
            routing_broadcast_interval=30.0,
            enable_crypto=self.enable_crypto
        )
        
        transport = UdpDirectTransport(
            config=config,
            node_id=self.node_id,
            message_handler=self._handle_inbound_message
        )
        
        await transport.start()
        logger.info(f"[ClawMeshAdapter] transport started")
        return transport
    
    def _handle_inbound_message(self, message: Message, sender_id: str):
        """处理来自 ClawMesh 的消息，转换为 ClawPhone 格式"""
        try:
            phone_msg = {
                "type": "call",
                "from": sender_id,
                "content": message.payload.content,
                "timestamp": message.meta.timestamp
            }
            
            if self._on_message_callback:
                # 回调可能是阻塞的，直接调用（在 transport 的事件循环线程）
                try:
                    self._on_message_callback(phone_msg)
                except Exception as e:
                    logger.error(f"[ClawMeshAdapter] callback error: {e}")
        except Exception as e:
            logger.error(f"[ClawMeshAdapter] message handling error: {e}")
    
    def on_message(self, callback: Callable[[Dict[str, Any]], None]):
        """设置消息回调（同步函数）"""
        self._on_message_callback = callback
    
    def send(self, target: str, payload: dict) -> bool:
        """
        同步发送消息（ClawPhone 接口）。
        
        Args:
            target: 目标 node_id 或 phone_id（此处直接用 node_id）
            payload: {"type": "call", "content": "..."}
            
        Returns:
            bool 表示发送是否成功
        """
        if not self._transport or not self._loop:
            logger.error("[ClawMeshAdapter] not started")
            return False
        
        msg_type = payload.get("type", "call")
        content = payload.get("content", "")
        
        try:
            # 构造 Message 对象
            msg = Message(
                meta=MessageMeta(
                    node_id=self.node_id,
                    timestamp=int(time.time()),
                    protocol_version="1.0"
                ),
                payload=MessagePayload(
                    type="text" if msg_type == "call" else msg_type,
                    content=content
                ),
                routing=MessageRouting(
                    to=target,
                    hops=[],
                    ttl=10,
                    route_required=True
                )
            )
            
            # 异步发送，同步等待结果
            future = asyncio.run_coroutine_threadsafe(
                self._transport.send(msg, target),
                self._loop
            )
            success = future.result(timeout=10.0)
            return success
            
        except Exception as e:
            logger.error(f"[ClawMeshAdapter] send failed: {e}")
            return False
    
    def stop(self):
        """停止适配器"""
        self._stopped.set()
        if self._loop and self._transport:
            future = asyncio.run_coroutine_threadsafe(
                self._transport.stop(),
                self._loop
            )
            try:
                future.result(timeout=5.0)
            except:
                pass
            self._loop.call_soon_threadsafe(self._loop.stop)
        
        if self._event_loop_thread and self._event_loop_thread.is_alive():
            self._event_loop_thread.join(timeout=5.0)
        
        logger.info("[ClawMeshAdapter] stopped")
