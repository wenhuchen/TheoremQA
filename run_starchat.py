from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from tqdm import tqdm
import argparse
from datetime import datetime
from datasets import Dataset
from torch.utils.data import DataLoader
from util import extract_code, postprocess_number
import torch
import re
import func_timeout
import numpy as np  # for code execution
import numpy  # for code execution
import sympy  # for code execution

parser = argparse.ArgumentParser()
parser.add_argument("--start", default=0, type=int)
parser.add_argument("--end", default=-1, type=int)
parser.add_argument("--byte", default=False, action='store_true')
parser.add_argument("--bs", default=4, type=int)

args = parser.parse_args()

def generate_data(test_set):
    for example in test_set:
        question = example['Question']
        if example['Answer_type'] == 'bool':
            prompt = f"""<|system|>
You are a mathematician, you need to implement a Python function `solve()' to solve the math question.
<|end|>
<|user|>
{question}
<|end|>
<|assistant|>
Let's write a Python function `solve()' to return the answer as True or False.
```Python
"""
        elif example['Answer_type'] == 'option':
            prompt = f"""<|system|>
You are a mathematician, you need to implement a Python function `solve()' to solve the math question.
<|end|>
<|user|>
{question}
<|end|>
<|assistant|>
Let's write a Python function `solve()' to return the (a), (b), (c) or (d).
```Python
"""
        else:
            prompt = f"""<|system|>
You are a mathematician, you need to implement a Python function `solve()' to solve the math question.
<|end|>
<|user|>
{question}
<|end|>
<|assistant|>
Let's write a Python function `solve()' to return the answer.
```Python
"""
        del example['Answer']
        del example['Picture']
        example['prompt'] = prompt
        yield example


if __name__ == "__main__":
    device = "cuda"  # for GPU usage or "cpu" for CPU usage

    with open('theoremqa_test.json', 'r') as f:
        test_set = json.load(f)
    if args.end == -1:
        test_set = test_set[args.start:]
    else:
        test_set = test_set[args.start:args.end]
    print(f'length of dataset: {len(test_set)}')

    answer_mapping = {}
    for entry in test_set:
        answer_mapping[entry['id']] = entry['Answer']

    ds = Dataset.from_generator(lambda: generate_data(test_set))
    dataloader = DataLoader(ds, batch_size=args.bs)

    model_name = 'HuggingFaceH4/starchat-alpha'

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.padding_side = 'left'
    tokenizer.pad_token = tokenizer.eos_token

    if args.byte:
        model = AutoModelForCausalLM.from_pretrained(model_name, load_in_8bit=True, device_map="auto")
    else:
        model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16)

    now = datetime.now()
    dt_string = now.strftime("%m_%d_%H_%M")

    correct, wrong = 0, 0
    filename = f'outputs/starchat_s{args.start}_e{args.end}_{dt_string}.jsonl'
    writer = open(filename, 'w')

    for entry in tqdm(dataloader):
        batch = tokenizer(entry['prompt'], return_tensors="pt", add_special_tokens=False, padding=True)
        batch = {k: v.to('cuda') for k, v in batch.items()}
        # Generate the model output
        outputs = model.generate(
            input_ids=batch['input_ids'],
            attention_mask=batch['attention_mask'],
            pad_token_id=tokenizer.eos_token_id,
            do_sample=False,
            max_new_tokens=200,
        )
        for i, sequence in enumerate(outputs):
            sequence = sequence[batch['input_ids'].shape[1]:].tolist()
            if tokenizer.eos_token_id in sequence:
                sequence = sequence[:sequence.index(tokenizer.eos_token_id)]
            result = tokenizer.decode(sequence, skip_special_tokens=True).strip()
            result = extract_code(result=result)
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

            print(result)
            print(prediction, ' $$$$$$$$$ ', answer_mapping[entry['id'][i]])
            print()

            tmp = {
                'id': entry['id'][i],
                'question': entry['Question'][i],
                'prediction': prediction,
                'answer': answer_mapping[entry['id'][i]],
                'rationale': result,
                'answer_type': entry['Answer_type'][i],
                }

            writer.write(json.dumps(tmp) + '\n')

    writer.close()
    print()
