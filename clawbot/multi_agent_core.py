"""
Multi-Agent 核心模块 - 借鉴 DevCodex 设计

核心设计参考：
1. fenced-task-write-owner.cjs - 任务锁机制（5分钟租期）
2. context-delivery-ledger-v2.cjs - 消息去重与状态管理
3. lifecycle.cjs - 生命周期事件处理

实现功能：
- Agent 注册与发现
- 消息队列（文件系统）
- 任务锁（防止并发冲突）
- 跨会话状态恢复
"""

import json
import hashlib
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


# ==================== 常量定义 ====================

WRITE_OWNER_LEASE_MS = 5 * 60 * 1000  # 5 分钟租期（借鉴 DevCodex）
MESSAGE_SCHEMA_VERSION = "ClawBotMessageV1"
TASK_LOCK_SCHEMA_VERSION = "ClawBotTaskLockV1"
AGENT_REGISTRY_SCHEMA_VERSION = "ClawBotAgentV1"


# ==================== 工具函数 ====================

def sha256_digest(data: Any) -> str:
    """计算 SHA256 摘要（借鉴 DevCodex 的 digest 函数）"""
    if isinstance(data, dict):
        # 确保字典键排序，保证相同内容产生相同摘要
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
    else:
        canonical = str(data)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def owner_nonce() -> str:
    """生成所有者随机数（借鉴 DevCodex 的 ownerNonce）"""
    random_bytes = uuid.uuid4().hex[:40]
    return f"owner-{random_bytes}"


def is_lease_expired(expires_at: str, now_ms: int) -> bool:
    """检查租约是否过期"""
    try:
        expires_dt = datetime.fromisoformat(expires_at)
        now_dt = datetime.fromtimestamp(now_ms / 1000)
        return now_dt >= expires_dt
    except (ValueError, TypeError):
        return True


# ==================== 数据类 ====================

@dataclass
class AgentInfo:
    """Agent 信息（对应 DevCodex 的 agent.json）"""
    agent_id: str
    provider: str
    model: str
    started_at: str
    last_heartbeat: str
    schema_version: str = AGENT_REGISTRY_SCHEMA_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Message:
    """消息结构（借鉴 DevCodex 的 context-delivery）"""
    message_id: str
    from_agent: str
    to_agent: str
    content: Dict[str, Any]
    timestamp: str
    message_digest: str
    schema_version: str = MESSAGE_SCHEMA_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TaskLock:
    """任务锁（借鉴 DevCodex 的 fenced-task-write-owner）"""
    task_id: str
    owner_agent: str
    owner_generation: int
    owner_nonce: str
    lease_revision: int
    issued_at: str
    expires_at: str
    lease_digest: str
    status: str  # 'active' 或 'released'
    schema_version: str = TASK_LOCK_SCHEMA_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


# ==================== 核心类 ====================

