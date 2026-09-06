# Multi-Agent 快速运行指南

## 🚀 立即开始

### 1. 运行单元测试（验证安装）

```bash
cd P:\github\Harness
python test_multi_agent.py
```

**预期输出**：
```
test_agent_registration ... ok
test_broadcast ... ok
test_list_agents ... ok
test_message_deduplication ... ok
test_send_and_receive_message ... ok
test_sha256_digest ... ok
test_task_lock_acquire_release ... ok
test_task_lock_cas_mismatch ... ok
test_task_lock_renew ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.038s

OK
[PASS] 通过: 9
[FAIL] 失败: 0
[ERROR] 错误: 0
```

---

### 2. 运行快速演示

```bash
python demo_quick.py
```

**演示内容**：
- ✅ 基本消息通信
- ✅ 任务锁协作
- ✅ 广播消息
- ✅ 列出 Agent

**运行时间**：约 5 秒

---

### 3. 多终端交互（真实场景）

#### 终端 1（启动 Alice）

```bash
python -m clawbot.multi_agent_cli --agent-id agent-alice
```

**可用命令**：
```
send <agent_id> <message>  - 发送消息
broadcast <message>        - 广播消息
receive                    - 接收消息
list                       - 列出所有 Agent
lock <task_id>             - 获取任务锁
unlock <task_id> <digest>  - 释放任务锁
help                       - 显示帮助
exit                       - 退出
```

#### 终端 2（启动 Bob）

```bash
python -m clawbot.multi_agent_cli --agent-id agent-bob
```

#### 交互示例

**终端 1（Alice）**：
```
[agent-alice]> send agent-bob Hello Bob!
✓ 消息已发送到 agent-bob

[agent-alice]> lock learn-phase2
🔒 成功获取任务锁: learn-phase2
   摘要: a1b2c3d4e5f6...
   过期时间: 2026-09-06T17:00:00
```

**终端 2（Bob）**：
```
📨 收到 1 条新消息:
  ├─ 来自: agent-alice
  ├─ 时间: 2026-09-06T16:55:00
  └─ 内容: {'text': 'Hello Bob!'}

[agent-bob]> send agent-alice Hi Alice!
✓ 消息已发送到 agent-alice

[agent-bob]> lock learn-phase2
❌ 锁已被占用
   所有者: agent-alice
   过期时间: 2026-09-06T17:00:00
```

---

## 📊 核心功能演示

### 功能 1：消息发送与接收

```python
from clawbot.multi_agent_core import AgentMessenger

# 创建两个 Agent
alice = AgentMessenger("alice")
bob = AgentMessenger("bob")

# Alice 发送消息
alice.send_message("bob", {"text": "Hello"})

# Bob 接收消息
messages = bob.receive_messages()
print(messages)  # [{'from_agent': 'alice', 'content': {'text': 'Hello'}, ...}]
```

### 功能 2：任务锁

```python
# Alice 获取锁
result = alice.task_lock.acquire("task-001", "alice")
if result['success']:
    digest = result['lock']['lease_digest']
    
    # 执行任务...
    
    # 释放锁
    alice.task_lock.release("task-001", "alice", digest)
```

### 功能 3：广播消息

```python
# Alice 广播消息
alice.broadcast({"text": "Hello everyone!"})

# 所有其他 Agent 都会收到
```

---

## 🎯 实战场景

### 场景：协作学习

**Learner Agent**（学习者）：
```python
learner = AgentMessenger("learner")

# 1. 获取学习任务锁
lock = learner.task_lock.acquire("learn-phase2", "learner")

# 2. 学习...
print("正在学习 Phase 2...")

# 3. 完成后请求审查
learner.send_message("reviewer", {
    "type": "review_request",
    "phase": "phase2",
    "notes": "已完成学习，请审查"
})
```

**Reviewer Agent**（审查者）：
```python
reviewer = AgentMessenger("reviewer")

# 1. 接收审查请求
messages = reviewer.receive_messages()
review_req = next(m for m in messages if m['content']['type'] == 'review_request')

# 2. 审查...
print(f"正在审查: {review_req['content']['phase']}")

# 3. 提供反馈
reviewer.send_message("learner", {
    "type": "review_feedback",
    "status": "approved",
    "comments": "做得很好！继续 Phase 3"
})
```

---

## 📁 生成的文件

运行后会在项目根目录生成 `.clawbot/` 目录：

```
.clawbot/
├── agents/                      # Agent 注册表
│   ├── agent-alice.json
│   └── agent-bob.json
├── messages/                    # 消息队列
│   ├── agent-alice/
│   │   └── msg-uuid.json
│   └── agent-bob/
│       └── msg-uuid.json
├── locks/                       # 任务锁
│   └── learn-phase2.lock
└── receipts/                    # 消息去重记录
    └── agent-alice-receipts.json
```

**可以直接查看这些 JSON 文件来理解系统运行原理！**

---

## 🔧 故障排除

### 问题 1：无法发送消息

**解决方法**：
```bash
# 检查目标 Agent 是否已注册
ls .clawbot/agents/
```

### 问题 2：锁获取失败

**解决方法**：
```python
# 检查锁状态
import json
with open('.clawbot/locks/task-001.lock', 'r') as f:
    lock = json.load(f)
    print(lock['owner_agent'])
    print(lock['expires_at'])
```

### 问题 3：消息重复接收

**不会发生！** 我们有消息去重机制：
```python
# 检查去重记录
import json
with open('.clawbot/receipts/agent-alice-receipts.json', 'r') as f:
    receipts = json.load(f)
    print(receipts['delivered_digests'])
```

---

## 📚 进一步学习

1. **阅读文档**：
   - [Multi-Agent 协作系统](docs/09-multi-agent-system.md)
   - [DevCodex 集成方案](docs/08-devcodex-integration-plan.md)

2. **查看源码**：
   - `clawbot/multi_agent_core.py` - 核心实现
   - `clawbot/multi_agent_cli.py` - CLI 工具

3. **运行完整演示**：
   ```bash
   python demo_multi_agent.py
   ```

4. **集成到你的项目**：
   ```python
   from clawbot.multi_agent_core import AgentMessenger
   
   agent = AgentMessenger("my-agent")
   # 开始使用...
   ```

---

## ✅ 检查清单

- [x] 单元测试通过（9/9）
- [x] 快速演示运行成功
- [x] 多终端交互正常
- [x] 消息发送/接收正常
- [x] 任务锁机制正常
- [x] 消息去重正常
- [x] Agent 注册/发现正常
- [x] 广播消息正常

**所有功能均已验证通过！**

---

## 🎉 恭喜！

你已经成功实现了一个完整的 Multi-Agent 协作系统！

**核心特性**：
- ✅ 文件系统消息队列
- ✅ 5 分钟任务锁租期
- ✅ CAS 一致性保证
- ✅ SHA256 消息去重
- ✅ Agent 注册与发现
- ✅ 心跳机制
- ✅ 广播消息

**参考**：
- DevCodex: https://github.com/devcodex-labs/devcodex
- ClawBot: https://github.com/lpzams/ClawBot

---

生成时间：2026-09-06
