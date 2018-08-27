from sys import argv
import os
import threading
import time

from solver import Solver
from parser import FileParser


def main():

    ip_file = None
    myargs = getopts(argv)
    if "-f" in myargs:
        ip_file = myargs["-f"]
    else:
        print "Usage: python mission_assign.py -f <input file>"
        exit()

    op_file = ip_file.split(".")[0]+"_output.txt"

    # create parser object
    parser = FileParser(filepath=ip_file)

    # flatten the uas indices into instances, taking into account uas count per uas
    parser.create_uas_index_to_instance_map()
    # setup mission map where each entry is a mission id - compatible uas list map.
    missions = parser.get_domain_for_missions()
    # setup pilot map where each entry is a pilot name - compatible uas list map.
    pilots, pilots_pref = parser.get_domain_for_pilots()
    uas_max = parser.get_uas_instance_count()
    uas_names = parser.get_uas_names()

    # create the solver object
    solver = Solver(pilot_map=pilots, mission_map=missions,
                    uas_max=uas_max, pilot_prefs={})

    # build the domain variables
    solver.build_variables()
    # build the constraints
    solver.build_constraints()

    # start the timer for 90 seconds
    t = threading.Timer(90.0, timeout)
    t.start()
    # solve the 'problem'
    solution = solver.get_solution()
    # solution was found, timer can be stopped
    t.cancel()

    if solution:

        # pretty print logic follows
        print "Solution found! Writing to file..."+op_file
        pretty_map = {}
        for key, value in solution.iteritems():
            if type(key) == int:
                if value in pretty_map:
                    pretty_map[value]["mission"].append(key)
                else:
                    pretty_map[value] = {
                        "mission": [key],
                        "pilot": None,
                        "uas": uas_names[parser.get_uas_index_from_instance(value)],
                        "fav": None
                    }

        sorted_pretty_list = [None]*len(missions)

        for key, value in solution.iteritems():
            if type(key) != int:
                pretty_map[value]["pilot"] = key
                pretty_map[value]["fav"] = "Yes" if value in pilots_pref[key] else "No"

        for uas, value in pretty_map.iteritems():
            missions = value["mission"]
            for mission in missions:
                sorted_pretty_list[mission] = str(
                    "M"+str(mission+1) + " " + value["pilot"] + " " + value["uas"] + " " + value["fav"])

        with open(op_file, 'w') as f:
            for assignment in sorted_pretty_list:
                f.write(assignment+"\n")
                print assignment
    else:
        print "No solution found!"
        with open(op_file, 'w') as f:
            f.write("No solution found!"+"\n")


# to get command-line parmas
def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            opts[argv[0]] = argv[1]
        argv = argv[1:]
    return opts


def timeout():
    print "Program timeout! No solution was found!"
    os._exit(1)


if __name__ == "__main__":
    main()
