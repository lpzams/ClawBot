import unittest

from clawbot import Harness, run_agent


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

    def test_harness_can_prepend_a_system_prompt(self):
        seen_messages = []

        def fake_model(messages):
            seen_messages.extend(messages)
            return "reply"

        harness = Harness(fake_model, system_prompt="Be concise")

        self.assertEqual(harness.run("hello"), "reply")
        self.assertEqual(
            seen_messages,
            [
                {"role": "system", "content": "Be concise"},
                {"role": "user", "content": "hello"},
            ],
        )

    def test_rejects_non_text_model_reply(self):
        with self.assertRaisesRegex(TypeError, "model must return a string"):
            Harness(lambda messages: 123).run("hello")


if __name__ == "__main__":
    unittest.main()
