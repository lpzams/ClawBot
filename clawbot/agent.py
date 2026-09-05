from typing import Callable, Dict, List, Optional


# ponytail: keep the reusable boundary to one callable and plain messages;
# introduce structured responses only when a real tool loop needs them.
Message = Dict[str, str]
Model = Callable[[List[Message]], str]


class Harness:
    """Small, provider-neutral execution boundary for one model turn.

    Project code supplies a callable model.  The harness owns input
    validation and message construction, so the same code can be reused by a
    CLI, a web endpoint, a scheduled job, or another Python application.
    """

    def __init__(self, model: Model, *, system_prompt: Optional[str] = None):
        if not callable(model):
            raise TypeError("model must be callable")
        if system_prompt is not None and not isinstance(system_prompt, str):
            raise TypeError("system_prompt must be a string or None")

        self.model = model
        self.system_prompt = system_prompt

    def run(self, prompt: str) -> str:
        """Validate a prompt, call the model once, and return its text reply."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt cannot be blank")

        messages: List[Message] = []
        if self.system_prompt and self.system_prompt.strip():
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        reply = self.model(messages)
        if not isinstance(reply, str):
            raise TypeError("model must return a string")
        return reply


def run_agent(
    prompt: str,
    model: Model,
    *,
    system_prompt: Optional[str] = None,
) -> str:
    """Backward-compatible function wrapper around :class:`Harness`."""

    return Harness(model, system_prompt=system_prompt).run(prompt)
