import unittest

from clawbot.agent import run_agent


class AgentTest(unittest.TestCase):
    def test_passes_user_message_to_model(self):
        seen_messages = []

        def fake_model(messages):
            seen_messages.extend(messages)
            return "fixed reply"

        self.assertEqual(run_agent("hello", fake_model), "fixed reply")
        self.assertEqual(
            seen_messages,
            [{"role": "user", "content": "hello"}],
        )

    def test_rejects_blank_prompt(self):
        with self.assertRaisesRegex(ValueError, "prompt cannot be blank"):
            run_agent("   ", lambda messages: "unused")


if __name__ == "__main__":
    unittest.main()
