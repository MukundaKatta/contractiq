"""CLI for contractiq."""
import sys, json, argparse
from .core import Contractiq

def main():
    parser = argparse.ArgumentParser(description="ContractIQ — AI Contract Reviewer. Automated contract analysis, risk identification, and clause extraction.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Contractiq()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.manage(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"contractiq v0.1.0 — ContractIQ — AI Contract Reviewer. Automated contract analysis, risk identification, and clause extraction.")

if __name__ == "__main__":
    main()
