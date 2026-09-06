"""
LangChain Skills - 可迁移的通用 Skills 实现

这些 Skills 可以被任何支持 LangChain 的 Agent 调用：
- OpenAI GPT-4
- Anthropic Claude
- DeepSeek
- 本地 Ollama 模型
- 任何其他 LLM

核心设计原则：
1. 状态文件驱动（learning/state.json）
2. 跨模型兼容
3. 可独立迁移到其他项目
"""

import json
from pathlib import Path
from typing import Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class LearnSkillInput(BaseModel):
    """Learn Skill 输入参数"""
    action: str = Field(
        description="动作类型：'继续'（继续当前Phase）、'开始'（开始新Phase）、'进度'（查看学习进度）"
    )
    phase: Optional[str] = Field(
        default=None,
        description="可选：Phase 名称，如 'phase1-minimal-loop'，仅在 action='开始' 时需要"
    )


class LearnSkill(BaseTool):
    """教学 Skill - 渐进式学习模式

    功能：
    - 读取学习状态（learning/state.json）
    - 加载课程内容（learning/curriculum/）
    - 提供互动式教学
    - 支持多模型切换
    """

    name: str = "learn"
    description: str = (
        "教学助手工具，用于结构化学习 ClawBot 项目。"
        "支持继续学习、开始新阶段、查看进度。"
        "示例：learn(action='继续') 或 learn(action='开始', phase='phase3-smart-context')"
    )
    args_schema: Type[BaseModel] = LearnSkillInput

    project_root: Path = Field(default_factory=lambda: Path("."))

    def __init__(self, project_root: str = "."):
        """初始化 Skill

        Args:
            project_root: 项目根目录（可迁移到其他项目）
        """
        super().__init__()
        self.project_root = Path(project_root)

    def _run(self, action: str, phase: Optional[str] = None) -> str:
        """执行教学逻辑

        Args:
            action: 动作类型
            phase: 可选的 Phase 名称

        Returns:
            教学内容或状态信息
        """
        state_file = self.project_root / "learning" / "state.json"

        # 读取状态
        if not state_file.exists():
            return (
                "❌ 学习状态文件不存在。\n"
                "请确保在项目根目录，并且已初始化 learning/ 框架。"
            )

        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)

        # 根据 action 执行不同逻辑
        if action == "进度":
            return self._show_progress(state)

        elif action == "继续":
            return self._continue_learning(state)

        elif action == "开始":
            if not phase:
                return "❌ 开始新 Phase 需要指定 phase 参数，如：learn(action='开始', phase='phase3-smart-context')"
            return self._start_phase(state, phase)

        else:
            return f"❌ 未知动作：{action}，支持的动作：'继续'、'开始'、'进度'"

    def _show_progress(self, state: dict) -> str:
        """显示学习进度"""
        output = ["## 📊 学习进度\n"]
        output.append(f"**学习者**：{state.get('student_name', 'Unknown')}")
        output.append(f"**当前阶段**：{state.get('current_phase', 'None')}")
        output.append(f"\n**已完成阶段**：")

        for completed in state.get('completed_phases', []):
            output.append(f"  - {completed['phase']} (完成于 {completed['completed_date']})")

        output.append(f"\n**面试准备度**：")
        readiness = state.get('interview_readiness', {})
        output.append(f"  - 已准备好：{', '.join(readiness.get('ready_topics', []))}")
        output.append(f"  - 练习中：{', '.join(readiness.get('practicing_topics', []))}")

        output.append(f"\n**学习过的企业案例**：")
        for case in state.get('enterprise_cases_studied', []):
            output.append(f"  - {case}")

        return "\n".join(output)

    def _continue_learning(self, state: dict) -> str:
        """继续当前 Phase"""
        current_phase = state.get('current_phase')

        if not current_phase:
            return (
                "❌ 当前没有正在学习的 Phase。\n"
                "使用 learn(action='开始', phase='phase1-minimal-loop') 开始学习。"
            )

        # 加载课程内容
        curriculum_dir = self.project_root / "learning" / "curriculum" / current_phase

        if not curriculum_dir.exists():
            return f"❌ 课程目录不存在：{curriculum_dir}"

        # 读取核心概念
        concepts_file = curriculum_dir / "核心概念.md"
        enterprise_file = list(curriculum_dir.glob("企业案例-*.md"))
        interview_file = curriculum_dir / "面试问答.md"

        output = [f"## 📚 继续学习：{current_phase}\n"]

        # 读取核心概念
        if concepts_file.exists():
            with open(concepts_file, 'r', encoding='utf-8') as f:
                concepts = f.read()
            output.append("### 核心概念\n")
            output.append(concepts[:1000] + "...\n（内容较长，已截断）")

        # 读取企业案例
        if enterprise_file:
            with open(enterprise_file[0], 'r', encoding='utf-8') as f:
                enterprise = f.read()
            output.append(f"\n### 🏢 企业案例\n")
            output.append(enterprise[:500] + "...\n（内容较长，已截断）")

        # 提示下一步
        workbook = state.get('current_workbook', f'learning/workbooks/{current_phase}.md')
        output.append(f"\n### ✅ 下一步\n")
        output.append(f"1. 完整阅读课程内容：`cat {concepts_file}`")
        output.append(f"2. 记录你的理解到：`{workbook}`")
        output.append(f"3. 完成动手练习：`learn(action='练习')`")
        output.append(f"4. 查看面试问答：`cat {interview_file}`")

        return "\n".join(output)

    def _start_phase(self, state: dict, phase: str) -> str:
        """开始新的 Phase"""
        curriculum_dir = self.project_root / "learning" / "curriculum" / phase

        if not curriculum_dir.exists():
            available = [p.name for p in (self.project_root / "learning" / "curriculum").iterdir() if p.is_dir()]
            return (
                f"❌ Phase '{phase}' 不存在。\n"
                f"可用的 Phase：{', '.join(available)}"
            )

        # 更新状态
        state['current_phase'] = phase
        state['current_workbook'] = f"learning/workbooks/{phase}-学习笔记.md"

        state_file = self.project_root / "learning" / "state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        return (
            f"✅ 已开始学习：{phase}\n\n"
            f"使用 learn(action='继续') 查看课程内容。"
        )


