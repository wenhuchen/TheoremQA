import csv
import json

with open('theoremqa_test.json') as f:
	data = json.load(f)

with open('all_theorems.json') as f:
	all_theorem = json.load(f)
	all_theorem = {k.lower(): v for k, v in all_theorem.items()}

fields = list(data[0].keys())

with open('test.csv', 'w') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(fields + ['theorem_def'])
	for line in data:
		if line['Picture'] is None:
			line['Picture'] = 'NONE'
		entry_list = [line[e] for e in fields]
		entry_list.append(all_theorem[line['theorem'].lower()])
		writer.writerow(entry_list)
