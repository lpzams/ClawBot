from typing import Callable, Dict, List


# ponytail: plain messages and string replies cover Phase 1; use structured
# responses when tool calling makes them necessary.
Message = Dict[str, str]
Model = Callable[[List[Message]], str]


def run_agent(prompt: str, model: Model) -> str:
    """Send one user message to a model and return its reply."""
    if not prompt.strip():
        raise ValueError("prompt cannot be blank")

    return model([{"role": "user", "content": prompt}])
