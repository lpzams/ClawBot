import json
import unittest

from clawbot.models import ModelError, OpenAICompatibleModel


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.body


class ModelAdapterTest(unittest.TestCase):
    def test_sends_openai_compatible_request_and_reads_reply(self):
        requests = []

        def opener(request, timeout):
            requests.append((request, timeout))
            return FakeResponse(
                b'{"choices":[{"message":{"content":"hello from model"}}]}'
            )

        model = OpenAICompatibleModel(
            "secret",
            model="demo-model",
            base_url="https://provider.example/v1",
            timeout=12,
            opener=opener,
        )

        self.assertEqual(
            model([{"role": "user", "content": "hi"}]),
            "hello from model",
        )
        request, timeout = requests[0]
        self.assertEqual(request.full_url, "https://provider.example/v1/chat/completions")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")
        self.assertEqual(timeout, 12)
        self.assertEqual(
            json.loads(request.data.decode("utf-8")),
            {
                "model": "demo-model",
                "messages": [{"role": "user", "content": "hi"}],
            },
        )

    def test_from_env_requires_an_api_key(self):
        with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY is required"):
            OpenAICompatibleModel.from_env({})

    def test_rejects_malformed_provider_response(self):
        model = OpenAICompatibleModel(
            "secret",
            model="demo-model",
            opener=lambda request, timeout: FakeResponse(b"{}"),
        )

        with self.assertRaisesRegex(ModelError, "did not contain text content"):
            model([])

    def test_validates_adapter_configuration(self):
        with self.assertRaisesRegex(ValueError, "base_url"):
            OpenAICompatibleModel("secret", model="demo", base_url="file:///tmp")
        with self.assertRaisesRegex(ValueError, "timeout"):
            OpenAICompatibleModel("secret", model="demo", timeout=0)

    def test_hides_transport_error_details(self):
        def opener(request, timeout):
            raise OSError("secret network detail")

        model = OpenAICompatibleModel("secret", model="demo", opener=opener)

        with self.assertRaisesRegex(ModelError, "provider unavailable") as raised:
            model([])
        self.assertNotIn("secret network detail", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
