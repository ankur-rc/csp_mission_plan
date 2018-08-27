from constraint import Problem, AllDifferentConstraint, MinConflictsSolver


class Solver(object):

    problem = None
    pilots, missions, pilot_prefs = None, None, None
    uas_max = None

    # variables
    pilot_vars, mission_vars = [], []
    max_obj = 0

    def __init__(self, pilot_map=None, mission_map=None, uas_max=None, pilot_prefs=None):
        self.problem = Problem(MinConflictsSolver())
        self.pilots = pilot_map
        self.missions = mission_map
        self.uas_max = uas_max
        self.pilot_prefs = pilot_prefs

    def build_variables(self):

        # pilot-uas variable
        for key, val in self.pilots.iteritems():
            self.problem.addVariable(key, val)
            self.pilot_vars.append(key)

        # mission-uas variable
        for key, val in self.missions.iteritems():
            self.problem.addVariable(key, val)
            self.mission_vars.append(key)

    def build_constraints(self):

        # all pilots assigned to different
        self.problem.addConstraint(AllDifferentConstraint(), self.pilot_vars)

        # missions must be assigned uas only if a pilot has been assigned to it
        for mission in self.mission_vars:
            mission_and_all_pilots = [mission] + self.pilot_vars
            self.problem.addConstraint(
                self.__assign__mission_from_assigned_pilots_only, mission_and_all_pilots)

        # no uas can be assigned to more than 3 missions
        self.problem.addConstraint(self.__limit_mission_uas, self.mission_vars)

    def __assign__mission_from_assigned_pilots_only(self, *mission_and_all_pilots):
        mission = mission_and_all_pilots[0]
        i = 1
        for i in range(1, len(mission_and_all_pilots)):
            if mission == mission_and_all_pilots[i]:
                return True
        return False

    def __limit_mission_uas(self, *missions):
        mission_count = {}
        for i in range(0, self.uas_max+1):
            mission_count[i] = 0

        for mission in missions:
            mission_count[mission] += 1

        for val in mission_count.itervalues():
            if val > 3:
                return False
        return True

    def get_solution(self):
        return self.problem.getSolution()
