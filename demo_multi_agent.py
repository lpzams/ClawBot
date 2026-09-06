"""
Multi-Agent 演示脚本

演示场景：两个 Agent 协作完成学习任务
- Agent A：学习 Phase 2
- Agent B：审查学习笔记并提供反馈
"""

import time
import json
from pathlib import Path
from clawbot.multi_agent_core import AgentMessenger


def demo_basic_messaging():
    """演示 1：基本消息通信"""
    print("=" * 70)
    print("演示 1：基本消息通信")
    print("=" * 70)

    # 创建两个 Agent
    agent_a = AgentMessenger("agent-alice", ".clawbot-demo")
    agent_b = AgentMessenger("agent-bob", ".clawbot-demo")

    print(f"\n✅ Agent Alice 已启动")
    print(f"✅ Agent Bob 已启动")

    # Alice 发送消息给 Bob
    print(f"\n📤 Alice 发送消息给 Bob...")
    result = agent_a.send_message("agent-bob", {
        "type": "greeting",
        "text": "你好 Bob，我们一起学习 Phase 2 吧！"
    })
    print(f"✅ 消息已发送，ID: {result['message_id']}")

    # Bob 接收消息
    print(f"\n📥 Bob 接收消息...")
    time.sleep(0.5)
    messages = agent_b.receive_messages()

    if messages:
        print(f"✅ Bob 收到 {len(messages)} 条消息:")
        for msg in messages:
            print(f"   来自: {msg['from_agent']}")
            print(f"   内容: {msg['content']['text']}")

    # Bob 回复 Alice
    print(f"\n📤 Bob 回复 Alice...")
    agent_b.send_message("agent-alice", {
        "type": "reply",
        "text": "好的 Alice，我们开始吧！"
    })

    # Alice 接收回复
    print(f"\n📥 Alice 接收回复...")
    time.sleep(0.5)
    messages = agent_a.receive_messages()

    if messages:
        print(f"✅ Alice 收到 {len(messages)} 条消息:")
        for msg in messages:
            print(f"   来自: {msg['from_agent']}")
            print(f"   内容: {msg['content']['text']}")

    print(f"\n✅ 基本消息通信演示完成！\n")


def demo_task_lock():
    """演示 2：任务锁协作"""
    print("=" * 70)
    print("演示 2：任务锁协作")
    print("=" * 70)

    agent_a = AgentMessenger("agent-alice", ".clawbot-demo")
    agent_b = AgentMessenger("agent-bob", ".clawbot-demo")

    task_id = "learn-phase2-adapter"

    # Alice 尝试获取任务锁
    print(f"\n🔒 Alice 尝试获取任务锁: {task_id}")
    result_a = agent_a.task_lock.acquire(task_id, "agent-alice")

    if result_a['success']:
        print(f"✅ Alice 成功获取锁")
        print(f"   租约摘要: {result_a['lock']['lease_digest'][:16]}...")
        print(f"   过期时间: {result_a['lock']['expires_at']}")
        alice_digest = result_a['lock']['lease_digest']
    else:
        print(f"❌ Alice 获取锁失败")
        return

    # Bob 尝试获取相同任务的锁
    print(f"\n🔒 Bob 尝试获取相同任务的锁...")
    result_b = agent_b.task_lock.acquire(task_id, "agent-bob")

    if result_b['success']:
        print(f"✅ Bob 成功获取锁（不应该发生！）")
    else:
        print(f"❌ Bob 获取锁失败（预期行为）")
        print(f"   原因: {result_b['reason']}")
        print(f"   当前所有者: {result_b['owner']}")

    # Alice 完成任务后释放锁
    print(f"\n🔓 Alice 完成任务，释放锁...")
    result_release = agent_a.task_lock.release(task_id, "agent-alice", alice_digest)

    if result_release['success']:
        print(f"✅ Alice 成功释放锁")
    else:
        print(f"❌ Alice 释放锁失败: {result_release.get('reason')}")

    # 现在 Bob 可以获取锁了
    print(f"\n🔒 Bob 再次尝试获取锁...")
    result_b2 = agent_b.task_lock.acquire(task_id, "agent-bob")

    if result_b2['success']:
        print(f"✅ Bob 成功获取锁")
        print(f"   租约摘要: {result_b2['lock']['lease_digest'][:16]}...")
    else:
        print(f"❌ Bob 获取锁失败")

    print(f"\n✅ 任务锁协作演示完成！\n")


