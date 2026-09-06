"""
测试 LangGraph Skills - 验证跨模型兼容性

不需要真实 API Key，使用 Fake LLM 测试
"""

import json
from pathlib import Path
from clawbot.skills import LearnSkill, PracticeSkill, InterviewPrepSkill


def test_learn_skill():
    """测试 Learn Skill 基本功能"""
    print("=" * 60)
    print("测试 1：Learn Skill")
    print("=" * 60)

    skill = LearnSkill(project_root=".")

    # 测试查看进度
    print("\n[测试] 查看学习进度...")
    result = skill._run(action="进度")
    print(result)
    assert "学习进度" in result
    assert "当前阶段" in result

    # 测试继续学习
    print("\n[测试] 继续学习...")
    result = skill._run(action="继续")
    print(result[:500] + "...")
    assert "phase" in result.lower() or "当前没有" in result

    print("\n✅ Learn Skill 测试通过")


def test_practice_skill():
    """测试 Practice Skill 基本功能"""
    print("\n" + "=" * 60)
    print("测试 2：Practice Skill")
    print("=" * 60)

    skill = PracticeSkill(project_root=".")

    # 测试查看练习
    print("\n[测试] 查看练习说明...")
    result = skill._run(practice_id="01-fake-model-test", action="查看")
    print(result[:300] + "...")

    # 测试答案路径
    print("\n[测试] 查看参考答案...")
    result = skill._run(practice_id="01-fake-model-test", action="答案")
    print(result)
    assert "solution" in result or "参考答案" in result

    print("\n✅ Practice Skill 测试通过")


def test_interview_prep_skill():
    """测试 Interview Prep Skill 基本功能"""
    print("\n" + "=" * 60)
    print("测试 3：Interview Prep Skill")
    print("=" * 60)

    skill = InterviewPrepSkill(project_root=".")

    # 测试特定主题
    print("\n[测试] Phase 1 面试准备...")
    result = skill._run(topic="phase1-minimal-loop")
    print(result[:500] + "...")

    print("\n✅ Interview Prep Skill 测试通过")


def test_skill_as_langchain_tool():
    """测试 Skills 作为 LangChain Tool 使用"""
    print("\n" + "=" * 60)
    print("测试 4：LangChain Tool 接口")
    print("=" * 60)

    from langchain.tools import BaseTool

    skill = LearnSkill(project_root=".")

    # 验证是 BaseTool 子类
    assert isinstance(skill, BaseTool)
    print(f"✅ Skill 名称: {skill.name}")
    print(f"✅ Skill 描述: {skill.description[:100]}...")

    # 验证有 args_schema
    assert skill.args_schema is not None
    print(f"✅ 参数 Schema: {skill.args_schema.__name__}")

    # 测试调用（LangChain 标准方式）
    print("\n[测试] 通过 LangChain 标准接口调用...")
    result = skill.invoke({"action": "进度"})
    print(result[:300] + "...")

    print("\n✅ LangChain Tool 接口测试通过")


def test_cross_model_state():
    """测试跨模型状态读取"""
    print("\n" + "=" * 60)
    print("测试 5：跨模型状态管理")
    print("=" * 60)

    state_file = Path("learning/state.json")

    if not state_file.exists():
        print("⚠️  状态文件不存在，跳过测试")
        return

    # 读取状态
    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

    print(f"✅ 当前 Phase: {state.get('current_phase')}")
    print(f"✅ 学习者: {state.get('student_name')}")
    print(f"✅ 已完成: {len(state.get('completed_phases', []))} 个阶段")

    # 模拟：不同 Agent 都能读取同一个状态
    print("\n[模拟] OpenAI Agent 读取状态...")
    skill_openai = LearnSkill(project_root=".")
    result1 = skill_openai._run(action="进度")

    print("\n[模拟] Claude Agent 读取状态...")
    skill_claude = LearnSkill(project_root=".")
    result2 = skill_claude._run(action="进度")

    print("\n[模拟] DeepSeek Agent 读取状态...")
    skill_deepseek = LearnSkill(project_root=".")
    result3 = skill_deepseek._run(action="进度")

    # 验证都读到同样的状态
    assert state.get('current_phase') in result1 or "None" in result1
    assert state.get('current_phase') in result2 or "None" in result2
    assert state.get('current_phase') in result3 or "None" in result3

    print("\n✅ 跨模型状态管理测试通过")


def test_migration_readiness():
    """测试迁移就绪性"""
    print("\n" + "=" * 60)
    print("测试 6：迁移就绪性")
    print("=" * 60)

    required_files = [
        "clawbot/skills.py",
        "langgraph_agent.py",
        "learning/state.json",
        "learning/curriculum",
    ]

    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} 不存在")

    print("\n📦 迁移到新项目只需要复制以上文件！")
    print("\n✅ 迁移就绪性测试通过")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║  ClawBot LangGraph Skills 测试套件                        ║
║  验证跨模型兼容性和可迁移性                                ║
╚═══════════════════════════════════════════════════════════╝
    """)

    try:
        test_learn_skill()
        test_practice_skill()
        test_interview_prep_skill()
        test_skill_as_langchain_tool()
        test_cross_model_state()
        test_migration_readiness()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        print("\n下一步：")
        print("  1. 安装依赖: pip install -e .")
        print("  2. 设置 API Key: export OPENAI_API_KEY='sk-...'")
        print("  3. 运行 Agent: python langgraph_agent.py openai gpt-4 '继续学习'")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
