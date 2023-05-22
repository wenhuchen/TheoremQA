# TheoremQA
The dataset and code for paper: TheoremQA: A Theorem-driven Question Answering dataset

## Introduction
We propose the first question-answering dataset driven by STEM theorems. We annotated 800 QA pairs covering 350+ theorems spanning across Math, EE&CS, Physics and Finance. The dataset is collected by human experts with very high quality. We provide the dataset as a new benchmark to test the limit of large language models to apply theorems to solve challenging university-level questions. We provide a pipeline in the following to prompt LLMs and evaluate their outputs with WolframAlpha.
<p align="center">
<img src="overview.001.jpeg" width="1000">
</p>

## Examples
<p align="center">
<img src="examples.001.jpeg" width="400">
</p>

<p align="center">
<img src="examples.002.jpeg" width="400">
</p>

## Files
- theoremqa_test.json: this file contains all the annotated question-answer pairs.
- all_theorems.json: this file contains the textual description of all the theorems being covered.

## Running Instruction

### Dependency
- openai == 0.27.6
- wolframalpha == 5.0.0
- pytorch == py3.8_cuda11.8_cudnn8.7.0_0
- sympy == 1.11.1
- transformers == 4.29.1
- accelerate == 0.19.0
- anthropic == 0.2.9


### Chain-of-Thoughts Prompting
```
python run_gpt4.py
```
This will write otuput to outputs/GPT4_s0...

### Program-of-Thoughts Prompting
```
python run_gpt4_pot.py
```
This will write otuput to outputs/GPT4_PoT_s0...


### Evaluate model output
You need to register an wolfram|alpha account to use their free API, checkout https://products.wolframalpha.com/api to register. Once you are done, you should receive an API_KEY.
```
export OPENAI_KEY=[YOUR_KEY]
export WOLFRAM_KEY=[YOUR_KEY]
python predict_accuracy.py outputs/[YOUR_FILE]
```
This will write a evaluation output as outputs/[YOUR_FILE].corrected

### Analyze the model output
```
python analyze_results.py outputs/[YOUR_FILE].corrected
```
