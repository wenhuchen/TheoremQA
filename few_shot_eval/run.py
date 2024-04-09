from examples import examples
from data_loader import get_prompt
from vllm import LLM, SamplingParams
import utils
import argparse
import torch
import data_loader
import json

parser = argparse.ArgumentParser()
parser.add_argument("--model", default='', type=str)
parser.add_argument("--output", default='', type=str)
parser.add_argument("--form", default='', type=str)
parser.add_argument("--shots", default=5, type=int)
args = parser.parse_args()


def run_question_answer(questions: list, groundtruths: list, form: str, shots: int):
    used_examples = examples[:shots]

    prompt_no_input, prefix = get_prompt(used_examples, form)
    input_strs = [prompt_no_input + prefix.format(query=q) for q in questions]
    outputs = llm.generate(input_strs, sampling_params)
    outputs = [output.outputs[0].text for output in outputs]

    returned_value = []
    for output, question, groundtruth in zip(outputs, questions, groundtruths):
        answer = utils.answer_clean(['The answer is:', 'The answer is', 'the answer is'], output)
        returned_value.append((question, output, answer, groundtruth))

    return returned_value


if __name__ == "__main__":
    stop_tokens = ["USER:", "ASSISTANT:",  "### Instruction:", "Response:", "<start_of_turn>", "[INST]", "Problem:"]
    sampling_params = SamplingParams(temperature=0, top_p=1, max_tokens=1024, stop=stop_tokens)
    llm = LLM(model=args.model, tensor_parallel_size=torch.cuda.device_count(), dtype='bfloat16', trust_remote_code=True)

    questions, groundtruths = data_loader.load_dataset()

    returned_values = run_question_answer(questions, groundtruths, args.form, args.shots)

    if not args.output:
        filename = args.model.strip('/').split('/')[-1].replace('-', '_')
        filename += '_' + f'{args.shots}shots' + '_' + args.form
        args.output = f'outputs/{filename}.jsonl'
        print('Writing the output to', args.output)

    file_handle = open(args.output, 'w')

    correct, wrong = 0, 0
    for question, output, answer, groundtruth in returned_values:
        if isinstance(groundtruth, str):
            groundtruth = [groundtruth]
        if utils.compare_answer_with_groundtruth(answer, *groundtruth):
            correct += 1
        else:
            wrong += 1

        # print(answer, '#', groundtruth, '#', correct / (correct + wrong))

        example = {
            'question': question,
            'correct': groundtruth,
            'solution': output,
            'pred': answer,
        }

        file_handle.write(json.dumps(example) + '\n')

    print('Final Accuracy: ', correct / (correct + wrong))
    print('finished one epoch')