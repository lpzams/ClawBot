# ClawBot Multi-Agent 系统

基于 DevCodex 设计理念的多 Agent 协作框架，支持多个终端同时运行并互相通信。

## 🎯 核心特性

### ✅ 已实现（借鉴 DevCodex）

1. **文件系统消息队列**
   - 每个 Agent 有独立收件箱
   - 消息持久化，断电不丢失
   - 自动去重机制

2. **任务锁机制（Fenced Task Write Owner）**
   - 5 分钟自动过期
   - CAS（Compare-And-Swap）保证一致性
   - 支持 acquire/renew/release

3. **消息去重（Context Delivery Ledger）**
   - 防止重复处理相同消息
   - 基于 SHA256 摘要

4. **Agent 注册与发现**
   - 自动注册到共享目录
   - 心跳机制
   - 列出所有在线 Agent

---

## 📚 DevCodex 核心设计分析

### 1. 生命周期管理（lifecycle.cjs）

**DevCodex 做法**：
```javascript
// 统一生命周期钩子，处理所有事件
const HOOKS = {
  UserPromptSubmit: [...],
  PreToolUse: [...],
  PostToolUse: [...],
  PreCompact: [...],
  Stop: [...]
}
```

**ClawBot 借鉴**：
```python
# 在 LangGraph Agent 的 checkpoint 中集成
agent = create_clawbot_agent(...)
agent.on_turn_start = lambda: messenger.heartbeat()
agent.on_message = lambda: messenger.receive_messages()
```

### 2. 任务锁（fenced-task-write-owner.cjs）

**DevCodex 核心机制**：
```javascript
// 5 分钟租期
const WRITE_OWNER_LEASE_MS = 5 * 60 * 1000

// CAS 保证一致性
function exactOwnerRefMatches(owner, expected) {
  return owner.ownerGeneration === expected.ownerGeneration &&
         owner.ownerNonce === expected.ownerNonce &&
         owner.leaseRevision === expected.leaseRevision &&
         owner.leaseDigest === expected.leaseDigest
}
```

**ClawBot 实现**：
```python
# clawbot/multi_agent_core.py
class FencedTaskWriteOwner:
    def acquire(self, task_id, agent_id):
        # 检查现有锁
        # 创建新锁（5 分钟过期）
        # 返回 lease_digest
    
    def renew(self, task_id, agent_id, expected_digest):
        # CAS 检查
        # 延长过期时间
        # 递增 lease_revision
```

### 3. 消息去重（context-delivery-ledger-v2.cjs）

**DevCodex 核心思路**：
```javascript
// 检查消息是否已投递
function getContextDeliveryDecision(input) {
  const descriptor = createDescriptor(input)
  const receipts = readReceipts()
  const observed = receipts.find(r => 
    r.deliveryLeaseId === descriptor.deliveryLeaseId
  )
  
  return observed 
    ? { status: 'reuse-observed-body', bodyDeliverySkipped: true }
    : { status: 'full-delivery', bodyDeliverySkipped: false }
}
```

**ClawBot 实现**：
```python
class ContextDeliveryLedger:
    def should_deliver(self, agent_id, message_digest):
        # 读取已投递记录
        # 检查 message_digest 是否存在
        return message_digest not in delivered_digests
    
    def mark_delivered(self, agent_id, message_digest):
        # 记录已投递
        delivered_digests.append(message_digest)
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd P:\github\Harness
pip install -e .
```

### 2. 运行测试

```bash
# 运行单元测试
python test_multi_agent.py

# 预期输出：
# 🧪 运行 Multi-Agent 核心功能测试...
# test_agent_registration ... ok
# test_broadcast ... ok
# test_message_deduplication ... ok
# test_send_and_receive_message ... ok
# test_task_lock_acquire_release ... ok
# test_task_lock_renew ... ok
# ...
# ✅ 通过: 9
```

### 3. 运行演示

```bash
# 运行完整演示
python demo_multi_agent.py

# 演示内容：
# - 基本消息通信
# - 任务锁协作
# - 广播消息
# - 协作学习场景
```

### 4. 多终端交互

**终端 1（Agent Alice）**：
```bash
python -m clawbot.multi_agent_cli --agent-id agent-alice

[agent-alice]> send agent-bob 你好 Bob！
✅ 消息已发送到 agent-bob

[agent-alice]> lock learn-phase2
🔒 成功获取任务锁: learn-phase2
   摘要: a1b2c3d4e5f6...
```

**终端 2（Agent Bob）**：
```bash
python -m clawbot.multi_agent_cli --agent-id agent-bob

📨 收到 1 条新消息:
  ├─ 来自: agent-alice
  ├─ 时间: 2026-09-06T16:45:30
  └─ 内容: {'text': '你好 Bob！'}

[agent-bob]> send agent-alice 你好 Alice！
✅ 消息已发送到 agent-alice

[agent-bob]> lock learn-phase2
❌ 锁已被占用
   所有者: agent-alice
```

---

## 📁 文件结构

```
.clawbot/
├── agents/                      # Agent 注册表
│   ├── agent-alice.json
│   └── agent-bob.json
├── messages/                    # 消息队列
│   ├── agent-alice/            # Alice 的收件箱
│   │   └── msg-uuid.json
│   └── agent-bob/              # Bob 的收件箱
│       └── msg-uuid.json
├── locks/                       # 任务锁
│   └── learn-phase2.lock
├── receipts/                    # 消息去重记录
│   ├── agent-alice-receipts.json
│   └── agent-bob-receipts.json
└── checkpoints/                 # LangGraph 状态（未来集成）
    └── agent-alice.db
```

---

