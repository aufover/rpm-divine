#!/usr/bin/python3

import sys
import yaml


def main():
    if len(sys.argv) != 2:
        print("USAGE: %s [DIVINE REPORT]" % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    in_file = sys.stdin if sys.argv[1] == "-" else open(sys.argv[1], "r")

    try:
        report = yaml.safe_load(in_file)
    except yaml.YAMLError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    if not report["error found"]:
        return

    if report["error found"] == "boot":
        trace = report["error trace"].split("\n")
        trace.pop()  # might break in future

        for line in trace:
            print(report["input file"] +
                  (": error: DIOS BOOT: " if line is trace[0]
                   else ": note: DIOS BOOT: ") + line)
        return

    for frame in report["active stack"]:
        if "/opt/divine/" in frame["location"]:
            continue

        location = frame["location"].split(":")
        print(location[0] + ": In funtion ‘" + frame["symbol"] + "’:")

        location = location[0] + ":" + location[1]
        trace = report["error trace"].split("\n")
        trace.pop()  # might break in future

        for line in trace:
            print(location + (": error: DIVINE " if line is trace[0]
                              else ": note: ") + line)

        print(location + ": note: backtrace:")
        break

    for frame in report["active stack"]:
        location = frame["location"].split(":")
        print(location[0] + ":" + location[1] + ": note: " + frame["symbol"])

    in_file.close()

if __name__ == "__main__":
    main()
