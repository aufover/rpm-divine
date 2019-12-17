#!/usr/bin/python3

from typing import List, TextIO

import sys
import yaml


def print_error_trace(report, error_type: str,
                      location: str = None) -> None:
    trace: List[str] = report["error trace"].split("\n")
    trace.pop()  # might break in future

    if location is None:
        location = report["input file"]

    for line in trace:
        print(location + (": error: " + error_type + ": " if line is trace[0]
                          else ": note: ") + line)

    return


def main() -> None:
    if len(sys.argv) != 2:
        print("USAGE: %s [DIVINE REPORT]" % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    in_file: TextIO = (sys.stdin if sys.argv[1] == "-"
                       else open(sys.argv[1], "r"))

    try:
        report = yaml.safe_load(in_file)
    except yaml.YAMLError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    if report is None:
        print("divine: error: DIVINE ERROR: Divine crashed and no log was"
              " created\ndivine: note: see stderr output of given divine"
              " process")
        return

    if not report["error found"]:
        return

    if report["error found"] == "unknown":
        print_error_trace(report, "DIVINE UNKNOWN")
        return

    if report["error found"] == "boot":
        print_error_trace(report, "DIOS BOOT")
        return

    for frame in report["active stack"]:
        if "/opt/divine/" in frame["location"]:
            continue

        location: List[str] = frame["location"].split(":")
        print(location[0] + ": In function ‘" + frame["symbol"] + "’:")

        location_string: str = location[0] + ":" + location[1]
        print_error_trace(report, "DIVINE ERROR", location_string)

        print(location_string + ": note: backtrace:")
        break

    for frame in report["active stack"]:
        location = frame["location"].split(":")
        print(location[0] + ":" + location[1] + ": note: " + frame["symbol"])

    in_file.close()


if __name__ == "__main__":
    main()
