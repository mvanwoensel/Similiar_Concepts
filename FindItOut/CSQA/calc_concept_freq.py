import numpy as np


easy_file = "easy_game_boards.txt"
medium_file = "medium_game_boards.txt"

"""
@filename = name of text file where to read concepts from
@output = name of file to write output to

Reads a file of concepts and writes a sorted list in descending order of frequency to the output file
"""
def calc_entity_freq(filename, output):
	f = open(filename)
	concept_ct = {}
	for line in f:
		line = line.strip().split("|")
		for concept in line:
			if concept not in concept_ct:
				concept_ct[concept] = 0
			concept_ct[concept] += 1
	f.close()
	concept_ct_list = [(concept, concept_ct[concept]) for concept in concept_ct]
	concept_ct_list.sort(key=lambda x:x[1], reverse=True)
	f = open(output, "w")
	for concept, ct in concept_ct_list:
		f.write("%s\t%d\n"%(concept, ct))
	f.close()

# not sure where these files are located when i try to look them up i cannot find them.
calc_entity_freq(easy_file, "easy_entity_freq.txt")
calc_entity_freq(medium_file, "medium_entity_freq.txt")


