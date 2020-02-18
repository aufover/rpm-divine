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
        return "%d heap object%s leaked" % (leak_count, "" if leak_count == 1
                                                        else "s")

    return re.sub(r"((?<=heap\*)|(?<=alloca\*)|(?<=global\*))[^]]+|[0-9]+:",
                  "", line)


def parse_location(location: List[str]) -> str:
    return location[0] + ("" if len(location) == 1 else ":" + location[1])


def print_error_trace(report, error: Error, verbose: bool,
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

            print(location + ": " + error.name.replace("_", " ") + ": " +
                  line.replace("FAULT: ", ""))
            continue

        print(location + ": note: " +
              line.replace("[0] FATAL: ", "").replace("DOUBLE FAULT: ", ""))

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

    if type(report) == str:
        print("Invalid input")
        sys.exit(1)

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
                      parse_location(location))

    for frame in report["active stack"]:
        print(parse_location(frame["location"].split(":")) + ": note: " +
              frame["symbol"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Divine to csgrep")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="do not sanitise the error cause")
    parser.add_argument("infile", nargs="?", type=argparse.FileType("r"),
                        default=sys.stdin, help="input file (default: stdin)")

    main(parser.parse_args())
