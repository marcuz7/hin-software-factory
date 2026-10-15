"""Demo-only CLI: no agents are launched."""
import argparse
import json
from .core import Factory

def main():
    parser = argparse.ArgumentParser(description="HIN P0 local task state machine")
    parser.add_argument("--db", default=".hin-p0/tasks.db")
    parser.add_argument("action", choices=["demo", "list", "expire"])
    args = parser.parse_args()
    factory = Factory(args.db)
    try:
        if args.action == "demo":
            first = factory.add("ithaca-demo", "Compile approved requirements")
            factory.claim(first, "mock-coder")
            factory.submit(first, "mock-coder", ["mock-evidence: specification scaffold"])
            factory.approve(first, "mock-reviewer")
            factory.add("ithaca-demo", "Build mock-profile feature", [first])
        elif args.action == "expire":
            print("expired:", factory.expire())
        print(json.dumps(factory.list(), indent=2))
    finally:
        factory.close()

if __name__ == "__main__":
    main()
