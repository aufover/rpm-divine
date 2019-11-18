#!/usr/bin/python3

import sys
import yaml


def main():
    if len(sys.argv) != 2:
        print("USAGE: %s [DIVINE REPORT]" % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r") as stream:
        try:
            report = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc, file=sys.stderr)
            sys.exit(1)

    with open(sys.argv[1] + ".csgrep", "w") as stream:
        if not report["error found"]:
            return

        if report["error found"] == "boot":
            trace = report["error trace"].split("\n")
            trace.pop()  # might break in future
            for line in trace:
                print(report["input file"] +
                      (": error: DIOS BOOT: " if line is trace[0]
                       else ": note: DIOS BOOT: ") + line, file=stream)
            return

        for frame in report["active stack"]:
            if "/opt/divine/" in frame["location"]:
                continue

            location = frame["location"].split(":")
            print(location[0] + ": In funtion ‘" +
                  frame["symbol"] + "’:", file=stream)

            location = location[0] + ":" + location[1]
            trace = report["error trace"].split("\n")
            trace.pop()  # might break in future
            for line in trace:
                print(location + (": error: DIVINE " if line is trace[0]
                                  else ": note: ") + line, file=stream)

            print(location + ": note: backtrace:", file=stream)
            break

        for frame in report["active stack"]:
            location = frame["location"].split(":")
            print(location[0] + ":" + location[1] +
                  ": note: " + frame["symbol"], file=stream)


if __name__ == "__main__":
    main()