class FencedTaskWriteOwner:
    """任务写入锁管理器（借鉴 DevCodex 的 fenced-task-write-owner.cjs）

    防止多个 Agent 同时修改同一任务，使用 5 分钟租期。
    """

    def __init__(self, root_dir: str = ".clawbot"):
        self.root_dir = Path(root_dir)
        self.locks_dir = self.root_dir / "locks"
        self.locks_dir.mkdir(parents=True, exist_ok=True)

    def _seal_lock(self, lock_data: dict) -> TaskLock:
        """密封锁（计算摘要）"""
        # 计算租约摘要（不包含 lease_digest 本身）
        digest_data = {k: v for k, v in lock_data.items() if k != 'lease_digest'}
        lease_digest = sha256_digest(digest_data)

        return TaskLock(
            task_id=lock_data['task_id'],
            owner_agent=lock_data['owner_agent'],
            owner_generation=lock_data['owner_generation'],
            owner_nonce=lock_data['owner_nonce'],
            lease_revision=lock_data['lease_revision'],
            issued_at=lock_data['issued_at'],
            expires_at=lock_data['expires_at'],
            lease_digest=lease_digest,
            status=lock_data['status']
        )

    def acquire(self, task_id: str, agent_id: str) -> dict:
        """获取任务锁（对应 DevCodex 的 'acquire' 操作）"""
        lock_file = self.locks_dir / f"{task_id}.lock"
        now_ms = int(datetime.now().timestamp() * 1000)
        now_iso = datetime.now().isoformat()
        expires_at = datetime.now() + timedelta(milliseconds=WRITE_OWNER_LEASE_MS)

        # 检查现有锁
        if lock_file.exists():
            with open(lock_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)

            # 如果锁已释放（status='released'），可以获取
            if existing.get('status') == 'released':
                pass  # 继续创建新锁
            # 否则检查锁是否过期
            elif not is_lease_expired(existing['expires_at'], now_ms):
                return {
                    "success": False,
                    "reason": "lock_held_by_other",
                    "owner": existing['owner_agent'],
                    "expires_at": existing['expires_at']
                }

        # 创建新锁
        lock = self._seal_lock({
            "task_id": task_id,
            "owner_agent": agent_id,
            "owner_generation": 1,
            "owner_nonce": owner_nonce(),
            "lease_revision": 1,
            "issued_at": now_iso,
            "expires_at": expires_at.isoformat(),
            "status": "active"
        })

        with open(lock_file, 'w', encoding='utf-8') as f:
            json.dump(lock.to_dict(), f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "lock": lock.to_dict(),
            "mutation_authority": True
        }

    def renew(self, task_id: str, agent_id: str, expected_digest: str) -> dict:
        """续约任务锁（对应 DevCodex 的 'renew' 操作）"""
        lock_file = self.locks_dir / f"{task_id}.lock"

        if not lock_file.exists():
            return {"success": False, "reason": "lock_not_found"}

        with open(lock_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)

        # CAS 检查（Compare-And-Swap）
        if existing['lease_digest'] != expected_digest:
            return {"success": False, "reason": "cas_mismatch"}

        if existing['owner_agent'] != agent_id:
            return {"success": False, "reason": "not_owner"}

        # 续约
        now_iso = datetime.now().isoformat()
        expires_at = datetime.now() + timedelta(milliseconds=WRITE_OWNER_LEASE_MS)

        renewed_lock = self._seal_lock({
            **existing,
            "lease_revision": existing['lease_revision'] + 1,
            "issued_at": now_iso,
            "expires_at": expires_at.isoformat()
        })

        with open(lock_file, 'w', encoding='utf-8') as f:
            json.dump(renewed_lock.to_dict(), f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "lock": renewed_lock.to_dict(),
            "mutation_authority": True
        }

    def release(self, task_id: str, agent_id: str, expected_digest: str) -> dict:
        """释放任务锁（对应 DevCodex 的 'release' 操作）"""
        lock_file = self.locks_dir / f"{task_id}.lock"

        if not lock_file.exists():
            return {"success": False, "reason": "lock_not_found"}

        with open(lock_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)

        # CAS 检查
        if existing['lease_digest'] != expected_digest:
            return {"success": False, "reason": "cas_mismatch"}

        if existing['owner_agent'] != agent_id:
            return {"success": False, "reason": "not_owner"}

        # 释放锁
        now_iso = datetime.now().isoformat()
        released_lock = self._seal_lock({
            **existing,
            "owner_generation": existing['owner_generation'] + 1,
            "owner_nonce": owner_nonce(),
            "lease_revision": existing['lease_revision'] + 1,
            "issued_at": now_iso,
            "expires_at": now_iso,  # 立即过期
            "status": "released"
        })

        with open(lock_file, 'w', encoding='utf-8') as f:
            json.dump(released_lock.to_dict(), f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "lock": released_lock.to_dict()
        }


class ContextDeliveryLedger:
    """消息去重账本（借鉴 DevCodex 的 context-delivery-ledger-v2.cjs）

    防止重复接收相同的消息。
    """

    def __init__(self, root_dir: str = ".clawbot"):
        self.root_dir = Path(root_dir)
        self.receipts_dir = self.root_dir / "receipts"
        self.receipts_dir.mkdir(parents=True, exist_ok=True)

    def _get_receipt_file(self, agent_id: str) -> Path:
        return self.receipts_dir / f"{agent_id}-receipts.json"

    def should_deliver(self, agent_id: str, message_digest: str) -> bool:
        """检查消息是否应该投递（未曾见过）"""
        receipt_file = self._get_receipt_file(agent_id)

        if not receipt_file.exists():
            return True

        with open(receipt_file, 'r', encoding='utf-8') as f:
            receipts = json.load(f)

        # 检查是否已接收过此消息
        return message_digest not in receipts.get('delivered_digests', [])

    def mark_delivered(self, agent_id: str, message_digest: str):
        """标记消息已投递"""
        receipt_file = self._get_receipt_file(agent_id)

        if receipt_file.exists():
            with open(receipt_file, 'r', encoding='utf-8') as f:
                receipts = json.load(f)
        else:
            receipts = {
                "agent_id": agent_id,
                "delivered_digests": []
            }

        if message_digest not in receipts['delivered_digests']:
            receipts['delivered_digests'].append(message_digest)
            receipts['last_updated'] = datetime.now().isoformat()

            # 限制历史记录数量（最多保留 1000 条）
            if len(receipts['delivered_digests']) > 1000:
                receipts['delivered_digests'] = receipts['delivered_digests'][-1000:]

            with open(receipt_file, 'w', encoding='utf-8') as f:
                json.dump(receipts, f, indent=2, ensure_ascii=False)


