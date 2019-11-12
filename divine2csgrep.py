#!/usr/bin/python3

import re
import sys
import yaml

if len(sys.argv) != 2:
    print("USAGE: % [DIVINE REPORT]" %(sys.argv[0]), file=sys.stderr)

with open(sys.argv[1], "r") as stream:
    try:
        report = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

with open(sys.argv[1] + ".csgrep", "w") as stream:
    if not report["error found"]:
        sys.exit(0)

    for frame in report["active stack"]:
        if "/opt/divine" in frame["location"]:
            continue
   
        key_location = frame["location"].split(":")
        print(key_location[0] + ": In funtion ‘" + frame["symbol"] + "’:", file=stream)
        
        key_location = key_location[0] + ":" + key_location[1]
        trace = report["error trace"].split("\n")
        trace.pop() # might break in future
        for line in trace:
            print(key_location + (": error: DIVINE " if line is trace[0] else ": note: ") + line, file=stream)

        print(key_location + ": note: backtrace:", file=stream)
        break

    for frame in report["active stack"]:
        location = frame["location"].split(":")
        print(location[0] + ":" + location[1] + ": note: " + frame["symbol"], file=stream)
