# DevCodex 集成方案

## 目标

实现多个 ClawBot Agent 终端同时运行并互相通信，借鉴 DevCodex 的设计思想。

## 方案对比

### 方案 A：直接集成 DevCodex（不推荐）

**优点**：
- 获得完整的工程化能力
- 80+ 专业 Skills

**缺点**：
- ❌ DevCodex 是 Node.js，ClawBot 是 Python（跨语言复杂）
- ❌ DevCodex 依赖特定宿主（Copilot/Claude Code）
- ❌ DevCodex 的 Skills 针对代码工程，不适合学习框架
- ❌ 需要维护两套技术栈

**结论**：技术栈不兼容，维护成本高。

---

### 方案 B：借鉴设计，Python 实现（推荐）✅

**核心思想**：
1. 用文件系统作为消息队列
2. 实现任务状态持久化
3. 支持跨会话恢复
4. 防止并发冲突

**优点**：
- ✅ 纯 Python 实现，无跨语言问题
- ✅ 保持 ClawBot 的简洁性
- ✅ 完全控制实现细节
- ✅ 可以逐步迭代

**实现计划**：

#### Phase 1：多终端消息通信

```python
# 目录结构
.clawbot/
├── agents/                      # Agent 注册表
│   ├── agent-001.json          # Agent 元信息
│   └── agent-002.json
├── messages/                    # 消息队列
│   ├── agent-001/              # Agent 001 的收件箱
│   │   ├── msg-001.json
│   │   └── msg-002.json
│   └── agent-002/
├── tasks/                       # 任务状态
│   ├── task-001.json
│   └── task-002.json
└── locks/                       # 并发锁
    └── task-001.lock
```

**核心功能**：
- Agent 注册与发现
- 消息发送与接收
- 轮询或 watchdog 监听
- 文件锁防止冲突

#### Phase 2：任务状态管理

借鉴 DevCodex 的 `context-delivery-ledger`：

```python
{
  "task_id": "learn-phase2",
  "status": "in_progress",
  "owner": "agent-001",
  "owner_expires_at": "2026-09-06T17:00:00Z",
  "checkpoints": [
    {
      "phase": "phase2-adapter",
      "completed": true,
      "timestamp": "2026-09-06T16:00:00Z"
    }
  ],
  "context": {
    "current_phase": "phase2-adapter",
    "last_agent": "agent-001"
  }
}
```

#### Phase 3：跨会话恢复

- 保存 LangGraph 的 checkpoint
- 记录工具调用历史
- 支持任务切换

---

## 实现细节

### 1. 消息通信模块

```python
# clawbot/multi_agent.py

class AgentMessenger:
    """多 Agent 消息通信"""
    
    def __init__(self, agent_id: str, root_dir: str = ".clawbot"):
        self.agent_id = agent_id
        self.root_dir = Path(root_dir)
        self.messages_dir = self.root_dir / "messages" / agent_id
        self.messages_dir.mkdir(parents=True, exist_ok=True)
        
    def send_message(self, to_agent: str, content: dict):
        """发送消息到指定 Agent"""
        target_dir = self.root_dir / "messages" / to_agent
        target_dir.mkdir(parents=True, exist_ok=True)
        
        msg = {
            "from": self.agent_id,
            "to": to_agent,
            "timestamp": datetime.utcnow().isoformat(),
            "content": content
        }
        
        msg_file = target_dir / f"msg-{uuid.uuid4()}.json"
        with open(msg_file, 'w') as f:
            json.dump(msg, f, indent=2)
            
    def receive_messages(self) -> List[dict]:
        """接收所有未读消息"""
        messages = []
        for msg_file in self.messages_dir.glob("msg-*.json"):
            with open(msg_file, 'r') as f:
                messages.append(json.load(f))
            msg_file.unlink()  # 读后删除
        return messages
        
    def broadcast(self, content: dict):
        """广播消息到所有 Agent"""
        agents_dir = self.root_dir / "agents"
        for agent_file in agents_dir.glob("agent-*.json"):
            agent_id = agent_file.stem
            if agent_id != self.agent_id:
                self.send_message(agent_id, content)
```

### 2. 任务锁机制

