import json
import sys

filename = sys.argv[1]

mapping = {}
with open('theoremqa_test.json', 'r') as f:
    orig_data = json.load(f)
    for entry in orig_data:
        mapping[entry['id']] = entry

subfield_rate = {}
with open(filename) as f:
    data = json.load(f)
    for entry in data:
        if mapping[entry['id']]['field'] not in subfield_rate:
            subfield_rate[mapping[entry['id']]['field']] = {'correct': 0, 'wrong': 0}

        if entry['correct']:
            subfield_rate[mapping[entry['id']]['field']]['correct'] += 1
        else:
            subfield_rate[mapping[entry['id']]['field']]['wrong'] += 1

for key in subfield_rate:
    subfield_rate[key] = subfield_rate[key]['correct'] / (subfield_rate[key]['correct'] + subfield_rate[key]['wrong'])

for key, value in subfield_rate.items():
    print(key, ',', round(value, 3))
print('----------------------------------------------------')

answer_type_rate = {'integer': {'correct': 0, 'wrong': 0},
                    'float': {'correct': 0, 'wrong': 0},
                    'option': {'correct': 0, 'wrong': 0},
                    'list': {'correct': 0, 'wrong': 0},
                    'bool': {'correct': 0, 'wrong': 0},
                    'all': {'correct': 0, 'wrong': 0}}

with open(filename) as f:
    data = json.load(f)
    for entry in data:
        answer_type = entry['answer_type'] if 'answer_type' in entry else entry['Answer_type']
        if answer_type.startswith('list'):
            answer_type = 'list'

        if entry['correct']:
            answer_type_rate[answer_type]['correct'] += 1
            answer_type_rate['all']['correct'] += 1
        else:
            answer_type_rate[answer_type]['wrong'] += 1
            answer_type_rate['all']['wrong'] += 1

print(answer_type_rate)
for key in answer_type_rate:
    answer_type_rate[key] = answer_type_rate[key]['correct'] / (answer_type_rate[key]['correct'] + answer_type_rate[key]['wrong'])

for key, value in answer_type_rate.items():
    print(key, ',', round(value, 3))
print('----------------------------------------------------')

mapping = {}
with open('theoremqa_test.json', 'r') as f:
    orig_data = json.load(f)
    for entry in orig_data:
        mapping[entry['id']] = entry

subfield_rate = {}
with open(filename) as f:
    data = json.load(f)
    for entry in data:
        if mapping[entry['id']]['subfield'] not in subfield_rate:
            subfield_rate[mapping[entry['id']]['subfield']] = {'correct': 0, 'wrong': 0}

        if entry['correct']:
            subfield_rate[mapping[entry['id']]['subfield']]['correct'] += 1
        else:
            subfield_rate[mapping[entry['id']]['subfield']]['wrong'] += 1

for key in subfield_rate:
    subfield_rate[key] = subfield_rate[key]['correct'] / (subfield_rate[key]['correct'] + subfield_rate[key]['wrong'])

for key, value in subfield_rate.items():
    print(key, ',', round(value, 2))
print('----------------------------------------------------')


image_questions = set()
with open('theoremqa_test.json', 'r') as f:
    orig_data = json.load(f)
    for entry in orig_data:
        if entry['Picture'] is not None:
            image_questions.add(entry['id'])
print(len(image_questions))

correct, fail = 0, 0
with open(filename) as f:
    data = json.load(f)
    for entry in data:
        if entry['id'] in image_questions:
            if entry['correct']:
                correct += 1 
            else:
                fail += 1
print('image question accuracy:', correct / (correct + fail))
