import argparse
import os
import subprocess
import sys
import yaml
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run pytest against one or more environments from config/environments.yaml"
    )
    parser.add_argument(
        "--env",
        default="dev",
        help="Environment key from config/environments.yaml. Hyphens are normalized to underscores. Use 'all' to run every environment.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run pytest against all environment keys defined in config/environments.yaml.",
    )
    parser.add_argument(
        "--headless",
        choices=["true", "false"],
        help="Override headless browser behavior.",
    )
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        help="Override browser type for Playwright.",
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments forwarded to pytest.",
    )
    return parser.parse_args()


def load_environment_keys():
    config_path = Path("config/environments.yaml")
    with open(config_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return [key.strip().lower().replace("-", "_") for key in data.keys()]


def run_pytest_for_env(env_value, args):
    os.environ["ENV"] = env_value
    if args.headless is not None:
        os.environ["HEADLESS"] = args.headless
    if args.browser:
        os.environ["BROWSER"] = args.browser

    cmd = [sys.executable, "-m", "pytest"] + args.pytest_args
    print(f"\n=== Running environment: {env_value} ===")
    print("Running test command:", " ".join(cmd))
    if args.headless is not None:
        print("Headless override:", args.headless)
    if args.browser:
        print("Browser override:", args.browser)

    result = subprocess.run(cmd)
    return result.returncode or 1


def main():
    args = parse_args()
    env_value = args.env.strip().lower().replace("-", "_")

    if args.all and args.env != "dev":
        print("Error: cannot use --all together with --env <env>.", file=sys.stderr)
        return 2

    if args.all or env_value == "all":
        env_values = load_environment_keys()
    else:
        env_values = [env_value]

    if not env_values:
        print("No environments found in config/environments.yaml.", file=sys.stderr)
        return 1

    exit_code = 0
    for env in env_values:
        current_code = run_pytest_for_env(env, args)
        if current_code != 0:
            exit_code = current_code

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
