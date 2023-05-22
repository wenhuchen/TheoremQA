from typing import Dict, Any
import os
import json
from tqdm import tqdm
from datetime import datetime
import openai
from time import sleep
import argparse
from util import extract_answer

parser = argparse.ArgumentParser()
parser.add_argument("--start", default=0, type=int)
parser.add_argument("--end", default=-1, type=int)
parser.add_argument("--answered", default=None, type=str)
parser.add_argument("--dry_run", default=False, action='store_true')

args = parser.parse_args()

def create_reader_request(example: Dict[str, Any]) -> str:
    string = f'Question: {example["Question"]}\nLet\'s think step by step.'
    return string

if __name__ == "__main__":

    with open('theoremqa_test.json', 'r') as f:
        test_set = json.load(f)

    filename = f'outputs/random_guess.jsonl'
    print(filename)

    writer = open(filename, 'w')
    inputs = []
    for example in tqdm(test_set):
        full_prompt = create_reader_request(example)
        if example['Answer_type'] == 'bool':
            prediction = 'True'
        elif example['Answer_type'] == 'option':
            prediction = '(a)'
        else:
            prediction = '1000'

        tmp = {
            'id': example['id'],
            'question': example['Question'],
            'prediction': prediction,
            'answer': example['Answer'],
            'answer_type': example['Answer_type'],
            }

        writer.write(json.dumps(tmp) + '\n')

    writer.close()
    print()
