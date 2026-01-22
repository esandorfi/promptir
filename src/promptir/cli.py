"""Command line interface for promptir."""

from __future__ import annotations

import argparse
import json
import sys

from promptir.compiler import compile_prompts
from promptir.demo import dump_demo_results, render_demo, write_demo_results
from promptir.errors import PromptCompileError, PromptInputError, PromptNotFound


def main() -> int:
    parser = argparse.ArgumentParser(prog="promptir")
    subparsers = parser.add_subparsers(dest="command")

    compile_parser = subparsers.add_parser("compile", help="Compile prompts to a manifest")
    compile_parser.add_argument("--src", required=True, help="Source prompts root")
    compile_parser.add_argument("--out", required=True, help="Output manifest path")

    demo_parser = subparsers.add_parser(
        "demo-run", help="Render a manifest with demo data to validate prompt outputs"
    )
    demo_parser.add_argument("--manifest", required=True, help="Manifest path")
    demo_parser.add_argument("--data", required=True, help="Demo data JSON path")
    demo_parser.add_argument("--out", help="Output path (defaults to stdout)")

    args = parser.parse_args()

    if args.command == "compile":
        try:
            compile_prompts(args.src, args.out)
        except PromptCompileError as exc:
            print(f"Compile error: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.command == "demo-run":
        try:
            results = render_demo(args.manifest, args.data)
        except (PromptInputError, PromptNotFound, ValueError, json.JSONDecodeError) as exc:
            print(f"Demo error: {exc}", file=sys.stderr)
            return 1
        if args.out:
            write_demo_results(results, args.out)
        else:
            print(dump_demo_results(results))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
