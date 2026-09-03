import argparse

from .agent import run_agent


def fake_model(messages):
    return f"ClawBot received: {messages[-1]['content']}"


def main():
    parser = argparse.ArgumentParser(description="Run the ClawBot harness")
    parser.add_argument("prompt", help="message sent to ClawBot")
    args = parser.parse_args()

    try:
        print(run_agent(args.prompt, fake_model))
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
