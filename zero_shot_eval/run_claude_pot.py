from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import os
import json
import argparse
from datetime import datetime
from util import extract_code, postprocess_number
import func_timeout

parser = argparse.ArgumentParser()
parser.add_argument("--start", default=0, type=int)
parser.add_argument("--end", default=-1, type=int)
parser.add_argument("--version", default="v1", type=str)
parser.add_argument("--answered", default=None, type=str)

args = parser.parse_args()

if args.version == 'v1':
    MODLE_NAME = 'claude-v1'
elif args.version == 'v2':
    MODLE_NAME = 'claude-2'
elif args.version == 'instant':
    MODLE_NAME = 'claude-instant'
else:
    raise ValueError(args.version)

SUFFIX = """I'm writing a Python program to solve the question. Let's implement a function solve(), where the returned value is supposed to be the answer.
```Python
# import library
"""

def run_claude(full_prompt: str, answer_type: bool):
    if answer_type == 'option':
        prompt=f"{HUMAN_PROMPT} Question: {full_prompt} \n Please think step by step, and then conclude the answer as `therefore, the answer is (a)/(b)/(c)/(d)'. {AI_PROMPT}",
    elif answer_type == 'bool':
        prompt=f"{HUMAN_PROMPT} Question: {full_prompt} \n Please think step by step, and then conclude the answer as `therefore, the answer is True/False' {AI_PROMPT}",
    else:
        prompt=f"{HUMAN_PROMPT} Question: {full_prompt} {AI_PROMPT} {SUFFIX}",

    client = Anthropic(api_key=os.environ["CLAUDE_KEY"])
    response = client.completions.create(
        model=MODLE_NAME,
        max_tokens_to_sample=1024,
        prompt=prompt,
    )
    return response.completion


def main():
    now = datetime.now()
    dt_string = now.strftime("%m_%d_%H_%M")

    with open('theoremqa_test.json', 'r') as f:
        test_set = json.load(f)

    answered_set = dict()
    if args.answered:
        with open(args.answered, 'r') as f:
            for line in f:
                answered_set[json.loads(line)['id']] = line.strip('\n')
    print('answered set:', len(answered_set))

    if args.end == -1:
        test_set = test_set[args.start:]
    else:
        test_set = test_set[args.start : args.end]

    filename = f'outputs/Claude_PoT_s{args.start}_e{args.end}_{dt_string}.jsonl'
    writer = open(filename, 'w')
    for example in test_set:

        if answered_set and example['id'] in answered_set:
            writer.write(answered_set[example['id']] + '\n')
            continue        

        result = run_claude(example['Question'], example['Answer_type'])
        
        prediction = ''
        if example['Answer_type'] in ['bool', 'option']:
            for sent in result.split('\n')[::-1]:
                if example['Answer_type'] == 'bool':
                    if 'true' in sent.lower() or 'correct' in sent.lower():
                        prediction = 'True'
                        break
                    if 'false' in sent.lower() or 'wrong' in sent.lower():
                        prediction = 'False'
                        break
                else:
                    if '(a)' in sent.lower() or '(b)' in sent.lower() or '(c)' in sent.lower() or '(d)' in sent.lower():
                        prediction = sent
                        break
        else:
            result = extract_code(result=result)
            print(result)
            try:
                exec(result, globals())
                try:
                    prediction = func_timeout.func_timeout(10, solve, args=())
                except func_timeout.FunctionTimedOut:
                    prediction = None
            except Exception as e:
                print(e)
                prediction = None

            # Convert the result to string
            if prediction is not None:
                prediction = str(prediction)
            else:
                prediction = ''

        prediction = postprocess_number(prediction)

        tmp = {
            'id': example['id'],
            'question': example['Question'],
            'answer': example['Answer'],
            'rationale': result,
            'prediction': prediction,
            'answer_type': example['Answer_type'],
            }
        
        writer.write(json.dumps(tmp) + '\n')

    writer.close()
    print()


if __name__ == "__main__":
    main()
