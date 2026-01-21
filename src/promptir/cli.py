"""Command line interface for promptir."""

from __future__ import annotations

import argparse
import sys

from promptir.compiler import compile_prompts
from promptir.errors import PromptCompileError


def main() -> int:
    parser = argparse.ArgumentParser(prog="promptir")
    subparsers = parser.add_subparsers(dest="command")

    compile_parser = subparsers.add_parser("compile", help="Compile prompts to a manifest")
    compile_parser.add_argument("--src", required=True, help="Source prompts root")
    compile_parser.add_argument("--out", required=True, help="Output manifest path")

    args = parser.parse_args()

    if args.command == "compile":
        try:
            compile_prompts(args.src, args.out)
        except PromptCompileError as exc:
            print(f"Compile error: {exc}", file=sys.stderr)
            return 1
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
