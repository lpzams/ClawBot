"""
Multi-Agent CLI - 多终端交互式命令行

使用方法：
    python -m clawbot.multi_agent_cli --agent-id agent-001
    python -m clawbot.multi_agent_cli --agent-id agent-002
"""

import sys
import time
import argparse
from pathlib import Path
from clawbot.multi_agent_core import AgentMessenger


class MultiAgentCLI:
    """多 Agent 交互式 CLI"""

    def __init__(self, agent_id: str, root_dir: str = ".clawbot"):
        self.agent_id = agent_id
        self.messenger = AgentMessenger(agent_id, root_dir)
        self.running = True

        print(f"🤖 Agent {agent_id} 已启动")
        print(f"📁 工作目录: {root_dir}")
        print(f"\n可用命令:")
        print(f"  send <agent_id> <message>  - 发送消息")
        print(f"  broadcast <message>        - 广播消息")
        print(f"  receive                    - 接收消息")
        print(f"  list                       - 列出所有 Agent")
        print(f"  lock <task_id>             - 获取任务锁")
        print(f"  unlock <task_id> <digest>  - 释放任务锁")
        print(f"  help                       - 显示帮助")
        print(f"  exit                       - 退出")
        print()

    def run(self):
        """运行交互式循环"""
        try:
            while self.running:
                try:
                    # 自动接收消息
                    self._check_messages()

                    # 读取用户输入
                    cmd = input(f"[{self.agent_id}]> ").strip()

                    if not cmd:
                        continue

                    self._handle_command(cmd)

                except KeyboardInterrupt:
                    print("\n使用 'exit' 退出")
                except Exception as e:
                    print(f"❌ 错误: {e}")

        finally:
            print(f"\n👋 Agent {self.agent_id} 已退出")

    def _check_messages(self):
        """检查并显示新消息"""
        messages = self.messenger.receive_messages(mark_read=True)

        if messages:
            print(f"\n📨 收到 {len(messages)} 条新消息:")
            for msg in messages:
                print(f"  ├─ 来自: {msg['from_agent']}")
                print(f"  ├─ 时间: {msg['timestamp']}")
                print(f"  └─ 内容: {msg['content']}")
            print()

    def _handle_command(self, cmd: str):
        """处理命令"""
        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()

        if action == "send":
            self._cmd_send(parts[1] if len(parts) > 1 else "")
        elif action == "broadcast":
            self._cmd_broadcast(parts[1] if len(parts) > 1 else "")
        elif action == "receive":
            self._cmd_receive()
        elif action == "list":
            self._cmd_list()
        elif action == "lock":
            self._cmd_lock(parts[1] if len(parts) > 1 else "")
        elif action == "unlock":
            self._cmd_unlock(parts[1] if len(parts) > 1 else "")
        elif action == "help":
            self._cmd_help()
        elif action == "exit":
            self.running = False
        else:
            print(f"❌ 未知命令: {action}，输入 'help' 查看帮助")

    def _cmd_send(self, args: str):
        """发送消息"""
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print("❌ 用法: send <agent_id> <message>")
            return

        to_agent, message = parts
        result = self.messenger.send_message(to_agent, {"text": message})

        if result['success']:
            print(f"✅ 消息已发送到 {to_agent}")
        else:
            print(f"❌ 发送失败")

    def _cmd_broadcast(self, message: str):
        """广播消息"""
        if not message:
            print("❌ 用法: broadcast <message>")
            return

        self.messenger.broadcast({"text": message})
        print(f"📢 消息已广播")

    def _cmd_receive(self):
        """手动接收消息"""
        messages = self.messenger.receive_messages(mark_read=True)

        if not messages:
            print("📭 没有新消息")
            return

        print(f"📨 收到 {len(messages)} 条消息:")
        for msg in messages:
            print(f"  ├─ 来自: {msg['from_agent']}")
            print(f"  ├─ 时间: {msg['timestamp']}")
            print(f"  └─ 内容: {msg['content']}")

    def _cmd_list(self):
        """列出所有 Agent"""
        agents = self.messenger.list_agents()

        if not agents:
            print("📭 没有在线的 Agent")
            return

        print(f"🤖 在线 Agent ({len(agents)}):")
        for agent in agents:
            status = "🟢" if agent['agent_id'] == self.agent_id else "⚪"
            print(f"  {status} {agent['agent_id']}")
            print(f"     └─ 最后心跳: {agent.get('last_heartbeat', 'N/A')}")

    def _cmd_lock(self, task_id: str):
        """获取任务锁"""
        if not task_id:
            print("❌ 用法: lock <task_id>")
            return

        result = self.messenger.task_lock.acquire(task_id, self.agent_id)

        if result['success']:
            print(f"🔒 成功获取任务锁: {task_id}")
            print(f"   摘要: {result['lock']['lease_digest'][:16]}...")
            print(f"   过期时间: {result['lock']['expires_at']}")
        else:
            print(f"❌ 锁已被占用")
            print(f"   所有者: {result.get('owner')}")
            print(f"   过期时间: {result.get('expires_at')}")

    def _cmd_unlock(self, args: str):
        """释放任务锁"""
        parts = args.split()
        if len(parts) < 2:
            print("❌ 用法: unlock <task_id> <digest>")
            return

        task_id, digest = parts
        result = self.messenger.task_lock.release(task_id, self.agent_id, digest)

        if result['success']:
            print(f"🔓 成功释放任务锁: {task_id}")
        else:
            print(f"❌ 释放失败: {result.get('reason')}")

    def _cmd_help(self):
        """显示帮助"""
        print("""
可用命令:
  send <agent_id> <message>  - 发送消息到指定 Agent
  broadcast <message>        - 广播消息到所有 Agent
  receive                    - 手动接收消息
  list                       - 列出所有在线 Agent
  lock <task_id>             - 获取任务锁
  unlock <task_id> <digest>  - 释放任务锁
  help                       - 显示此帮助
  exit                       - 退出程序

示例:
  send agent-002 你好
  broadcast 大家好！
  lock learn-phase2
  unlock learn-phase2 abc123...
        """)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="ClawBot Multi-Agent CLI - 多终端协作工具"
    )
    parser.add_argument(
        "--agent-id",
        required=True,
        help="Agent 唯一标识，如 agent-001"
    )
    parser.add_argument(
        "--root-dir",
        default=".clawbot",
        help="工作目录（默认 .clawbot）"
    )

    args = parser.parse_args()

    cli = MultiAgentCLI(args.agent_id, args.root_dir)
    cli.run()


if __name__ == "__main__":
    main()
