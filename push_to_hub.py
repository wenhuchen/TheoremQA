import csv
import json
from PIL import Image
import datasets

with open('theoremqa_test.json') as f:
	data = json.load(f)

all_items = []
for line in data:
	if line['Picture'] is None:
		picture = None
	else:
		picture = Image.open(line['Picture'])
	all_items.append(
		{'Question': line['Question'], 
		'Answer': str(line['Answer']), 
		'Answer_type': line['Answer_type'], 
		'Picture': picture}
		)

data = datasets.Dataset.from_list(all_items)

data.push_to_hub('wenhu/TheoremQA', split='test')
data.push_to_hub('TIGER-Lab/TheoremQA', split='test')