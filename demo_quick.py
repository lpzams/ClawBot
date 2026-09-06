"""
Multi-Agent 快速演示（简化版，无 emoji）
"""

import time
from pathlib import Path
from clawbot.multi_agent_core import AgentMessenger


def quick_demo():
    """快速演示核心功能"""
    print("\n" + "=" * 70)
    print("ClawBot Multi-Agent System - Quick Demo")
    print("=" * 70 + "\n")

    # 创建两个 Agent
    agent_a = AgentMessenger("agent-alice", ".clawbot-demo")
    agent_b = AgentMessenger("agent-bob", ".clawbot-demo")

    print("[OK] Agent Alice started")
    print("[OK] Agent Bob started\n")

    # 1. 基本消息通信
    print("-" * 70)
    print("Test 1: Basic Messaging")
    print("-" * 70)

    print("[SEND] Alice -> Bob: Hello!")
    result = agent_a.send_message("agent-bob", {
        "text": "Hello Bob, let's work together!"
    })
    print(f"[OK] Message sent, ID: {result['message_id'][:8]}...")

    time.sleep(0.5)

    print("[RECV] Bob receiving messages...")
    messages = agent_b.receive_messages()
    if messages:
        print(f"[OK] Bob received {len(messages)} message(s):")
        for msg in messages:
            print(f"     From: {msg['from_agent']}")
            print(f"     Text: {msg['content']['text']}")

    print()

    # 2. 任务锁
    print("-" * 70)
    print("Test 2: Task Lock")
    print("-" * 70)

    task_id = "learn-phase2"

    print(f"[LOCK] Alice acquiring lock: {task_id}")
    lock_a = agent_a.task_lock.acquire(task_id, "agent-alice")

    if lock_a['success']:
        print(f"[OK] Alice got the lock")
        print(f"     Digest: {lock_a['lock']['lease_digest'][:16]}...")
        alice_digest = lock_a['lock']['lease_digest']
    else:
        print(f"[FAIL] Alice failed to get lock")
        return

    print(f"[LOCK] Bob trying to acquire same lock...")
    lock_b = agent_b.task_lock.acquire(task_id, "agent-bob")

    if lock_b['success']:
        print(f"[FAIL] Bob got the lock (should not happen!)")
    else:
        print(f"[OK] Bob failed (expected)")
        print(f"     Reason: {lock_b['reason']}")
        print(f"     Owner: {lock_b['owner']}")

    print(f"[UNLOCK] Alice releasing lock...")
    agent_a.task_lock.release(task_id, "agent-alice", alice_digest)
    print(f"[OK] Lock released")

    print(f"[LOCK] Bob trying again...")
    lock_b2 = agent_b.task_lock.acquire(task_id, "agent-bob")
    if lock_b2['success']:
        print(f"[OK] Bob got the lock now")

    print()

    # 3. 广播
    print("-" * 70)
    print("Test 3: Broadcast")
    print("-" * 70)

    agent_c = AgentMessenger("agent-charlie", ".clawbot-demo")
    print("[OK] Agent Charlie started")

    print("[BROADCAST] Alice broadcasting message...")
    agent_a.broadcast({"text": "Hello everyone!"})
    print("[OK] Message broadcasted")

    time.sleep(0.5)

    print("[RECV] Bob receiving broadcast...")
    msgs_b = agent_b.receive_messages()
    print(f"[OK] Bob received {len(msgs_b)} message(s)")

    print("[RECV] Charlie receiving broadcast...")
    msgs_c = agent_c.receive_messages()
    print(f"[OK] Charlie received {len(msgs_c)} message(s)")

    print()

    # 4. 列出 Agent
    print("-" * 70)
    print("Test 4: List Agents")
    print("-" * 70)

    agents = agent_a.list_agents()
    print(f"[OK] Found {len(agents)} agent(s):")
    for agent in agents:
        print(f"     - {agent['agent_id']}")

    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70 + "\n")

    # 清理
    response = input("Clean up demo data? (y/n): ").strip().lower()
    if response == 'y':
        import shutil
        demo_dir = Path(".clawbot-demo")
        if demo_dir.exists():
            shutil.rmtree(demo_dir)
            print("[CLEAN] Demo data removed")


if __name__ == "__main__":
    try:
        quick_demo()
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Demo stopped")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
