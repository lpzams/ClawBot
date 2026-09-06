# LangGraph Agent 使用指南

## ✅ 已完成的改造

ClawBot 现在是一个**真正可迁移、跨模型的 AI Harness 学习框架**！

### 核心改进

1. **Skills 通用化**（`clawbot/skills.py`）
   - 基于 LangChain `BaseTool`
   - 任何支持工具调用的 LLM 都能使用
   - OpenAI、Claude、DeepSeek 等全部支持

2. **Agent 框架**（`langgraph_agent.py`）
   - 支持 OpenAI、Anthropic、Ollama
   - 状态自动持久化（SQLite）
   - 跨会话记忆（关机不丢数据）

3. **完全可迁移**
   - 复制 3 个文件即可用在新项目
   - 不依赖特定工具（Claude Code）

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

这会安装：
- `langchain` - LLM 框架
- `langgraph` - 状态管理
- `langchain-openai` - OpenAI 支持
- `langchain-anthropic` - Claude 支持
- `chromadb` - 向量记忆（Phase 3 会用到）

### 2. 设置 API Key

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# 本地模型不需要 API Key
```

### 3. 使用不同模型

#### OpenAI GPT-4

```bash
python langgraph_agent.py openai gpt-4 "继续学习"
```

#### Anthropic Claude

```bash
python langgraph_agent.py anthropic claude-3-opus-20240229 "查看进度"
```

#### 本地 Ollama（DeepSeek）

```bash
# 先启动 Ollama
ollama serve

# 拉取模型
ollama pull deepseek-coder

# 使用
python langgraph_agent.py ollama deepseek-coder "做练习 01-fake-model-test"
```

---

## 🔄 跨模型切换演示

```bash
# 第 1 天：用 OpenAI 学习
python langgraph_agent.py openai gpt-4 "开始学习 phase2-adapter"
# 状态保存到 learning/checkpoints.db

# 第 2 天：切换到 Claude
python langgraph_agent.py anthropic claude-3-opus-20240229 "继续学习"
# ✅ Claude 能看到昨天 OpenAI 的学习记录！

# 第 3 天：用本地模型
python langgraph_agent.py ollama deepseek-coder "总结我学了什么"
# ✅ DeepSeek 也能看到完整历史！
```

---

## 📦 可用的 Skills

### 1. `learn` - 教学 Skill

```python
from langgraph_agent import create_clawbot_agent

agent = create_clawbot_agent("openai", "gpt-4")

# 查看进度
agent.invoke({"input": "查看学习进度"})

# 继续当前 Phase
agent.invoke({"input": "继续学习"})

# 开始新 Phase
agent.invoke({"input": "开始学习 phase3-smart-context"})
```

### 2. `practice` - 练习 Skill

```python
# 查看练习说明
agent.invoke({"input": "查看练习 01-fake-model-test 的说明"})

# 运行验证
agent.invoke({"input": "运行练习 01-fake-model-test"})

# 查看参考答案
agent.invoke({"input": "查看练习 01-fake-model-test 的答案"})
```

### 3. `interview_prep` - 面试准备 Skill

```python
# 准备特定 Phase 的面试
agent.invoke({"input": "准备 phase1-minimal-loop 的面试"})

# 全面准备
agent.invoke({"input": "全面准备面试"})
```

---

## 🎯 迁移到新项目

### 方式 1：Python API

```python
from langgraph_agent import migrate_to_new_project

migrate_to_new_project(
    source_dir="./ClawBot",
    target_dir="./MyNewAIProject"
)
```

### 方式 2：手动复制

```bash
# 1. 复制核心文件
cp -r ClawBot/learning MyProject/learning
cp ClawBot/clawbot/skills.py MyProject/clawbot/skills.py
cp ClawBot/langgraph_agent.py MyProject/langgraph_agent.py

# 2. 重置状态
cd MyProject
# 编辑 learning/state.json，设置 current_phase = null

# 3. 调整课程内容
# 修改 learning/curriculum/ 中的案例和代码引用

# 4. 开始使用
python langgraph_agent.py openai gpt-4 "开始学习"
```

---

## 🔧 Python API 使用

```python
from langgraph_agent import create_clawbot_agent

# 创建 Agent
agent = create_clawbot_agent(
    provider="openai",
    model="gpt-4",
    project_root=".",  # 项目根目录
    checkpoint_db="learning/checkpoints.db",  # 状态数据库
    temperature=0.0
)

