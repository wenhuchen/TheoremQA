import numpy as np
from inspect import isfunction

def extract_code(result: str) -> str:
    lines = []
    within_func = False
    for line in result.split('\n'):
        if line.startswith('`'):
            continue

        if line.startswith('def '):
            within_func = True

        if line.startswith('import') or line.startswith('from'):
            lines.append(line)

        if within_func:
            lines.append(line)

        if line.startswith('  return') or line.startswith('    return'):
            within_func = False

    for line_no in range(len(lines) - 1, -1, -1):
        if 'return ' not in lines[line_no]:
            del lines[line_no]
        else:
            break
    result = '\n'.join(lines)
    return result


def extract_answer(result: str) -> str:
    prediction = result.strip().strip('\n').split('\n')[-1]
    tmp = ''
    for entry in prediction.split(' ')[::-1]:
        if entry == 'is' or entry == 'be' or entry == 'are' or entry.endswith(':'):
            break
        tmp = entry + ' ' + tmp
    prediction = tmp.strip().strip('.')
    return prediction


def postprocess_number(prediction):
    if isinstance(prediction, set):
        prediction = list(prediction)
    elif isinstance(prediction, np.complex128):
        prediction = prediction.real
    elif isinstance(prediction, np.ndarray):
        prediction = prediction.tolist()
    elif isinstance(prediction, complex):
        prediction = prediction.real
    elif isinstance(prediction, list):
        prediction = [float(x) for x in prediction]
    elif 'sympy' in str(type(prediction)):
        prediction = float(prediction)
    elif isfunction(prediction):
        prediction = None
    
    return prediction


impossible_questions = ['jianyu_xu/integer_programming_1.json', 'tonyxia/totient6.json']