# ClawBot

ClawBot 是一个 **可迁移、跨模型的 AI Harness 学习框架**，基于 LangGraph 实现真正的 Skills 通用化。

在线学习站：<https://lpzams.github.io/ClawBot/>

## 🎯 核心特性

- ✅ **跨模型支持**：OpenAI、Claude、DeepSeek、Ollama 等任意 LLM
- ✅ **Skills 通用化**：基于 LangChain Tools，任何模型都能调用
- ✅ **状态持久化**：LangGraph checkpointer，关机不丢数据
- ✅ **完全可迁移**：3 个文件即可迁移到新项目
- ✅ **学习导向**：从零理解 Harness 核心机制，而非直接套用框架
- ✅ **多 Agent 协作**：借鉴 DevCodex 设计，支持多终端同时运行并互相通信

我们从一条可测试的执行链开始：

```text
用户输入 -> 模型请求 -> 工具调用 -> 工具结果 -> 模型回答 -> 事件记录
```

既能理解模型 API，也能在面试中讲清楚 Harness 为什么需要状态、循环、安全边界、可观测性和评测。

## 当前状态

项目处于 **Phase 2：可复用核心与模型适配器**，已完成 **LangGraph 跨模型框架重构** 和 **Multi-Agent 协作系统**。

- [x] 初始化本地 Git 仓库，默认分支为 `main`
- [x] 定义最小产品范围和学习路线
- [x] 编写 GitHub 与 worktree 实操手册
- [x] 创建第一个功能 worktree
- [x] 实现不依赖真实模型的最小 Harness 执行链
- [x] 把核心执行器封装为可复用 `Harness`
- [x] 增加无第三方运行时依赖的 OpenAI-compatible adapter
- [x] 增加 Jenkins Pipeline：测试、冒烟检查、打包和交付归档
- [x] **重构为 LangGraph 框架：Skills 通用化、跨模型支持**
- [x] **Multi-Agent 协作系统（借鉴 DevCodex 设计）**
- [ ] Phase 3：智能上下文管理（语义检索记忆）
- [ ] 用真实 API 做一次手工集成验证

## 文档

1. [先读：ClawBot 到底是什么](docs/00-what-is-clawbot.md)
2. [学习与开发路线](docs/00-learning-roadmap.md)
3. [Git、GitHub 与 worktree](docs/01-git-github-worktree.md)
4. [ClawBot 最小产品定义](docs/02-mvp-definition.md)
5. [开发日志](docs/03-development-log.md)
6. [Phase 1：最小执行链](docs/04-phase-1-minimal-loop.md)
7. [可复用框架接入指南](docs/06-reusable-framework.md)
8. [发布到 GitHub Pages](docs/05-publishing-github-pages.md)
9. [Jenkins CI/CD 实操](docs/07-jenkins-ci-cd.md)
10. **[DevCodex 集成方案](docs/08-devcodex-integration-plan.md)**
11. **[Multi-Agent 协作系统](docs/09-multi-agent-system.md)**

## 技术选择

- Python 3.9+（推荐 3.11+）
- **LangChain + LangGraph**：跨模型 Agent 框架
- **ChromaDB**：语义检索记忆（Phase 3）
- CLI 优先
- 标准库优先
- 先用 Fake Model 写测试，再接真实模型 API
- 暂不引入多 Agent、复杂 RAG（等核心执行链跑通后再扩展）

## 框架架构

```
ClawBot/
├── clawbot/
│   ├── agent.py           # 原有 Harness（Phase 1-2）
│   ├── models.py          # 模型适配器
│   ├── skills.py          # LangChain Skills（通用化）
│   └── memory.py          # 智能上下文管理（Phase 3）
├── langgraph_agent.py     # LangGraph Agent 入口
├── learning/
│   ├── state.json         # 学习状态（人类可读）
│   ├── checkpoints.db     # LangGraph 状态（自动管理）
│   ├── curriculum/        # 课程内容
│   └── workbooks/         # 学习笔记
├── tests/                 # 单元测试
└── Jenkinsfile            # CI/CD 配置
```

## 作为框架使用

安装当前仓库后，其他 Python 项目即可复用同一个包：

```powershell
python -m pip install -e .
```

业务项目只需要提供一个 `messages -> string` 的模型函数：

```python
from clawbot import Harness

harness = Harness(my_model, system_prompt="回答要简洁、可执行")
answer = harness.run("分析这份报告")
```

CLI、Web 接口和定时任务都可以调用同一个 `Harness`；供应商 SDK 或 HTTP 只放在模型 adapter 中。完整的跨项目接入示例见[可复用框架接入指南](docs/06-reusable-framework.md)。

## 快速开始

### 方式 1：使用 LangGraph Agent（推荐）

```bash
# 1. 安装依赖
pip install -e .

# 2. 设置 API Key
export OPENAI_API_KEY="sk-..."

# 3. 运行
python langgraph_agent.py openai gpt-4 "继续学习"
```

### 方式 2：Multi-Agent 协作（新功能）

**终端 1**：
```bash
python -m clawbot.multi_agent_cli --agent-id agent-alice
```

**终端 2**：
```bash
python -m clawbot.multi_agent_cli --agent-id agent-bob
```

**运行演示**：
```bash
# 快速演示
python demo_quick.py

# 单元测试
python test_multi_agent.py
```

详细使用指南：[Multi-Agent 协作系统](docs/09-multi-agent-system.md)

### 方式 3：跨模型切换

```bash
# 今天用 OpenAI
python langgraph_agent.py openai gpt-4 "开始学习 phase2-adapter"

# 明天用 Claude（状态自动继承）
python langgraph_agent.py anthropic claude-3-opus-20240229 "继续学习"

# 后天用本地模型
python langgraph_agent.py ollama deepseek-coder "总结我学了什么"
```

### 方式 3：传统 CLI（原有功能）

```bash
python -m unittest discover -s tests -v
python -m clawbot "hello harness"
python -m clawbot --provider openai "hello harness"
```

详细使用指南：[LANGGRAPH_GUIDE.md](LANGGRAPH_GUIDE.md)
