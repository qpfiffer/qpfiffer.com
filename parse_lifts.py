#!/usr/bin/env python3
import json, re, sys

INFILE = "./wiki/lifting.markdown"

class Parser(object):
    def __init__(self):
        self.state = "UNSARTED"
        self.current_date = None
        self.lifts_by_date = {}
        self.lifts_by_exercise = {}
        self.lifts_by_reps = {}
        self.lifts_by_sets = {}
        self.lifts_by_weight = {}

    def dump_data(self):
        obj = {
            "liftsByDate": self.lifts_by_date,
            "liftsByExercise": self.lifts_by_exercise,
            "liftsByReps": self.lifts_by_reps,
            "liftsBySets": self.lifts_by_sets,
            "liftsByWeight": self.lifts_by_weight
        }
        sys.stdout.write(json.dumps(obj))

    def _parse_started(self, line):
        self.current_date = re.match(r'\* ([0-9\/]+):', line).groups(0)[0]
        self.state = "PARSING_DATE"
        self.lifts_by_date[self.current_date] = {}

    def _parse_lifts(self, line):
        if line.startswith("    ") and "*" in line:
            pass
        else:
            self.state = "STARTED"
            return self._parse_started(line)

    def parse_line(self, line):
        if self.state == "UNSARTED" and line == ";;START\n":
            self.state = "STARTED"
            return

        if self.state == "STARTED":
            return self._parse_started(line)
        elif self.state == "PARSING_DATE":
            return self._parse_lifts(line)

def main():
    parser = Parser()
    with open(INFILE) as lift_file:
        for line in lift_file:
            parser.parse_line(line)

    parser.dump_data()

if __name__ == '__main__':
    main()
