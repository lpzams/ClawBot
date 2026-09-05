import argparse

from .agent import run_agent
from .models import ModelError, OpenAICompatibleModel


def fake_model(messages):
    return f"ClawBot received: {messages[-1]['content']}"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the ClawBot harness")
    parser.add_argument(
        "--provider",
        choices=("fake", "openai"),
        default="fake",
        help="model provider (fake is offline by default)",
    )
    parser.add_argument(
        "--system-prompt",
        help="optional instruction prepended to the user message",
    )
    parser.add_argument("prompt", help="message sent to ClawBot")
    args = parser.parse_args(argv)

    try:
        model = (
            fake_model
            if args.provider == "fake"
            else OpenAICompatibleModel.from_env()
        )
        print(
            run_agent(
                args.prompt,
                model,
                system_prompt=args.system_prompt,
            )
        )
        return 0
    except (ValueError, ModelError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
