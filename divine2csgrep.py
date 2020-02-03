#!/usr/bin/python3

from enum import Enum
from typing import List

import argparse
import re
import sys
import yaml


class Error(Enum):
    warning = 1
    error = 2
    fatal_error = 3


def sanitise(line: str) -> str:
    if "leaked" in line:
        leak_count: int = len(re.findall(r"leaked", line))
        return "FAULT: %d heap object%s leaked" % (leak_count,
                                                   "" if leak_count == 1
                                                   else "s")

    return re.sub(
            re.compile("((?<=heap\*)|(?<=alloca\*)|(?<=global\*))(.*(?= leaked)|[^]]+)||[0-9]+:",
                       re.DOTALL),
            "",
            line)


def print_error_trace(report, error_type: Error, verbose: bool,
                      location: str = None) -> None:
    trace: List[str] = report["error trace"].split("\n")
    trace.pop()  # might break in future

    if location is None:
        location = report["input file"]

    for line in trace:
        if report.get("symbolic") is not None and "ASSUME" in line:
            continue

        if line.startswith("FAULT"):
            if not verbose:
                line = sanitise(line)

            print(location + ": " + error_type.name.replace("_", " ") + ": " +
                  line)
            continue

        print(location + ": note: " + line.replace("[0] ", ""))

    return


def main(args: argparse.Namespace) -> None:
    try:
        report = yaml.safe_load(args.infile)
        args.infile.close()
    except yaml.YAMLError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    if report is None:
        print("Error: DIVINE_WARNING:\n" +
              "divine: fatal error: Divine crashed and no log was created\n" +
              "divine: note: see stderr output of given divine process")
        return

    if not report["error found"]:
        return

    print("Error: DIVINE_WARNING:")
    if report["error found"] == "unknown":
        print_error_trace(report, Error.fatal_error, args.verbose)
        return

    if report["error found"] == "boot":
        print_error_trace(report, Error.fatal_error, args.verbose)
        return

    # FIXME: This is atrocious
    for frame in report["active stack"]:
        if "/opt/divine/" in frame["location"]:
            continue
        break

    location: List[str] = frame["location"].split(":")
    print(location[0] + ": scope_hint: In function ‘" + frame["symbol"] + "’:")
    print_error_trace(report, Error.error, args.verbose,
                      location[0] + ":" + location[1])

    for frame in report["active stack"]:
        location = frame["location"].split(":")
        print(location[0] + ":" + location[1] + ": note: " + frame["symbol"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Divine to csgrep")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="do not sanitise the error cause")
    parser.add_argument("infile", nargs="?", type=argparse.FileType("r"),
                        default=sys.stdin, help="input file (default: stdin)")

    main(parser.parse_args())
