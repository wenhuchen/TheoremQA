import re
from number_utils import *
from latex2sympy2 import latex2sympy


def extract_theoremqa_answer(pred_str: str, answer_flag: bool):
    if answer_flag:
        # Extract the numbers out of the string
        if '=' in pred_str:
            pred_str = pred_str.split('=')[-1].strip()
        pred_str = clean_units(pred_str)
        if re.match(r'-?[\d\.]+\s\D+$', pred_str):
            pred_str = pred_str.split(' ')[0]
        elif re.match(r'-?[\d\.]+\s[^\s]+$', pred_str):
            pred_str = pred_str.split(' ')[0]
        pred = pred_str
    else:
        pred = pred_str

    if any([option in pred.lower() for option in ['yes', 'true']]):
        pred = 'True'
    elif any([option in pred.lower() for option in ['no', 'false']]):
        pred = 'False'
    elif any([option in pred.lower() for option in ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']]):
        pass
    else:
        try:
            pred = str(eval(pred))
            # If it's working, we are all good!
        except Exception:
            try:
                # Let's try to convert that to sympy version and then execture
                pred = str(latex2sympy(pred))
                pred = str(eval(pred))
            except Exception:
                # Still no? Then give up.
                pass

    return pred


def answer_clean(direct_answer_trigger_for_fewshot: tuple, pred: str):
    pred = pred.strip('\n')

    # Determine if this is ICL, if so, use \n\n to split the first chunk.
    ICL = False
    for trigger in direct_answer_trigger_for_fewshot:
        if pred.count(trigger) > 1:
            ICL = True
    if ICL:
        pred = pred.split('\n\n')[0]

    # Split the trigger to find the answer.
    preds = re.split('|'.join(direct_answer_trigger_for_fewshot), pred)
    if len(preds) > 1:
        answer_flag = True
        pred = preds[-1]
    else:
        answer_flag = False

    pred = pred.strip('\n').rstrip('.').rstrip('/').strip(' ')

    pred = [extract_theoremqa_answer(pred, answer_flag)]

    # If there is no candidate in list, null is set.
    if len(pred) == 0:
        pred = ""
    else:
        if answer_flag:
            # choose the first element in list ...
            pred = pred[0]
        else:
            # choose the last e
            pred = pred[-1]

    # Remove the period at the end, again!
    pred = pred.rstrip('.').rstrip('/')

    return pred



def compare_answer_with_groundtruth(answer: str, groundtruth_str: str, groundtruth_num = None):
    if groundtruth_str.lower() in ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']:
        return groundtruth_str.lower() in answer.lower()
    elif answer.lower() == groundtruth_str.lower():
        return True
    elif groundtruth_num is not None:
        if isinstance(groundtruth_num, (int, float)):
            return compare_two_numbers(number_it(answer), groundtruth_num)
        else:
            if answer.startswith('(') and answer.endswith(')'):
                try:
                    answer = list(eval(answer))
                    answer = [number_it(a) for a in answer]
                except Exception as e:
                    return False
                return compare_two_list(answer, groundtruth_num)
            else:
                return False
    else:
        return False