```python
class TaskLock:
    """防止多 Agent 并发修改同一任务"""
    
    def __init__(self, task_id: str, root_dir: str = ".clawbot"):
        self.task_id = task_id
        self.lock_file = Path(root_dir) / "locks" / f"{task_id}.lock"
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        
    def acquire(self, agent_id: str, timeout: int = 300) -> bool:
        """获取任务锁（5 分钟超时）"""
        if self.lock_file.exists():
            with open(self.lock_file, 'r') as f:
                lock_data = json.load(f)
            
            # 检查锁是否过期
            expires_at = datetime.fromisoformat(lock_data['expires_at'])
            if datetime.utcnow() < expires_at:
                return False  # 锁未过期，获取失败
                
        # 写入新锁
        lock_data = {
            "owner": agent_id,
            "acquired_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=timeout)).isoformat()
        }
        with open(self.lock_file, 'w') as f:
            json.dump(lock_data, f)
        return True
        
    def release(self):
        """释放锁"""
        if self.lock_file.exists():
            self.lock_file.unlink()
```

### 3. 集成到 LangGraph Agent

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from clawbot.multi_agent import AgentMessenger, TaskLock

def create_multi_agent(agent_id: str, provider: str, model: str):
    """创建支持多 Agent 通信的 Agent"""
    
    # 初始化消息通信
    messenger = AgentMessenger(agent_id)
    
    # 注册 Agent
    agent_file = Path(f".clawbot/agents/{agent_id}.json")
    agent_file.parent.mkdir(parents=True, exist_ok=True)
    with open(agent_file, 'w') as f:
        json.dump({
            "agent_id": agent_id,
            "provider": provider,
            "model": model,
            "started_at": datetime.utcnow().isoformat()
        }, f)
    
    # 创建 Agent（复用原有逻辑）
    agent = create_clawbot_agent(
        provider=provider,
        model=model,
        checkpoint_db=f".clawbot/checkpoints/{agent_id}.db"
    )
    
    # 包装 invoke 方法，支持消息接收
    original_invoke = agent.invoke
    
    def invoke_with_messaging(input_dict):
        # 检查是否有新消息
        messages = messenger.receive_messages()
        if messages:
            print(f"📨 收到 {len(messages)} 条消息:")
            for msg in messages:
                print(f"  - 来自 {msg['from']}: {msg['content']}")
            
            # 将消息添加到输入上下文
            input_dict["messages"] = messages
        
        # 执行原有逻辑
        result = original_invoke(input_dict)
        
        return result
    
    agent.invoke = invoke_with_messaging
    agent.messenger = messenger
    
    return agent
```

---

## 使用示例

### 启动多个终端

**终端 1（Agent A）**：
```bash
python -m clawbot.multi_agent_cli --agent-id agent-001 --provider openai --model gpt-4
```

**终端 2（Agent B）**：
```bash
python -m clawbot.multi_agent_cli --agent-id agent-002 --provider anthropic --model claude-3-opus
```

### 交互示例

**终端 1**：
```python
>>> agent.messenger.send_message("agent-002", {
    "type": "request",
    "action": "help_review",
    "content": "请帮我审查 phase2 的学习笔记"
})
```

**终端 2** 自动接收消息：
```
📨 收到 1 条消息:
  - 来自 agent-001: {'type': 'request', 'action': 'help_review', ...}

🤖 Agent B 正在处理请求...
```

---

## 实现优先级

1. **P0（立即实现）**：
   - [ ] 消息发送/接收
   - [ ] Agent 注册与发现
   - [ ] 基本的文件锁

2. **P1（本周）**：
   - [ ] 任务状态持久化
   - [ ] 跨会话恢复
   - [ ] 广播消息

3. **P2（下周）**：
   - [ ] 消息优先级队列
   - [ ] 任务协作流程
   - [ ] Web 可视化界面

---

## 对比 DevCodex

| 特性 | DevCodex | ClawBot Multi-Agent |
|------|----------|---------------------|
| 语言 | Node.js | Python |
| 消息队列 | 文件系统 | 文件系统 |
| 并发控制 | fenced-task-write-owner | TaskLock（Python） |
| 任务恢复 | context-delivery-ledger | JSON + LangGraph checkpoint |
| 宿主依赖 | Copilot/Claude Code | 独立运行 |
| Skills | 80+ 代码工程 | 3 学习专用 |
| 适用场景 | 生产环境代码开发 | 学习框架 |

---

## 下一步

你想要我：

1. **立即实现方案 B 的 P0 功能**（消息通信 + Agent 注册）？
2. **先做一个简单原型演示**（2 个终端互发消息）？
3. **详细设计某个模块**（比如任务锁机制）？
4. **先看看 DevCodex 的某个具体实现**（比如 lifecycle.cjs）？

告诉我你的选择，我马上开始！
