"""Taslak veri için kaynak sabitleme, doğrulama, inceleme ve kontrollü dışa aktarma."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluation.dataset import (DEFAULT_DATA, Dataset, digest, export_rows, read_json,
                                review_markdown, snapshot, validate)


def write_new(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(content)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("snapshot")
    schema = sub.add_parser("schema")
    schema.add_argument("--output", type=Path, required=True)
    validation = sub.add_parser("validate")
    validation.add_argument("--verify-raw", action="store_true")
    validation.add_argument("--report", type=Path)
    review = sub.add_parser("review")
    review.add_argument("--output", type=Path, required=True)
    export = sub.add_parser("export")
    export.add_argument("--purpose", choices=["evaluation", "lora"], required=True)
    export.add_argument("--split", choices=["train", "dev", "test"], required=True)
    export.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "schema":
            write_new(args.output, json.dumps(Dataset.model_json_schema(), ensure_ascii=False, indent=2) + "\n")
            print(args.output)
            return
        if args.command == "snapshot":
            result = snapshot(read_json(args.data / "catalog.json"))
            write_new(args.data / "evidence.json", json.dumps(result, ensure_ascii=False, indent=2) + "\n")
            print(f"Kaynak özeti: {digest(result)}")
            return
        dataset = Dataset.model_validate(read_json(args.data / "dataset.json"))
        evidence = read_json(args.data / "evidence.json")
        if args.command == "validate":
            report = json.dumps(validate(dataset, evidence, verify_raw=args.verify_raw), ensure_ascii=False, indent=2)
            if args.report:
                write_new(args.report, report + "\n")
            print(report)
        elif args.command == "review":
            write_new(args.output, review_markdown(dataset, evidence))
            print(args.output)
        else:
            rows = export_rows(dataset, evidence, args.split, args.purpose)
            write_new(args.output, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
            print(f"{len(rows)} onaylı kayıt: {args.output}")
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"HATA: {exc}\n")


if __name__ == "__main__":
    main()
