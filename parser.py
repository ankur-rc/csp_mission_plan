import re


class FileParser(object):

    n_uas, uas_count, uas_names, missions, mission_type_map, pilot_map = [], 0, [], [], {}, {}
    uas_index_to_instance_map, pilot_domain_map, pilot_pref_map, mission_domain_map, uas_instance_count = {}, {}, {}, {}, 0

    # line parsers
    def transform_uas_vector_to_int_list(self, vector):
        uas_list = []
        i = 0
        for bit in vector:
            if bit == "1":
                uas_list.append(i)
            i += 1
        return uas_list

    def get_pref_from_uas_vector(self, vector):
        pref = None
        i = 0
        for bit in vector:
            if bit == "1":
                pref = i
                break
            i += 1
        return pref

    # file parser
    def __init__(self, filepath=None):

        comment_pattern = re.compile("(^%)")
        mt_pattern = re.compile("(^MT )")
        mission_pattern = re.compile("(^M )")
        pilot_pattern = re.compile("(^P )")
        nuas_pattern = re.compile("(^NUAS )")

        with open(filepath, 'r') as f:
            for line in f:
                if comment_pattern.match(line):
                    #print "comment:", line
                    pass

                elif mt_pattern.match(line):
                    #print "mt:", line
                    mt = line.split()[1]
                    uas_list = self.transform_uas_vector_to_int_list(
                        list(line.split()[2]))
                    self.mission_type_map[mt] = uas_list

                elif mission_pattern.match(line):
                    #print "mission:", line
                    self.missions.append(line.split()[2])

                elif pilot_pattern.match(line):
                    #print "pilot:", line
                    pilot = line.split()[1]
                    uas_list = self.transform_uas_vector_to_int_list(
                        list(line.split()[2]))
                    pref = self.get_pref_from_uas_vector(list(line.split()[3]))
                    self.pilot_map[pilot] = {
                        "compat": uas_list,
                        "pref": pref
                    }

                elif nuas_pattern.match(line):
                    #print "nuas:", line
                    self.n_uas = map(lambda num: int(
                        num), list(line.split()[1]))

                else:
                    self.uas_names.append(line.strip())

            self.uas_count = len(self.n_uas)

        #print self.n_uas, "\n", self.pilot_map, "\n", self.mission_type_map, "\n", self.uas_types, "\n", self.missions

    # mappers
    def create_uas_index_to_instance_map(self):
        k = 0
        for i in range(0, self.uas_count):
            uas_instances = []
            for j in range(0, self.n_uas[i]):
                uas_instances.append(k)
                k += 1
            self.uas_index_to_instance_map[i] = uas_instances
        self.uas_instance_count = k
        return self.uas_index_to_instance_map

    def get_uas_index_from_instance(self, instance):
        rolling_sum = 0
        i = 0
        for i in range(0, self.uas_count):
            rolling_sum += self.n_uas[i]
            if rolling_sum > instance:
                return i

        raise Exception('UAS instance is out-of-bounds!')

    def get_uas_names(self):
        return self.uas_names

    def get_domain_for_missions(self):
        for i in range(0, len(self.missions)):
            mt = self.missions[i]
            uas_list = self.mission_type_map[mt]
            uas_instances = []
            for uas in uas_list:
                uas_instances += self.uas_index_to_instance_map[uas]
            self.mission_domain_map[i] = uas_instances

        return self.mission_domain_map

    def get_domain_for_pilots(self):
        for pilot in self.pilot_map.iterkeys():
            uas_prefs = self.pilot_map[pilot]
            uas_list = uas_prefs["compat"]
            uas_list.append(uas_prefs["pref"])
            uas_list = set(uas_list)
            uas_instances = []
            for uas in uas_list:
                uas_instances += self.uas_index_to_instance_map[uas]
            self.pilot_domain_map[pilot] = uas_instances
            self.pilot_pref_map[pilot] = self.uas_index_to_instance_map[uas_prefs["pref"]]

        return self.pilot_domain_map, self.pilot_pref_map

    def get_uas_instance_count(self):
        return self.uas_instance_count


def main():
    parser = FileParser(filepath='sample3.txt')

    parser.create_uas_index_to_instance_map()
    parser.get_domain_for_missions()
    print parser.get_domain_for_pilots()


if __name__ == "__main__":
    main()