def demo_broadcast():
    """演示 3：广播消息"""
    print("=" * 70)
    print("演示 3：广播消息")
    print("=" * 70)

    # 创建多个 Agent
    agent_a = AgentMessenger("agent-alice", ".clawbot-demo")
    agent_b = AgentMessenger("agent-bob", ".clawbot-demo")
    agent_c = AgentMessenger("agent-charlie", ".clawbot-demo")

    print(f"\n✅ 3 个 Agent 已启动: Alice, Bob, Charlie")

    # Alice 广播消息
    print(f"\n📢 Alice 广播消息到所有 Agent...")
    agent_a.broadcast({
        "type": "announcement",
        "text": "大家好！我们开始集体学习 Phase 2！"
    })

    print(f"✅ 消息已广播")

    # Bob 和 Charlie 接收广播
    time.sleep(0.5)

    print(f"\n📥 Bob 接收消息...")
    messages_b = agent_b.receive_messages()
    print(f"   收到 {len(messages_b)} 条消息")
    for msg in messages_b:
        print(f"   - {msg['content']['text']}")

    print(f"\n📥 Charlie 接收消息...")
    messages_c = agent_c.receive_messages()
    print(f"   收到 {len(messages_c)} 条消息")
    for msg in messages_c:
        print(f"   - {msg['content']['text']}")

    print(f"\n✅ 广播消息演示完成！\n")


def demo_collaborative_learning():
    """演示 4：协作学习场景"""
    print("=" * 70)
    print("演示 4：协作学习场景")
    print("=" * 70)

    learner = AgentMessenger("agent-learner", ".clawbot-demo")
    reviewer = AgentMessenger("agent-reviewer", ".clawbot-demo")

    print(f"\n✅ Learner Agent 和 Reviewer Agent 已启动")

    # Learner 开始学习任务
    task_id = "learn-phase2-adapter"
    print(f"\n🎓 Learner 开始学习任务: {task_id}")

    lock_result = learner.task_lock.acquire(task_id, "agent-learner")
    if lock_result['success']:
        print(f"✅ Learner 获取任务锁")
        learner_digest = lock_result['lock']['lease_digest']

        # Learner 通知 Reviewer
        print(f"\n📤 Learner 通知 Reviewer 开始学习...")
        learner.send_message("agent-reviewer", {
            "type": "learning_started",
            "task_id": task_id,
            "phase": "phase2-adapter",
            "status": "in_progress"
        })

        # 模拟学习过程
        print(f"\n⏳ Learner 正在学习...")
        time.sleep(1)

        # Learner 完成学习，请求审查
        print(f"\n📤 Learner 请求 Reviewer 审查...")
        learner.send_message("agent-reviewer", {
            "type": "review_request",
            "task_id": task_id,
            "notes": "我已经完成了 Phase 2 的学习，请审查我的笔记。",
            "checkpoints": ["adapter-pattern", "model-abstraction", "testing"]
        })

        # Reviewer 接收请求
        time.sleep(0.5)
        print(f"\n📥 Reviewer 接收审查请求...")
        messages = reviewer.receive_messages()

        if messages:
            review_req = next((m for m in messages if m['content'].get('type') == 'review_request'), None)
            if review_req:
                print(f"✅ Reviewer 收到审查请求:")
                print(f"   任务: {review_req['content']['task_id']}")
                print(f"   备注: {review_req['content']['notes']}")

                # Reviewer 提供反馈
                print(f"\n📤 Reviewer 提供反馈...")
                reviewer.send_message("agent-learner", {
                    "type": "review_feedback",
                    "task_id": task_id,
                    "status": "approved",
                    "comments": "做得很好！Adapter 模式理解透彻，建议继续 Phase 3。"
                })

        # Learner 接收反馈并释放锁
        time.sleep(0.5)
        print(f"\n📥 Learner 接收反馈...")
        feedback_messages = learner.receive_messages()

        if feedback_messages:
            feedback = next((m for m in feedback_messages if m['content'].get('type') == 'review_feedback'), None)
            if feedback:
                print(f"✅ Learner 收到反馈:")
                print(f"   状态: {feedback['content']['status']}")
                print(f"   评论: {feedback['content']['comments']}")

        # 释放任务锁
        print(f"\n🔓 Learner 释放任务锁...")
        learner.task_lock.release(task_id, "agent-learner", learner_digest)
        print(f"✅ 任务完成")

    print(f"\n✅ 协作学习场景演示完成！\n")


def cleanup_demo():
    """清理演示数据"""
    import shutil
    demo_dir = Path(".clawbot-demo")
    if demo_dir.exists():
        shutil.rmtree(demo_dir)
        print(f"[CLEAN] 清理演示数据完成")


def main():
    """运行所有演示"""
    print("\n" + "=" * 70)
    print("ClawBot Multi-Agent 系统演示")
    print("=" * 70 + "\n")

    try:
        # 清理旧数据
        cleanup_demo()

        # 运行演示
        demo_basic_messaging()
        time.sleep(1)

        demo_task_lock()
        time.sleep(1)

        demo_broadcast()
        time.sleep(1)

        demo_collaborative_learning()

        print("\n" + "=" * 70)
        print("所有演示完成！")
        print("=" * 70 + "\n")

        # 询问是否清理
        response = input("是否清理演示数据？(y/n): ").strip().lower()
        if response == 'y':
            cleanup_demo()

    except KeyboardInterrupt:
        print("\n\n⚠️ 演示被中断")
        cleanup_demo()
    except Exception as e:
        print(f"\n\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
