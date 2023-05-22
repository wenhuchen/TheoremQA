import openai
from time import sleep
import csv
import json
import os
import tqdm

def run_prompt(theorem_name: str):
    SYSTEMQ = f"Can you describe {theorem_name}?"
    got_result = False
    while not got_result:
        try:
            result = openai.ChatCompletion.create(
                model='gpt-4-0314',
                messages=[{"role": "system", "content": ""},
                          {"role": "user", "content": SYSTEMQ}],
                max_tokens=1028,
                temperature=0.0,
                top_p=1,
                n=1,
            )
            got_result = True
        except Exception as e:
            sleep(3)
    result = result['choices'][0]['message']['content']
    return result

if __name__ == "__main__":
    openai.api_key = os.getenv('OPENAI_KEY')

    writer = open('theorems.jsonl', 'w')
    """
    with open('Math_Theorem.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for i, row in tqdm.tqdm(enumerate(reader)):
            if i > 0:
                theorem_name = row[0].split('(')[0].strip()
                output = run_prompt(row[0])
                tmp = {'theorem': theorem_name, 'output': output}
                writer.write(json.dumps(tmp) + '\n')
    """
    with open('EECS_Theorem.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for i, row in tqdm.tqdm(enumerate(reader)):
            if i > 0:
                theorem_name = row[0].split('(')[0].strip()
                output = run_prompt(row[0])
                tmp = {'theorem': theorem_name, 'output': output}
                writer.write(json.dumps(tmp) + '\n')    
    with open('Physics_Theorem.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for i, row in tqdm.tqdm(enumerate(reader)):
            if i > 0:
                theorem_name = row[0].split('(')[0].strip()
                output = run_prompt(row[0])
                tmp = {'theorem': theorem_name, 'output': output}
                writer.write(json.dumps(tmp) + '\n')
    with open('Finance_Theorem.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for i, row in tqdm.tqdm(enumerate(reader)):
            if i > 0:
                theorem_name = row[0].split('(')[0].strip()
                output = run_prompt(row[0])
                tmp = {'theorem': theorem_name, 'output': output}
                writer.write(json.dumps(tmp) + '\n')
    writer.close()