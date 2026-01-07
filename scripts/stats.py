#!/usr/bin/env python3
import argparse
import glob
import json
import os
import sys


def iter_files(paths, include_evals):
    if paths:
        return paths
    files = sorted(glob.glob("*.jsonl"))
    if include_evals:
        files.extend(sorted(glob.glob(os.path.join("evals", "*.jsonl"))))
    return sorted(set(files))


def count_words(text):
    return len(text.split())


def stats_for_file(path):
    examples = 0
    total_turns = 0
    min_turns = None
    max_turns = None
    total_msgs = 0
    user_msgs = 0
    assistant_msgs = 0
    total_words = 0
    user_words = 0
    assistant_words = 0
    errors = 0

    with open(path, "r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                errors += 1
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                errors += 1
                continue
            chat = obj.get("chat")
            if not isinstance(chat, list) or not chat:
                errors += 1
                continue
            examples += 1
            turns = len(chat)
            total_turns += turns
            min_turns = turns if min_turns is None else min(min_turns, turns)
            max_turns = turns if max_turns is None else max(max_turns, turns)
            for message in chat:
                if not isinstance(message, dict):
                    errors += 1
                    continue
                role = message.get("role", "")
                content = message.get("content", "")
                if not isinstance(content, str):
                    errors += 1
                    continue
                words = count_words(content)
                total_msgs += 1
                total_words += words
                if role == "user":
                    user_msgs += 1
                    user_words += words
                elif role == "assistant":
                    assistant_msgs += 1
                    assistant_words += words
                else:
                    errors += 1

    return {
        "examples": examples,
        "total_turns": total_turns,
        "min_turns": min_turns or 0,
        "max_turns": max_turns or 0,
        "total_msgs": total_msgs,
        "user_msgs": user_msgs,
        "assistant_msgs": assistant_msgs,
        "total_words": total_words,
        "user_words": user_words,
        "assistant_words": assistant_words,
        "errors": errors,
    }


def print_report(path, stats):
    examples = stats["examples"]
    total_turns = stats["total_turns"]
    total_msgs = stats["total_msgs"]
    total_words = stats["total_words"]
    avg_turns = (total_turns / examples) if examples else 0
    avg_words = (total_words / total_msgs) if total_msgs else 0
    print(path)
    print(f"  examples: {examples}")
    print(f"  turns_avg: {avg_turns:.2f}")
    print(f"  turns_min: {stats['min_turns']}")
    print(f"  turns_max: {stats['max_turns']}")
    print(f"  messages: {total_msgs}")
    print(f"  user_msgs: {stats['user_msgs']}")
    print(f"  assistant_msgs: {stats['assistant_msgs']}")
    print(f"  words_avg_per_msg: {avg_words:.2f}")
    print(f"  errors: {stats['errors']}")


def main():
    parser = argparse.ArgumentParser(description="Dataset stats report for CAIA AI Safety JSONL files.")
    parser.add_argument("paths", nargs="*", help="JSONL files to report on")
    parser.add_argument(
        "--include-evals",
        action="store_true",
        help="Include evals/*.jsonl when no paths are provided",
    )
    args = parser.parse_args()

    files = iter_files(args.paths, args.include_evals)
    if not files:
        print("No JSONL files found to report on.", file=sys.stderr)
        return 1

    totals = {
        "examples": 0,
        "total_turns": 0,
        "min_turns": None,
        "max_turns": None,
        "total_msgs": 0,
        "user_msgs": 0,
        "assistant_msgs": 0,
        "total_words": 0,
        "user_words": 0,
        "assistant_words": 0,
        "errors": 0,
    }

    for path in files:
        stats = stats_for_file(path)
        print_report(path, stats)
        totals["examples"] += stats["examples"]
        totals["total_turns"] += stats["total_turns"]
        totals["total_msgs"] += stats["total_msgs"]
        totals["user_msgs"] += stats["user_msgs"]
        totals["assistant_msgs"] += stats["assistant_msgs"]
        totals["total_words"] += stats["total_words"]
        totals["user_words"] += stats["user_words"]
        totals["assistant_words"] += stats["assistant_words"]
        totals["errors"] += stats["errors"]
        if stats["min_turns"]:
            totals["min_turns"] = (
                stats["min_turns"]
                if totals["min_turns"] is None
                else min(totals["min_turns"], stats["min_turns"])
            )
        totals["max_turns"] = max(totals["max_turns"] or 0, stats["max_turns"])

    if len(files) > 1:
        print("TOTAL")
        print_report("all_files", totals)

    return 1 if totals["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
