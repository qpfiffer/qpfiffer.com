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
        possible_date = re.match(r'\* ([0-9\/]+):', line)
        if possible_date is None:
            raise Exception("Could not parse line: {}".format(line))
        self.current_date = possible_date.groups(0)[0]
        self.state = "PARSING_DATE"
        self.lifts_by_date[self.current_date] = {}

    def _parse_lifts(self, line):
        if line.startswith("    ") and "*" in line:
            split_line = line.strip().rstrip().split(": ")
            possible_lift = re.match(r'\* ([a-zA-Z()\ -]+)', split_line[0])
            self.current_lift = possible_lift.groups(0)[0].lower()
            if self.current_lift == "meta":
                return
            #print("LIFT: {}".format(self.current_lift))
            if self.lifts_by_exercise.get(self.current_lift) is None:
                self.lifts_by_exercise[self.current_lift] = {}

            try:
                for sets_by_reps_by_weight in split_line[1].split(", "):
                    print("SRW: {}".format(sets_by_reps_by_weight))
            except IndexError:
                return
        elif "*" not in line:
            return
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
