"""
LangGraph Agent - 可迁移的跨模型 Agent 框架

特性：
1. 支持任意 LLM（OpenAI/Claude/DeepSeek/Ollama）
2. 状态持久化（SQLite checkpointer）
3. Skills 自动注册（learn/practice/interview_prep）
4. 完全可迁移到其他项目

使用方法：
    # 创建 OpenAI Agent
    agent = create_clawbot_agent(provider="openai", model="gpt-4")
    result = agent.invoke({"input": "继续学习"})

    # 切换到 Claude（状态自动继承）
    agent = create_clawbot_agent(provider="anthropic", model="claude-3-opus-20240229")
    result = agent.invoke({"input": "总结刚才学的内容"})

    # 本地模型
    agent = create_clawbot_agent(provider="ollama", model="deepseek-coder")
    result = agent.invoke({"input": "做练习 1"})
"""

from typing import Literal, Optional
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.sqlite import SqliteSaver

from clawbot.skills import LearnSkill, PracticeSkill, InterviewPrepSkill


# 系统提示词模板
SYSTEM_PROMPT = """你是 ClawBot 学习助手，帮助用户深入理解 AI Harness 开发。

你有以下工具可用：
- learn: 教学工具，提供结构化课程内容
- practice: 练习工具，指导动手编码练习
- interview_prep: 面试准备工具，生成简历和话术

工作原则：
1. 主动使用工具获取信息，不要凭记忆回答
2. 学习状态存储在 learning/state.json 中
3. 课程内容在 learning/curriculum/ 中
4. 始终基于文件内容回答，不要编造

当用户说"继续学习"、"查看进度"、"做练习"时，立即调用对应的工具。
"""


def create_clawbot_agent(
    provider: Literal["openai", "anthropic", "ollama"] = "openai",
    model: str = "gpt-4o-mini",
    project_root: str = ".",
    checkpoint_db: str = "learning/checkpoints.db",
    temperature: float = 0.0,
    **llm_kwargs
) -> AgentExecutor:
    """创建 ClawBot Agent（支持跨模型切换）

    Args:
        provider: 模型提供商
            - "openai": OpenAI GPT 系列
            - "anthropic": Anthropic Claude 系列
            - "ollama": 本地 Ollama 模型
        model: 模型名称
            - OpenAI: "gpt-4", "gpt-4o-mini", "gpt-3.5-turbo"
            - Anthropic: "claude-3-opus-20240229", "claude-3-sonnet-20240229"
            - Ollama: "deepseek-coder", "llama3", "mistral"
        project_root: 项目根目录（可迁移）
        checkpoint_db: 状态持久化数据库路径
        temperature: 模型温度
        **llm_kwargs: 传递给 LLM 的额外参数

    Returns:
        AgentExecutor 实例

    示例：
        >>> # OpenAI
        >>> agent = create_clawbot_agent("openai", "gpt-4")
        >>> agent.invoke({"input": "继续学习"})

        >>> # Claude
        >>> agent = create_clawbot_agent("anthropic", "claude-3-opus-20240229")
        >>> agent.invoke({"input": "查看进度"})

        >>> # 本地模型
        >>> agent = create_clawbot_agent("ollama", "deepseek-coder")
        >>> agent.invoke({"input": "做练习 01-fake-model-test"})
    """

    # 1. 选择 LLM
    if provider == "openai":
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            **llm_kwargs
        )
    elif provider == "anthropic":
        llm = ChatAnthropic(
            model=model,
            temperature=temperature,
            **llm_kwargs
        )
    elif provider == "ollama":
        from langchain_community.llms import Ollama
        # Ollama 需要特殊处理（不支持原生 tool calling）
        from langchain.agents import create_react_agent
        from langchain.prompts import PromptTemplate

        llm = Ollama(model=model, temperature=temperature)

        # 使用 ReAct 模式（因为 Ollama 不支持原生工具调用）
        tools = [
            LearnSkill(project_root=project_root),
            PracticeSkill(project_root=project_root),
            InterviewPrepSkill(project_root=project_root),
        ]

        prompt = PromptTemplate.from_template(
            SYSTEM_PROMPT + "\n\n{tools}\n\n{tool_names}\n\n"
            "User: {input}\n{agent_scratchpad}"
        )

        agent = create_react_agent(llm, tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
        )
    else:
        raise ValueError(f"不支持的 provider: {provider}")

    # 2. 初始化 Skills（Tools）
    tools = [
        LearnSkill(project_root=project_root),
        PracticeSkill(project_root=project_root),
        InterviewPrepSkill(project_root=project_root),
    ]

    # 3. 创建 Prompt 模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 4. 创建 Agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # 5. 状态持久化（关键！）
    checkpoint_path = Path(project_root) / checkpoint_db
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    memory = SqliteSaver.from_conn_string(str(checkpoint_path))

    # 6. 创建 Executor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        memory=memory,  # 跨会话记忆
        max_iterations=10,
    )

    return executor


def migrate_to_new_project(source_dir: str, target_dir: str):
    """迁移框架到新项目

    Args:
        source_dir: ClawBot 项目根目录
        target_dir: 目标项目根目录

    复制的内容：
        - learning/ 目录（课程、状态、练习）
        - clawbot/skills.py（Skills 定义）
        - langgraph_agent.py（Agent 创建函数）

    使用方法：
        >>> migrate_to_new_project("./ClawBot", "./MyNewProject")
        >>> # 在新项目中
        >>> from langgraph_agent import create_clawbot_agent
        >>> agent = create_clawbot_agent("openai", "gpt-4", project_root=".")
    """
    import shutil

    source = Path(source_dir)
    target = Path(target_dir)

    # 1. 复制 learning 框架
    shutil.copytree(
        source / "learning",
        target / "learning",
        dirs_exist_ok=True
    )

    # 2. 复制 skills 定义
    target_skills = target / "clawbot"
    target_skills.mkdir(parents=True, exist_ok=True)
    shutil.copy(source / "clawbot" / "skills.py", target_skills / "skills.py")

    # 3. 复制 agent 入口
    shutil.copy(source / "langgraph_agent.py", target / "langgraph_agent.py")

    # 4. 重置状态
    state_file = target / "learning" / "state.json"
    import json
    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

    state['current_phase'] = None
    state['completed_phases'] = []
    state['student_name'] = "New Student"

    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"✅ 框架已迁移到：{target}")
    print(f"\n使用方法：")
    print(f"  cd {target}")
    print(f"  python langgraph_agent.py")


# CLI 入口
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python langgraph_agent.py <provider> <model> <prompt>")
        print("\n示例：")
        print("  python langgraph_agent.py openai gpt-4 '继续学习'")
        print("  python langgraph_agent.py anthropic claude-3-opus-20240229 '查看进度'")
        print("  python langgraph_agent.py ollama deepseek-coder '做练习 01'")
        sys.exit(1)

    provider = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "gpt-4o-mini"
    prompt = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "继续学习"

    # 创建 Agent
    print(f"🤖 创建 {provider} Agent（模型：{model}）...")
    agent = create_clawbot_agent(provider=provider, model=model)

    # 执行
    print(f"\n📝 用户输入：{prompt}\n")
    result = agent.invoke({"input": prompt})

    print(f"\n✅ 回复：\n{result['output']}")
