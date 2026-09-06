"""
Multi-Agent 核心功能测试

测试内容：
1. Agent 消息发送/接收
2. 任务锁机制（acquire/renew/release）
3. 消息去重
4. 广播功能
"""

import unittest
import json
import time
from pathlib import Path
import shutil
from clawbot.multi_agent_core import (
    AgentMessenger,
    FencedTaskWriteOwner,
    ContextDeliveryLedger,
    sha256_digest
)


class TestMultiAgentCore(unittest.TestCase):
    """测试 Multi-Agent 核心功能"""

    def setUp(self):
        """测试前准备"""
        self.test_root = Path(".clawbot-test")
        # 清理旧测试数据
        if self.test_root.exists():
            shutil.rmtree(self.test_root)
        self.test_root.mkdir()

    def tearDown(self):
        """测试后清理"""
        if self.test_root.exists():
            shutil.rmtree(self.test_root)

    def test_agent_registration(self):
        """测试 Agent 注册"""
        agent = AgentMessenger("agent-001", str(self.test_root))

        # 检查注册文件
        agent_file = self.test_root / "agents" / "agent-001.json"
        self.assertTrue(agent_file.exists())

        with open(agent_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(data['agent_id'], "agent-001")
        self.assertIn('started_at', data)

    def test_send_and_receive_message(self):
        """测试消息发送和接收"""
        agent1 = AgentMessenger("agent-001", str(self.test_root))
        agent2 = AgentMessenger("agent-002", str(self.test_root))

        # Agent 1 发送消息给 Agent 2
        result = agent1.send_message("agent-002", {"text": "Hello from Agent 1"})
        self.assertTrue(result['success'])

        # Agent 2 接收消息
        messages = agent2.receive_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['from_agent'], "agent-001")
        self.assertEqual(messages[0]['content']['text'], "Hello from Agent 1")

    def test_message_deduplication(self):
        """测试消息去重"""
        agent1 = AgentMessenger("agent-001", str(self.test_root))
        agent2 = AgentMessenger("agent-002", str(self.test_root))

        # 发送消息
        result = agent1.send_message("agent-002", {"text": "Test message"})
        message_digest = result['message_digest']

        # 第一次接收
        messages = agent2.receive_messages(mark_read=True)
        self.assertEqual(len(messages), 1)

        # 模拟消息重复（手动写入相同摘要的消息）
        # 注意：正常情况下不会有重复，这里是为了测试去重机制
        ledger = ContextDeliveryLedger(str(self.test_root))
        should_deliver = ledger.should_deliver("agent-002", message_digest)
        self.assertFalse(should_deliver)  # 不应该再次投递

    def test_task_lock_acquire_release(self):
        """测试任务锁获取和释放"""
        lock_manager = FencedTaskWriteOwner(str(self.test_root))

        # Agent 1 获取锁
        result = lock_manager.acquire("task-001", "agent-001")
        self.assertTrue(result['success'])
        self.assertTrue(result['mutation_authority'])

        lock_digest = result['lock']['lease_digest']

        # Agent 2 尝试获取相同任务的锁（应该失败）
        result2 = lock_manager.acquire("task-001", "agent-002")
        self.assertFalse(result2['success'])
        self.assertEqual(result2['reason'], "lock_held_by_other")

        # Agent 1 释放锁
        result3 = lock_manager.release("task-001", "agent-001", lock_digest)
        self.assertTrue(result3['success'])

        # 现在 Agent 2 可以获取锁了
        result4 = lock_manager.acquire("task-001", "agent-002")
        self.assertTrue(result4['success'])

    def test_task_lock_renew(self):
        """测试任务锁续约"""
        lock_manager = FencedTaskWriteOwner(str(self.test_root))

        # 获取锁
        result = lock_manager.acquire("task-002", "agent-001")
        self.assertTrue(result['success'])

        original_digest = result['lock']['lease_digest']
        original_revision = result['lock']['lease_revision']

        # 续约
        result2 = lock_manager.renew("task-002", "agent-001", original_digest)
        self.assertTrue(result2['success'])

        new_digest = result2['lock']['lease_digest']
        new_revision = result2['lock']['lease_revision']

        # 检查租约版本递增
        self.assertEqual(new_revision, original_revision + 1)
        self.assertNotEqual(new_digest, original_digest)

    def test_task_lock_cas_mismatch(self):
        """测试 CAS（Compare-And-Swap）失败"""
        lock_manager = FencedTaskWriteOwner(str(self.test_root))

        # 获取锁
        result = lock_manager.acquire("task-003", "agent-001")
        lock_digest = result['lock']['lease_digest']

        # 使用错误的摘要尝试续约
        wrong_digest = "0" * 64
        result2 = lock_manager.renew("task-003", "agent-001", wrong_digest)

        self.assertFalse(result2['success'])
        self.assertEqual(result2['reason'], "cas_mismatch")

    def test_broadcast(self):
        """测试广播消息"""
        agent1 = AgentMessenger("agent-001", str(self.test_root))
        agent2 = AgentMessenger("agent-002", str(self.test_root))
        agent3 = AgentMessenger("agent-003", str(self.test_root))

        # Agent 1 广播消息
        agent1.broadcast({"text": "Broadcast message"})

        # Agent 2 和 3 都应该收到
        messages2 = agent2.receive_messages()
        messages3 = agent3.receive_messages()

        self.assertEqual(len(messages2), 1)
        self.assertEqual(len(messages3), 1)
        self.assertEqual(messages2[0]['content']['text'], "Broadcast message")
        self.assertEqual(messages3[0]['content']['text'], "Broadcast message")

    def test_list_agents(self):
        """测试列出 Agent"""
        agent1 = AgentMessenger("agent-001", str(self.test_root))
        agent2 = AgentMessenger("agent-002", str(self.test_root))
        agent3 = AgentMessenger("agent-003", str(self.test_root))

        agents = agent1.list_agents()

        self.assertEqual(len(agents), 3)
        agent_ids = [a['agent_id'] for a in agents]
        self.assertIn("agent-001", agent_ids)
        self.assertIn("agent-002", agent_ids)
        self.assertIn("agent-003", agent_ids)

    def test_sha256_digest(self):
        """测试 SHA256 摘要计算"""
        data1 = {"key": "value"}
        data2 = {"key": "value"}
        data3 = {"key": "other"}

        digest1 = sha256_digest(data1)
        digest2 = sha256_digest(data2)
        digest3 = sha256_digest(data3)

        # 相同数据应该产生相同摘要
        self.assertEqual(digest1, digest2)

        # 不同数据应该产生不同摘要
        self.assertNotEqual(digest1, digest3)

        # 摘要应该是 64 位十六进制字符串
        self.assertEqual(len(digest1), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in digest1))


def run_tests():
    """运行所有测试"""
    print("运行 Multi-Agent 核心功能测试...\n")

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMultiAgentCore)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出总结
    print(f"\n{'='*70}")
    print(f"测试完成:")
    print(f"  [PASS] 通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  [FAIL] 失败: {len(result.failures)}")
    print(f"  [ERROR] 错误: {len(result.errors)}")
    print(f"{'='*70}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
