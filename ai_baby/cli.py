import argparse
import json
from .core import AIBaby
from .memory import MemoryStore

def demo_sequence():
    # Sequenza quadratica: n^2 + 1, da n=0 a n=11.
    return [1, 2, 5, 10, 17, 26, 37, 50, 65, 82, 101, 122]

def main(argv=None):
    parser = argparse.ArgumentParser(prog="ai-baby")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo")
    demo.add_argument("--db", default="ai_baby_memory.sqlite")
    demo.add_argument("--budget", type=int, default=20000)
    demo.add_argument("--depth", type=int, default=3)
    hist = sub.add_parser("history")
    hist.add_argument("--db", default="ai_baby_memory.sqlite")
    hist.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)
    memory = MemoryStore(args.db)
    if args.command == "demo":
        result = AIBaby(memory).investigate_sequence(
            demo_sequence(), train_end=8, max_depth=args.depth, budget=args.budget
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(json.dumps(memory.history(args.limit), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
