from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from tqdm import tqdm
import argparse
from datetime import datetime
from datasets import Dataset
from torch.utils.data import DataLoader
import torch
import re

parser = argparse.ArgumentParser()
parser.add_argument("--start", default=0, type=int)
parser.add_argument("--end", default=-1, type=int)
parser.add_argument("--byte", default=False, action='store_true')
parser.add_argument("--model", default=None, type=str)
parser.add_argument("--model_path", default=None, type=str)
parser.add_argument("--bs", default=4, type=int)

args = parser.parse_args()

def generate_data(test_set):
    for example in test_set:
        if args.model in ['alpaca', 'vicuna']:
            if example['Answer_type'] in ['bool']:
                instruction = "Please read a math problem, and then think step by step to derive the answer. The answer needs to be True or False."
            elif example['Answer_type'] in ['option']:
                instruction = "Please read a math problem, and then think step by step to derive the answer. The answer needs to be (a), (b), (c) or (d)."
            else:
                instruction = "Please read a math problem, and then think step by step to derive the answer. The answer needs to be in numerical form."

            question = example['Question']
            prompt = f"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Input:\n{question}\n\n### Response:\n"
        elif args.model in ['pythia']:
            if example['Answer_type'] in ['bool']:
                instruction = "Please think step by step and then answer `Therefore, the answer is True/False'."
            elif example['Answer_type'] in ['option']:
                instruction = "Please think step by step to derive the answer. The answer should be (a), (b), (c) or (d)."
            else:
                instruction = "Please think step by step to derive the answer in deciaml form."

            question = example['Question']
            prompt = f"<|prompter|>{question} {instruction} <|endoftext|><|assistant|>"
        else:
            raise NotImplementedError('The big model is not implement')

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

    if args.model == 'alpaca':
        model_name = 'chavinlo/alpaca-13b'
    elif args.model == 'vicuna':
        model_name = args.model_path
    elif args.model == 'pythia':
        model_name = 'OpenAssistant/oasst-sft-1-pythia-12b'
    else:
        raise ValueError('the model type is not supported')

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
    filename = f'outputs/{args.model}_s{args.start}_e{args.end}_{dt_string}.jsonl'
    writer = open(filename, 'w')

    for entry in tqdm(dataloader):
        batch = tokenizer(entry['prompt'], return_tensors="pt", add_special_tokens=False, padding=True)
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model.generate(
            input_ids=batch['input_ids'],
            attention_mask=batch['attention_mask'],
            pad_token_id=tokenizer.eos_token_id,
            do_sample=False,
            max_new_tokens=1024,
        )
        for i, sequence in enumerate(outputs):
            sequence = sequence[batch['input_ids'].shape[1]:]
            result = tokenizer.decode(sequence, skip_special_tokens=True).strip()
            result = result.replace('</s><s>', '')
            prediction = None
            for sent in result.split('\n')[::-1]:
                if entry['Answer_type'] == 'bool':
                    if len(sent) < 2:
                        continue
                    else:
                        if 'true' in sent.lower() or 'correct' in sent.lower():
                            prediction = 'True'
                        elif 'false' in sent.lower() or 'wrong' in sent.lower():
                            prediction = 'False'
                        elif ' not ' in sent.lower() or "n't " in sent.lower():
                            prediction = 'False'
                        else:
                            prediction = 'True'
                        break
                elif entry['Answer_type'] == 'option':
                    if '(a)' in sent.lower() or '(b)' in sent.lower() or '(c)' in sent.lower() or '(d)' in sent.lower():
                        prediction = sent
                        break
                else:
                    if ' is ' in sent.lower() or ' be ' in sent.lower() or ' are ' in sent.lower() or ' is: ' in sent.lower():
                        prediction = re.split(' be | is | are | is: ', sent)[-1].strip('.')
                        break
                    elif re.search('[0-9]', sent):
                        prediction = sent
                        break
                    else:
                        continue

            if prediction is None:
                print(result)

            tmp = {
                'id': entry['id'][i],
                'question': entry['Question'][i],
                'prediction': prediction,
                'answer': answer_mapping[entry['id'][i]],
                'rationale': result,
                'answer_type': entry['Answer_type'][i],
                }

            print(result)
            print('-------------------------')
            writer.write(json.dumps(tmp) + '\n')

    writer.close()
    print()
