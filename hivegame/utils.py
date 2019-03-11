""" def debug_possible_actions:
        print("-------------------------")
        print(sorted(self.hive.get_all_possible_actions(), key=lambda k: str(k[0])))
        print("-------------------------")

def adjacent_pretty_print(self, matrix):
    #pprint(self.hive.get_adjacency_state())
    print("DEBUG")
    adja_state = self.get_adjacency_state()
    for key, row in adja_state.items():
        print(key + ":", end=" ")
        pprint(row.values())
    print("----------------------------") """