## 🔑 核心 API

### AgentMessenger

```python
from clawbot.multi_agent_core import AgentMessenger

# 创建 Agent
agent = AgentMessenger("agent-001", root_dir=".clawbot")

# 发送消息
agent.send_message("agent-002", {"text": "Hello"})

# 接收消息
messages = agent.receive_messages()

# 广播消息
agent.broadcast({"text": "Hello everyone"})

# 列出所有 Agent
agents = agent.list_agents()
```

### FencedTaskWriteOwner

```python
# 获取任务锁
result = agent.task_lock.acquire("task-001", "agent-001")
if result['success']:
    digest = result['lock']['lease_digest']
    
    # 执行任务...
    
    # 释放锁
    agent.task_lock.release("task-001", "agent-001", digest)
```

### ContextDeliveryLedger

```python
# 检查是否应该投递
if agent.delivery_ledger.should_deliver(agent_id, message_digest):
    # 处理消息
    process_message(message)
    
    # 标记已投递
    agent.delivery_ledger.mark_delivered(agent_id, message_digest)
```

---

## 🎓 使用场景

### 场景 1：协作学习

```python
# Learner Agent
learner = AgentMessenger("learner")

# 获取学习任务锁
lock = learner.task_lock.acquire("learn-phase2", "learner")

# 完成学习后请求审查
learner.send_message("reviewer", {
    "type": "review_request",
    "phase": "phase2",
    "notes": "已完成学习"
})

# Reviewer Agent
reviewer = AgentMessenger("reviewer")

# 接收审查请求
messages = reviewer.receive_messages()

# 审查后提供反馈
reviewer.send_message("learner", {
    "type": "review_feedback",
    "status": "approved",
    "comments": "做得很好！"
})
```

### 场景 2：任务分配

```python
# Coordinator Agent
coordinator = AgentMessenger("coordinator")

# 广播任务
coordinator.broadcast({
    "type": "task_available",
    "task_id": "learn-phase3",
    "description": "学习 Phase 3"
})

# Worker Agent
worker = AgentMessenger("worker-001")

# 接收任务
messages = worker.receive_messages()
task = next(m for m in messages if m['content']['type'] == 'task_available')

# 尝试获取任务锁
lock = worker.task_lock.acquire(task['content']['task_id'], "worker-001")
if lock['success']:
    # 执行任务
    print("开始执行任务")
```

---

## 🆚 DevCodex vs ClawBot

| 特性 | DevCodex | ClawBot Multi-Agent |
|------|----------|---------------------|
| **语言** | Node.js | Python |
| **消息队列** | 文件系统 | 文件系统（相同） |
| **任务锁** | fenced-task-write-owner.cjs | FencedTaskWriteOwner（Python 实现） |
| **消息去重** | context-delivery-ledger-v2.cjs | ContextDeliveryLedger（Python 实现） |
| **租期时间** | 5 分钟 | 5 分钟（相同） |
| **CAS 机制** | ✅ | ✅ |
| **生命周期** | lifecycle.cjs（6 个钩子） | 未来集成到 LangGraph |
| **宿主依赖** | Copilot/Claude Code | 独立运行 |
| **适用场景** | 代码工程 | 学习框架 + 通用协作 |

---

## 🔄 集成到现有 LangGraph Agent

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from clawbot.multi_agent_core import AgentMessenger

def create_multi_agent_clawbot(agent_id: str, provider: str, model: str):
    """创建支持多 Agent 通信的 ClawBot"""
    
    # 初始化消息通信
    messenger = AgentMessenger(agent_id, root_dir=".clawbot")
    
    # 创建 LangGraph Agent
    agent = create_clawbot_agent(
        provider=provider,
        model=model,
        checkpoint_db=f".clawbot/checkpoints/{agent_id}.db"
    )
    
    # 包装 invoke 方法
    original_invoke = agent.invoke
    
    def invoke_with_messaging(input_dict):
        # 1. 检查新消息
        messages = messenger.receive_messages()
        if messages:
            print(f"📨 收到 {len(messages)} 条消息")
            input_dict["messages"] = messages
        
        # 2. 执行原有逻辑
        result = original_invoke(input_dict)
        
        # 3. 心跳
        messenger.heartbeat()
        
        return result
    
    agent.invoke = invoke_with_messaging
    agent.messenger = messenger
    
    return agent
```

---

## 📈 下一步计划

### P0（立即实现）
- [x] 消息发送/接收
- [x] Agent 注册与发现
- [x] 任务锁机制
- [x] 消息去重
- [x] CLI 工具
- [x] 单元测试

### P1（本周）
- [ ] 集成到 LangGraph Agent
- [ ] 消息优先级队列
- [ ] 任务状态持久化
- [ ] 跨会话恢复

### P2（下周）
- [ ] Web 可视化界面
- [ ] 实时消息监听（watchdog）
- [ ] 任务协作工作流
- [ ] 性能优化

### P3（未来）
- [ ] 升级到 Redis（高性能场景）
- [ ] 支持远程通信（跨机器）
- [ ] 消息加密
- [ ] 权限控制

---

## 🤝 致谢

本项目核心设计灵感来自 [DevCodex](https://github.com/devcodex-labs/devcodex)：

- `fenced-task-write-owner.cjs` - 任务锁机制
- `context-delivery-ledger-v2.cjs` - 消息去重
- `lifecycle.cjs` - 生命周期管理

我们将 DevCodex 的 Node.js 实现翻译为 Python，并适配到 ClawBot 学习框架。

---

## 📝 许可证

MIT License

---

## 🐛 问题反馈

如有问题，请提交 Issue 或联系项目维护者。
