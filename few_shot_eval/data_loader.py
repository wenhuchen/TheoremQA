import json


def load_dataset():
    questions = []
    answers = []
    with open('../theoremqa_test.json') as f:
        test_set = json.load(f)
        for row in test_set:
            questions.append(row['Question'])
            if isinstance(row['Answer'], bool):
                answers.append([str(row['Answer']), None])
            elif isinstance(row['Answer'], (list, int, float)):
                answers.append([str(row['Answer']), row['Answer']])
            else:
                answers.append([str(row['Answer']), None])
    return questions, answers


def get_prompt(qas: list, form: str):
    if form == 'alpaca':
        prompt_no_input, prefix = get_alpaca_format_prompt_wo_input(qas)
    elif form == 'alpaca_mc':
        prompt_no_input, prefix = get_alpaca_format_mc_prompt_wo_input(qas)
    elif form == 'vicuna':
        prompt_no_input, prefix = get_vicuna_format_prompt(qas)
    elif form == 'short':
        prompt_no_input, prefix = get_short_format(qas)
    elif form == 'step':
        prompt_no_input, prefix = get_short_formt_step_by_step(qas)
    elif form == 'tulu':
        prompt_no_input, prefix = get_tulu_format_prompt(qas)
    elif form == 'guanaco':
        prompt_no_input, prefix = get_Guanaco_format_prompt(qas)
    elif form == 'llama2chat':
        prompt_no_input, prefix = get_Guanaco_format_prompt(qas)
    elif form == 'gemma':
        prompt_no_input, prefix = get_gemma_wo_input(qas)
    elif form == 'mistral':
        prompt_no_input, prefix = get_mistral_wo_input(qas)
    else:
        raise NotImplementedError(form)

    return  prompt_no_input, prefix


def get_tulu_format_prompt(qas: list):
    tmp = ""
    for q, a in qas:
        tmp += '<|user|>\n{query}\n <|assistant|>\nThe answer is: {response}\n'.format(query=q, response=a)
    prefix = '<|user|>\n{query}\n<|assistant|>\nThe answer is: '

    return tmp, prefix


def get_vicuna_format_prompt(qas: list):
    tmp = (
        "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions."
    )
    for q, a in qas:
        tmp += '\n\n' + 'USER: {query} \n ASSISTANT: {response}\n'.format(query=q, response=a)
    prefix = '\n' + 'USER: {query}\n ASSISTANT: '

    return tmp, prefix


def get_Guanaco_format_prompt(qas: list):
    tmp = (
        "A chat between a curious human and an artificial intelligence assistant. "
        "The assistant gives helpful, detailed, and polite answers to the user's questions. "
    )
    for q, a in qas:
        tmp += '\n\n' + '### Human: {query}\n### Assistant: {response}\n'.format(query=q, response=a)
    prefix = '\n' + '### Human: {query}\n### Assistant:'

    return tmp, prefix


def get_llama2_chat_format_prompt(qas: list):
    tmp = (
        "A chat between a curious human and an artificial intelligence assistant. "
        "The assistant gives helpful, detailed, and polite answers to the user's questions. "
    )
    for q, a in qas:
        tmp += '\n\n' + '### Human: {query}\n### Assistant: {response}\n'.format(query=q, response=a)
    prefix = '\n' + '### Human: {query}\n### Assistant:'

    return tmp, prefix


def get_alpaca_format_prompt_wo_input(qas: list):
    tmp = (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n"
    )
    for q, a in qas:
        tmp += '\n' + '### Instruction:\n{query}\n\n### Response: {response}\n'.format(query=q, response=a)
    prefix = '\n' + '### Instruction:\n{query}\n\n### Response:'

    return tmp, prefix


def get_alpaca_format_mc_prompt_wo_input(qas: list):
    tmp = (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n"
    )
    for q, a in qas:
        tmp += '\n' + '### Instruction:\n{query}\n\n### Response: Let\'s solve the multi-choice question step by step.\n{response}\n'.format(query=q, response=a)
    prefix = '\n' + '### Instruction:\n{query}\n\n### Response: Let\'s solve the multi-choice question step by step.\n'

    return tmp, prefix


def get_gemma_wo_input(qas: list):
    tmp = ""
    for q, a in qas:
        tmp += '\n' + '<start_of_turn>user\n{query}<end_of_turn>\n<start_of_turn>model\n{response}\n'.format(query=q, response=a)
    tmp = tmp.lstrip('\n')

    prefix = '<start_of_turn>user\n{query}<end_of_turn>\n<start_of_turn>model\n'

    return tmp, prefix


def get_mistral_wo_input(qas: list):
    # tmp = "Given a question, please answer it step by step and then give your final answer at the end with 'The answer is ...'"
    tmp = ""
    for q, a in qas:
        tmp += '\n' + '[INST] {query} [/INST]{response}\n'.format(query=q, response=a)
    tmp = tmp.lstrip('\n')
    
    prefix = '[INST] {query} [/INST]'

    return tmp, prefix


def get_short_format(qas: list):
    tmp = "You are supposed to provide a solution to a given problem.\n\n"
    for q, a in qas:
        tmp += '\n' + 'Problem:\n{query}\nSolution:\n{response}\n'.format(query=q, response=a)
    prefix = '\n' + 'Problem:\n{query}\nSolution\n'

    return tmp, prefix


def get_short_formt_step_by_step(qas: list):
    tmp = "You are supposed to provide a step-by-step solution to a given problem.\n\n"
    for q, a in qas:
        tmp += '\n' + 'Problem:\n{query}\nSolution:\nLet\'s think step by step. {response}\n'.format(query=q, response=a)
    prefix = '\n' + 'Problem:\n{query}\nSolution:\nLet\'s think step by step.'

    return tmp, prefix