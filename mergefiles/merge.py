from os import listdir
from ast import literal_eval
import json

##
# Please make sure Files have either StateQualitiesX or VisitedX
# somewhere in the filename, where X is a unique number
##

files = listdir('Files')

ThreadQualities = []
ThreadVisited = []

for _ in range(0, int(len(files)/2)):
	ThreadQualities.append({})
	ThreadVisited.append({})

for f in files:
	if "StateQualities" in f:
		with open('Files/'+f, 'r') as infile:
			tmp = json.load(infile)
			for key, value in tmp.items():
				ThreadQualities[int(''.join([x for x in f if x.isdigit()]))][literal_eval(key)] = value
	elif "Visited" in f:
		with open('Files/'+f, 'r') as infile:
			tmp = json.load(infile)
			for key, value in tmp.items():
				ThreadVisited[int(''.join([x for x in f if x.isdigit()]))][literal_eval(key)] = value

## Average together all the values output from threads
StateQualities = {}
Visited = {}

for _ in range(0, len(files)):
	q = []
	v = []
	loopQualities = ThreadQualities.pop(0)
	loopVisited = ThreadVisited.pop(0)
	for key, value in loopQualities.items():
		if value == 0 or not key[0] in loopVisited.keys():
			continue
		for i in range(0, len(ThreadQualities)):
			if key in ThreadQualities[i].keys():
				x = ThreadQualities[i].pop(key)
				if x != 0:
					q.append(x)
					v.append(ThreadVisited[i][key[0]])
		totalV = sum(v) + loopVisited[key[0]]
		avgQ = value * (loopVisited[key[0]] / totalV)
		for i in range(0, len(q)):
			avgQ += q[i] * (v[i] / totalV)
		StateQualities[key] = avgQ
		if key[0] in Visited.keys():
			Visited[key[0]] += totalV
		else:
			Visited[key[0]] = totalV
		
with open('StateQualities.json', 'w') as outfile:
	tmp = {}
	for key, value in StateQualities.items():
		tmp[str(key)] = value
	json.dump(tmp, outfile)
with open('Visited.json', 'w') as outfile:
	tmp = {}
	for key, value in Visited.items():
		tmp[str(key)] = value
	json.dump(tmp, outfile)