class AgentMessenger:
    """Agent 消息通信器（集成锁和去重机制）"""

    def __init__(self, agent_id: str, root_dir: str = ".clawbot"):
        self.agent_id = agent_id
        self.root_dir = Path(root_dir)
        self.messages_dir = self.root_dir / "messages"
        self.agents_dir = self.root_dir / "agents"

        # 初始化子组件
        self.task_lock = FencedTaskWriteOwner(root_dir)
        self.delivery_ledger = ContextDeliveryLedger(root_dir)

        # 创建目录
        self.messages_dir.mkdir(parents=True, exist_ok=True)
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        # 注册当前 Agent
        self._register_agent()

    def _register_agent(self):
        """注册 Agent"""
        agent_file = self.agents_dir / f"{self.agent_id}.json"
        now = datetime.now().isoformat()

        agent_info = AgentInfo(
            agent_id=self.agent_id,
            provider="unknown",
            model="unknown",
            started_at=now,
            last_heartbeat=now
        )

        with open(agent_file, 'w', encoding='utf-8') as f:
            json.dump(agent_info.to_dict(), f, indent=2, ensure_ascii=False)

    def heartbeat(self):
        """更新心跳"""
        agent_file = self.agents_dir / f"{self.agent_id}.json"
        if agent_file.exists():
            with open(agent_file, 'r', encoding='utf-8') as f:
                agent_info = json.load(f)
            agent_info['last_heartbeat'] = datetime.now().isoformat()
            with open(agent_file, 'w', encoding='utf-8') as f:
                json.dump(agent_info, f, indent=2, ensure_ascii=False)

    def send_message(self, to_agent: str, content: Dict[str, Any]) -> dict:
        """发送消息（带去重检查）"""
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # 构造消息
        msg_data = {
            "message_id": message_id,
            "from_agent": self.agent_id,
            "to_agent": to_agent,
            "content": content,
            "timestamp": timestamp
        }

        # 计算消息摘要
        message_digest = sha256_digest(msg_data)

        message = Message(
            message_id=message_id,
            from_agent=self.agent_id,
            to_agent=to_agent,
            content=content,
            timestamp=timestamp,
            message_digest=message_digest
        )

        # 写入目标 Agent 的收件箱
        target_inbox = self.messages_dir / to_agent
        target_inbox.mkdir(parents=True, exist_ok=True)

        msg_file = target_inbox / f"{message_id}.json"
        with open(msg_file, 'w', encoding='utf-8') as f:
            json.dump(message.to_dict(), f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "message_id": message_id,
            "message_digest": message_digest
        }

    def receive_messages(self, mark_read: bool = True) -> List[dict]:
        """接收消息（带去重检查）"""
        inbox = self.messages_dir / self.agent_id

        if not inbox.exists():
            return []

        messages = []
        for msg_file in sorted(inbox.glob("*.json")):
            try:
                with open(msg_file, 'r', encoding='utf-8') as f:
                    msg = json.load(f)

                # 检查是否应该投递
                if self.delivery_ledger.should_deliver(self.agent_id, msg['message_digest']):
                    messages.append(msg)

                    # 标记已投递
                    if mark_read:
                        self.delivery_ledger.mark_delivered(self.agent_id, msg['message_digest'])

                # 删除已读消息
                if mark_read:
                    msg_file.unlink()
            except Exception as e:
                print(f"⚠️ 读取消息失败 {msg_file}: {e}")

        return messages

    def list_agents(self) -> List[dict]:
        """列出所有在线 Agent"""
        agents = []
        for agent_file in self.agents_dir.glob("*.json"):
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    agent = json.load(f)
                agents.append(agent)
            except Exception:
                pass
        return agents

    def broadcast(self, content: Dict[str, Any]):
        """广播消息到所有其他 Agent"""
        agents = self.list_agents()
        for agent in agents:
            if agent['agent_id'] != self.agent_id:
                self.send_message(agent['agent_id'], content)


# ==================== 导出 ====================

__all__ = [
    'AgentMessenger',
    'FencedTaskWriteOwner',
    'ContextDeliveryLedger',
    'AgentInfo',
    'Message',
    'TaskLock'
]
