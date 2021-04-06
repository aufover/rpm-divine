#!/usr/bin/python3

from enum import Enum
from typing import Any, Dict, List, Optional, TextIO, Union
from yaml import CLoader

import argparse
import re
import sys
import yaml

import os.path


# Separates reports
separator: str = ""


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


def sanitise_note(line: str) -> str:
    return line.replace("[0] ", "").replace("(0) ", "") \
               .replace("FATAL: ", "").replace("DOUBLE FAULT: ", "")


def print_error_trace(report: Dict[str, Any], error: Error, args: argparse.Namespace,
                      location: Optional[str] = None) -> None:
    trace: List[str] = report["error trace"].split("\n")
    trace.pop()  # might break in future

    if location is None:
        location = parse_location(report["input file"], args.absolute_paths)

    for line in trace:
        if report.get("symbolic") is not None and "ASSUME" in line:
            continue

        if line.startswith("FAULT"):
            if not args.verbose:
                line = sanitise(line)

            print(location + ": " + error.name.replace("_", " ") + ": " +
                  line.replace("FAULT: ", ""))
            continue

        print(location + ": note: " + sanitise_note(line))

    return


def parse_location(loc: str, absolute_paths: bool) -> str:
    if "unknown" in loc:
        return "<unknown>"

    if not absolute_paths:
        return loc

    # make it absolute
    locations = loc.split(":")

    assert os.path.exists(locations[0])
    locations[0] = os.path.abspath(locations[0])

    return ":".join(locations)


def parse_reports(file: TextIO) -> List[str]:
    reports: List[str] = []
    found: bool = False
    rep: str = ""

    for line in file:
        if not found and "states per second" not in line:
            continue

        if "a report was written" in line:
            found = False
            reports.append(rep)
            rep = ""
            continue

        if "states per second" in line:
            if found:
                reports.append(rep)
            rep = ""

        found = True
        rep += line

    if found:
        reports.append(rep)

    return reports if reports else [""]


def process_report(args: argparse.Namespace,
                   report: Union[str, Dict[str, Any]]) -> None:
    global separator

    if report is None:
        print(separator + "Error: DIVINE_WARNING:\n" +
              "divine: fatal error: Divine crashed and incomplete log was" +
              " created\n" +
              "divine: note: see stderr output of given divine process")
        return

    if type(report) == str:
        print("Invalid input")
        sys.exit(1)

    assert isinstance(report, dict)
    if not report["error found"]:
        return

    print(separator + "Error: DIVINE_WARNING:")
    if report["error found"] == "unknown":
        print_error_trace(report, Error.fatal_error, args)
        return

    if report["error found"] == "boot":
        print_error_trace(report, Error.fatal_error, args)
        return

    # FIXME: This is atrocious
    for frame in report["active stack"]:
        if "/opt/divine/" in frame["location"]:
            continue
        break

    location: str = parse_location(frame["location"], args.absolute_paths)
    print(location.split(":")[0] + ": scope_hint: In function ‘" +
          frame["symbol"] + "’:")
    print_error_trace(report, Error.error, args, location)

    for frame in report["active stack"]:
        print(parse_location(frame["location"], args.absolute_paths)
                + ": note: " + frame["symbol"])

    separator = "\n"


def main(args: argparse.Namespace) -> None:
    for report in parse_reports(args.infile):
        try:
            report = yaml.load(report, Loader=CLoader)
            args.infile.close()
            process_report(args, report)
        except yaml.YAMLError as exc:
            print(exc, file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Divine to csgrep")
    parser.add_argument("-a", "--absolute-paths", action="store_true",
                        help="make all paths absolute")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="do not sanitise the error cause")
    parser.add_argument("infile", nargs="?", type=argparse.FileType("r"),
                        default=sys.stdin, help="input file (default: stdin)")

    main(parser.parse_args())