class PracticeSkillInput(BaseModel):
    """Practice Skill 输入参数"""
    practice_id: str = Field(
        description="练习 ID，如 '01-fake-model-test' 或 '02-adapter-pattern'"
    )
    action: str = Field(
        default="运行",
        description="动作：'运行'（运行验证）、'查看'（查看说明）、'答案'（查看参考答案）"
    )


class PracticeSkill(BaseTool):
    """练习 Skill - 动手编码练习"""

    name: str = "practice"
    description: str = (
        "动手练习工具，用于完成编码练习并自动验证。"
        "示例：practice(practice_id='01-fake-model-test', action='运行')"
    )
    args_schema: Type[BaseModel] = PracticeSkillInput

    project_root: Path = Field(default_factory=lambda: Path("."))

    def __init__(self, project_root: str = "."):
        super().__init__()
        self.project_root = Path(project_root)

    def _run(self, practice_id: str, action: str = "运行") -> str:
        """执行练习逻辑"""
        practice_dir = self.project_root / "learning" / "practice" / practice_id

        if not practice_dir.exists():
            available = [p.name for p in (self.project_root / "learning" / "practice").iterdir() if p.is_dir()]
            return (
                f"❌ 练习 '{practice_id}' 不存在。\n"
                f"可用的练习：{', '.join(available)}"
            )

        if action == "查看":
            readme = practice_dir / "练习说明.md"
            if readme.exists():
                with open(readme, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"❌ 练习说明不存在：{readme}"

        elif action == "答案":
            solution_dir = practice_dir / "solution"
            if solution_dir.exists():
                files = list(solution_dir.glob("*.py"))
                return (
                    f"📁 参考答案位置：{solution_dir}\n\n"
                    f"文件列表：\n" + "\n".join(f"  - {f.name}" for f in files)
                )
            else:
                return "❌ 参考答案目录不存在"

        elif action == "运行":
            verify_script = practice_dir / "verify.py"
            if not verify_script.exists():
                return f"❌ 验证脚本不存在：{verify_script}"

            # 提示用户在终端运行
            return (
                f"请在终端运行验证脚本：\n\n"
                f"  cd {practice_dir}\n"
                f"  python verify.py\n\n"
                f"（自动验证需要在终端执行，Skill 无法直接运行）"
            )

        else:
            return f"❌ 未知动作：{action}，支持：'查看'、'运行'、'答案'"


class InterviewPrepSkillInput(BaseModel):
    """Interview Prep Skill 输入参数"""
    topic: str = Field(
        description="准备的主题，如 'phase1-minimal-loop' 或 '全面准备'"
    )


class InterviewPrepSkill(BaseTool):
    """面试准备 Skill"""

    name: str = "interview_prep"
    description: str = (
        "面试准备工具，生成简历描述、项目话术、技术问答。"
        "示例：interview_prep(topic='phase1-minimal-loop')"
    )
    args_schema: Type[BaseModel] = InterviewPrepSkillInput

    project_root: Path = Field(default_factory=lambda: Path("."))

    def __init__(self, project_root: str = "."):
        super().__init__()
        self.project_root = Path(project_root)

    def _run(self, topic: str) -> str:
        """生成面试准备材料"""
        if topic == "全面准备":
            return self._generate_full_prep()

        # 读取特定 Phase 的面试问答
        interview_file = self.project_root / "learning" / "curriculum" / topic / "面试问答.md"

        if not interview_file.exists():
            return f"❌ 面试问答文件不存在：{interview_file}"

        with open(interview_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return f"## 📝 {topic} 面试准备\n\n{content}"

    def _generate_full_prep(self) -> str:
        """生成完整面试准备"""
        output = ["## 📝 完整面试准备\n"]

        curriculum_dir = self.project_root / "learning" / "curriculum"

        for phase_dir in sorted(curriculum_dir.iterdir()):
            if not phase_dir.is_dir():
                continue

            interview_file = phase_dir / "面试问答.md"
            if interview_file.exists():
                output.append(f"\n### {phase_dir.name}\n")
                with open(interview_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                output.append(content[:500] + "...\n（已截断）")

        return "\n".join(output)


# 导出所有 Skills
__all__ = ['LearnSkill', 'PracticeSkill', 'InterviewPrepSkill']
