"""Model adapters used by the reusable ClawBot harness.

The core only knows about a callable ``messages -> string`` contract.  This
module contains the optional network adapter for providers that implement the
OpenAI chat-completions shape; it deliberately uses the standard library so
projects can adopt the harness without another runtime dependency.
"""

import json
import os
from typing import Callable, List, Mapping, Optional
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from .agent import Message


class ModelError(RuntimeError):
    """A provider request or response could not be completed safely."""


class OpenAICompatibleModel:
    """Callable adapter for an OpenAI-compatible ``/chat/completions`` API."""

    def __init__(
        self,
        api_key: str,
        *,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 60.0,
        opener: Callable = urlopen,
    ):
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("api_key cannot be blank")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model cannot be blank")
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("base_url cannot be blank")
        if (
            not isinstance(timeout, (int, float))
            or isinstance(timeout, bool)
            or timeout <= 0
        ):
            raise ValueError("timeout must be greater than zero")
        if not callable(opener):
            raise TypeError("opener must be callable")

        api_key = api_key.strip()
        model = model.strip()
        base_url = base_url.strip().rstrip("/")
        parsed_url = urlsplit(base_url)
        if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
            raise ValueError("base_url must be an http:// or https:// URL")

        self._api_key = api_key
        self.model = model
        self.endpoint = (
            base_url
            if base_url.endswith("/chat/completions")
            else base_url + "/chat/completions"
        )
        self.timeout = timeout
        self._opener = opener

    @classmethod
    def from_env(
        cls,
        environ: Optional[Mapping[str, str]] = None,
        *,
        opener: Callable = urlopen,
    ) -> "OpenAICompatibleModel":
        """Build an adapter from ``OPENAI_*`` environment variables."""
        values = os.environ if environ is None else environ
        raw_api_key = values.get("OPENAI_API_KEY", "")
        api_key = raw_api_key.strip() if isinstance(raw_api_key, str) else ""
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required")

        return cls(
            api_key,
            model=values.get("OPENAI_MODEL", "gpt-4o-mini"),
            base_url=values.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            opener=opener,
        )

    def __call__(self, messages: List[Message]) -> str:
        payload = json.dumps(
            {"model": self.model, "messages": messages},
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            self.endpoint,
            data=payload,
            headers={
                "Authorization": "Bearer " + self._api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with self._opener(request, timeout=self.timeout) as response:
                raw_body = response.read()
        except HTTPError as error:
            raise ModelError(
                "model request failed (HTTP {})".format(error.code)
            ) from error
        except OSError as error:
            raise ModelError("model request failed: provider unavailable") from error

        try:
            data = json.loads(raw_body.decode("utf-8"))
            reply = data["choices"][0]["message"]["content"]
        except (
            KeyError,
            IndexError,
            TypeError,
            ValueError,
            UnicodeDecodeError,
        ) as error:
            raise ModelError("model response did not contain text content") from error

        if not isinstance(reply, str):
            raise ModelError("model response did not contain text content")
        return reply
