from os import listdir
from ast import literal_eval
import json

files = listdir('Files')

ThreadQualities = []
ThreadVisited = []
for f in files:
	with open('Files/'+f, 'r') as infile:
		tmp = json.load(infile)
		ThreadQualities.append({})
		for key, value in tmp.items():
			ThreadQualities[-1][literal_eval(key)] = value

	with open('Files/'+f, 'r') as infile:
		tmp = json.load(infile)
		ThreadVisited.append({})
		for key, value in tmp.items():
			ThreadVisited[-1][literal_eval(key)] = value

## Average together all the values output from threads
StateQualities = {}
Visited = {}

for _ in range(0, len(files)):
	q = []
	v = []
	loopQualities = ThreadQualities.pop(0)
	loopVisited = ThreadVisited.pop(0)
	for key, value in loopQualities.items():
		if value == 0:
			continue
		for i in range(0, len(ThreadQualities)):
			if key in ThreadQualities[i].keys():
				x = ThreadQualities[i].pop(key)
				if x != 0:
					q.append(x)
					v.append(ThreadVisited[i][key[0]])
		totalV= sum(v) + loopVisited[key[0]]
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
