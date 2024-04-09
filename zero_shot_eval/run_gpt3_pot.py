from typing import Dict, Any
import os
import json
from tqdm import tqdm
from datetime import datetime
import openai
from time import sleep
import argparse
from util import extract_code, extract_answer, impossible_questions, postprocess_number
import func_timeout
import math  # import for code execution
import numpy  # import for code execution
import numpy as np  # import for code execution
import cmath

parser = argparse.ArgumentParser()
parser.add_argument("--start", default=0, type=int)
parser.add_argument("--end", default=-1, type=int)
parser.add_argument("--answered", default=None, type=str)
parser.add_argument("--dry_run", default=False, action='store_true')

args = parser.parse_args()

def create_reader_request(example: Dict[str, Any]) -> str:
    string = f'Question: {example["Question"]}\n'
    return string

def run_cot_prompt(full_prompt: str):
    SYSTEMQ = """You are a mathematician, you are supposed to answer the given question. You need to output the answer in your final sentence like "Therefore, the answer is ...". The answer can only be one of the following forms:
1. a numerical value like 0.1, no symbol and no unit at all.
2. a list of number like [2, 3, 4].
3. True/False.
4. an option like (a), (b), (c), (d)
"""
    full_prompt += "Let\'s think step by step."
    # greedy decoding
    got_result = False
    while not got_result:
        try:
            result = openai.Completion.create(
                engine='text-davinci-002',
                prompt=SYSTEMQ + full_prompt,
                max_tokens=1028,
                temperature=0.0,
                top_p=0.5,
                frequency_penalty=0,
                presence_penalty=0,
                best_of=1,
                stop=None)
            got_result = True
        except Exception as e:
            sleep(3)
    result = result['choices'][0]['text']
    return result

def run_pot_prompt(full_prompt: str):
    SYSTEMQ = """You are a mathematician, you are supposed to generate a Python program to answer the given question. The returned value of the program is supposed to be the answer. It should be integer or float or list of integer/float.
Question: What is the 50-th value of a fibonacci sequence?
def solve():
    # Let's write the program step by step
    # Let's define recursive fibonacci function
    def recur_fibo(n):
        if n <= 1:
            # define the base case
            return n
        else:
            # use the fibonacci recursive formula
            return(recur_fibo(n-1) + recur_fibo(n-2))
    return recur_fibo(50)

"""
    full_prompt += """def solve():
    # Let's write the program step by step
"""
    # greedy decoding
    got_result = False
    while not got_result:
        try:
            result = openai.Completion.create(
                engine='text-davinci-002',
                prompt=SYSTEMQ + full_prompt,
                max_tokens=1028,
                temperature=0.0,
                top_p=0.5,
                frequency_penalty=0,
                presence_penalty=0,
                best_of=1,
                stop=None)
            got_result = True
        except Exception as e:
            sleep(3)
    result = result['choices'][0]['text']
    return result


if __name__ == "__main__":
    openai.api_type = "azure"
    openai.api_base = "https://waterloogpt.openai.azure.com/"
    openai.api_version = "2022-12-01"
    openai.api_key = os.getenv('AZURE_KEY')

    with open('theoremqa_test.json', 'r') as f:
        test_set = json.load(f)

    answered_set = dict()
    if args.answered:
        with open(args.answered, 'r') as f:
            for line in f:
                answered_set[json.loads(line)['id']] = line.strip('\n')
    print('answered set:', len(answered_set))

    now = datetime.now()
    dt_string = now.strftime("%m_%d_%H_%M")

    correct, wrong = 0, 0
    if args.end == -1:
        test_set = test_set[args.start:]
    else:
        test_set = test_set[args.start : args.end]
    print(f'length of dataset: {len(test_set)}')

    filename = f'outputs/GPT3_PoT_s{args.start}_e{args.end}_{dt_string}.jsonl'
    print(filename)

    writer = open(filename, 'w')
    inputs = []
    for example in tqdm(test_set):
        full_prompt = create_reader_request(example)
        if args.dry_run:
            print(full_prompt)
            print('=======================')
            continue

        if answered_set and example['id'] in answered_set:
            writer.write(answered_set[example['id']] + '\n')
            continue

        if example['Answer_type'] in ['bool', 'option'] or example['id'] in impossible_questions:
            result = run_cot_prompt(full_prompt)
            prediction = extract_answer(result=result)
        else:
            result = run_pot_prompt(full_prompt)
            result = "def solve():\n" + result
            result = extract_code(result=result)
            try:
                exec(result)
                try:
                    prediction = func_timeout.func_timeout(10, solve, args=())
                except func_timeout.FunctionTimedOut:
                    prediction = None
            except Exception as e:
                print(e)
                prediction = None

        prediction = postprocess_number(prediction)

        print(result)
        print(prediction, ' $$$$$$$$$ ', example['Answer'])
        print()

        tmp = {
            'id': example['id'],
            'question': example['Question'],
            'prediction': prediction,
            'answer': example['Answer'],
            'rationale': result,
            'answer_type': example['Answer_type'],
            }

        writer.write(json.dumps(tmp) + '\n')

    writer.close()
    print()
