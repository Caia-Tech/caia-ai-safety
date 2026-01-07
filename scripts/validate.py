#!/usr/bin/env python3
import argparse
import glob
import json
import os
import sys

ALLOWED_ROLES = {"user", "assistant"}


def iter_files(paths, include_evals):
    if paths:
        return paths
    files = sorted(glob.glob("*.jsonl"))
    if include_evals:
        files.extend(sorted(glob.glob(os.path.join("evals", "*.jsonl"))))
    return sorted(set(files))


def validate_file(path):
    errors = []
    line_count = 0
    with open(path, "r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line_count += 1
            if not line.strip():
                errors.append(f"{path}:{line_number}: empty line")
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}:{line_number}: invalid json ({exc})")
                continue
            if not isinstance(obj, dict):
                errors.append(f"{path}:{line_number}: top-level value must be an object")
                continue
            chat = obj.get("chat")
            if not isinstance(chat, list) or not chat:
                errors.append(f"{path}:{line_number}: chat must be a non-empty list")
                continue
            for index, message in enumerate(chat, 1):
                if not isinstance(message, dict):
                    errors.append(f"{path}:{line_number}: chat[{index}] must be an object")
                    continue
                role = message.get("role")
                content = message.get("content")
                if role not in ALLOWED_ROLES:
                    errors.append(f"{path}:{line_number}: chat[{index}].role invalid")
                if not isinstance(content, str) or not content.strip():
                    errors.append(f"{path}:{line_number}: chat[{index}].content must be a non-empty string")
    return line_count, errors


def main():
    parser = argparse.ArgumentParser(description="Validate CAIA AI Safety JSONL schema.")
    parser.add_argument("paths", nargs="*", help="JSONL files to validate")
    parser.add_argument(
        "--include-evals",
        action="store_true",
        help="Include evals/*.jsonl when no paths are provided",
    )
    args = parser.parse_args()

    files = iter_files(args.paths, args.include_evals)
    if not files:
        print("No JSONL files found to validate.", file=sys.stderr)
        return 1

    total_lines = 0
    total_errors = 0
    for path in files:
        line_count, errors = validate_file(path)
        total_lines += line_count
        total_errors += len(errors)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
        print(f"{path}: {line_count} lines, {len(errors)} errors")

    print(f"Checked {len(files)} files, {total_lines} lines, {total_errors} errors")
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