# 使用
result = agent.invoke({
    "input": "继续学习 Phase 2"
})

print(result["output"])
```

---

## 📊 状态持久化机制

### 两层状态管理

1. **轻量状态**（`learning/state.json`）
   - 人类可读的 JSON
   - 记录当前 Phase、完成情况
   - 任何工具都能读写

2. **Agent 状态**（`learning/checkpoints.db`）
   - LangGraph 管理的 SQLite 数据库
   - 保存完整对话历史
   - 支持跨会话恢复

### 切换模型时发生了什么？

```python
# OpenAI 学了 10 轮
agent_openai = create_clawbot_agent("openai", "gpt-4")
for i in range(10):
    agent_openai.invoke({"input": f"问题 {i}"})
# checkpoints.db 保存了 10 轮对话

# 切换到 Claude
agent_claude = create_clawbot_agent("anthropic", "claude-3-opus")
agent_claude.invoke({"input": "总结之前的内容"})
# ✅ Claude 从 checkpoints.db 加载了 OpenAI 的 10 轮对话！
```

---

## 🆚 对比：改造前 vs 改造后

| 特性 | 改造前（Claude Code Skills） | 改造后（LangGraph） |
|------|---------------------------|------------------|
| **跨模型支持** | ❌ 只支持 Claude | ✅ OpenAI/Claude/Ollama/任意 LLM |
| **状态管理** | ⚠️ 手动 JSON | ✅ 自动持久化（SQLite） |
| **可迁移性** | ⚠️ 依赖 Claude Code | ✅ 完全独立，3 个文件即可 |
| **工具调用** | ✅ Claude 专属 | ✅ 标准 LangChain Tools |
| **对话历史** | ❌ 无 | ✅ 跨会话记忆 |
| **实现复杂度** | ⭐ 简单 | ⭐⭐ 中等 |
| **生态** | Claude 生态 | LangChain 生态 |

---

## 🎓 学习路径建议

### Phase 1-2（已完成）
- 最小执行链
- 适配器模式
- 使用原有的 learning 框架

### Phase 3（下一步）
- 智能上下文管理
- 集成 ChromaDB
- 使用新的 LangGraph Agent

```bash
# 用 LangGraph Agent 开始 Phase 3
python langgraph_agent.py openai gpt-4 "开始学习 phase3-smart-context"
```

---

## ⚠️ 注意事项

### 1. Ollama 模型限制

本地模型（如 DeepSeek）不支持原生工具调用，使用 ReAct 模式：
- 速度稍慢（需要多轮推理）
- 准确性稍低（可能解析错误）
- 适合学习和测试，不适合生产

### 2. API Key 管理

```bash
# 不要把 Key 写进代码！
# 使用环境变量
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. 状态文件位置

```
project_root/
├── learning/
│   ├── state.json            # 轻量状态
│   ├── checkpoints.db        # Agent 状态（自动创建）
│   ├── curriculum/
│   └── workbooks/
```

---

## 🐛 故障排除

### 问题 1：Skills 调用失败

```bash
# 检查项目结构
ls learning/state.json
ls learning/curriculum/

# 确认在项目根目录
pwd
```

### 问题 2：API Key 错误

```bash
# 检查环境变量
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# 重新设置
export OPENAI_API_KEY="sk-..."
```

### 问题 3：Ollama 连接失败

```bash
# 启动 Ollama 服务
ollama serve

# 检查模型是否存在
ollama list

# 拉取模型
ollama pull deepseek-coder
```

---

## 📚 下一步

1. **完成 Phase 1-2 学习**
   ```bash
   python langgraph_agent.py openai gpt-4 "继续学习"
   ```

2. **添加 Phase 3 内容**
   - 智能上下文管理
   - ChromaDB 集成
   - 语义检索

3. **迁移到实际项目**
   ```python
   migrate_to_new_project("./ClawBot", "./MyRealProject")
   ```

4. **准备面试**
   ```bash
   python langgraph_agent.py openai gpt-4 "全面准备面试"
   ```

---

## 🎉 总结

ClawBot 现在是：
- ✅ 真正跨模型的框架
- ✅ 完全可迁移（3 个文件）
- ✅ Skills 通用（任何 LLM 都能用）
- ✅ 状态自动管理（跨会话记忆）
- ✅ 工业级实现（LangGraph）

**立即开始：**
```bash
pip install -e .
python langgraph_agent.py openai gpt-4 "继续学习"
```
