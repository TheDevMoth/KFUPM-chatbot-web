import os
import json
import re
import openai
import pprint

from embed_retrieve import retrieve_context
from enums import Category, CATE_STRING
from schedule import get_schedule

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

### api functionality ###
def _get_completion_from_messages_full(messages, model="gpt-3.5-turbo", temperature=0.7):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response

def _get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0.7):
    return _get_completion_from_messages_full(messages, model=model, temperature=temperature).choices[0].message["content"]

def _get_completion_from_prompt(prompt, model="gpt-3.5-turbo", temperature=0.7):
    message = [{"role": "user", "content": prompt}]
    return _get_completion_from_messages(message, model=model, temperature=temperature)

### Chat functionality ###
def chat(history, verbose=False):
    language = _get_language(history, verbose=verbose)
    category = _categorize(history, verbose=verbose)
    response = _decide(history, category, verbose=verbose, language=language)
    return response

def _get_language(history, verbose=False):
    """Returns the language the bot should use."""
    template = "is the following question in arabic? answer \"[yes]\" or \"[no]\".\n```{question}```"
    question = history[-1]["content"]
    prompt = template.format(question=question)
    response = _get_completion_from_prompt(prompt, temperature=0)

    response = response.replace(" ", "").lower()
    answer = re.match(r"\[([^]]*)\]", response).group(1)
    
    if verbose:
        print("### Language ###")
        print("Prompt: \n", prompt)
        print("Response: \n", response)
        print("using " + "arabic" if answer == "yes" else "english")

    return "arabic" if answer == "yes" else "english"
    

def _categorize(history, verbose=False):
    template = """
you are given a question from a student and some previous context delimited by ```. your task is to assign the question to the most accurate categories.
the categories are:
{categories}

previous context: ```{context}```
the question is: ```{question}```

Format your answer as a list of numbers surrounded with brackets. Do not add any other text. 
for example, if the question is a follow up question and about university rules, then your answer should be: [1,3]
if it is unrelated to the previous context, then your answer should be: [6]
""".strip()

    question = history[-1]["content"]
    context = history[-2]["content"]
    cats = "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(list(CATE_STRING.values()))])

    prompt = template.format(categories=cats, context=context, question=question)
    response = _get_completion_from_prompt(prompt, temperature=0)

    # extract categories from response
    response = response.replace(" ", "")
    output_categories = re.match(r"\[([^]]*)\]", response).group(1)
    # output_category = int(output_category)
    output_categories = output_categories.split(",")
    output_categories = [int(i) for i in output_categories]

    if verbose:
        print("### Categorization ###")
        print("Prompt: \n", prompt)
        print("")
        print("Response: \n", response)
        print("")
        print("Output categories: ", output_categories)
        print("")
        print("Categories: ")
        print(cats)
    
    return output_categories

def _decide(history, category, language="arabic", verbose=False):
    switch = {
        Category.FOLLOWUP.value: _follow_up,
        Category.SCHEDULE.value: _schedule,
        Category.RULES.value: _retrieve,
        Category.REGISTRATION.value: _retrieve,
        Category.SMALLTALK.value: _small_talk,
        Category.UNRELATED.value: _unrelated,
        Category.OTHER.value: _retrieve
    }
    prompt = ""
    if any([i in category for i in [Category.RULES.value, Category.REGISTRATION.value, Category.SCHEDULE.value]]):
        prompt += "Write a detailed answer to the student question in the same language as the student using information provided: \n"

    func_set = set()
    for i in category:
        func_set.add(switch[i])
    for i in func_set:
        prompt += i(history, verbose=verbose, language=language)

    prompt += f"Student question: ```{history[-1]['content']}```"

    history[-1]["content"] = prompt
    response = _get_completion_from_messages(history, temperature=0.7)

    if verbose:
        print("### Decision ###")
        print("Response: \n", response)

    return response
    
def _retrieve(history, verbose=False, language="arabic"):
    question = history[-1]["content"]
    context, similarity = retrieve_context(question, k=3, language=language)
    # TODO add thresholds and decisions
    text = f"handbook context: ```{context}```"

    if verbose:
        print("### Retrieve ###")
        for i in range(len(context)):
            print(f"Context {i} with similarity {similarity[i]}: \n", context[i])
            print("")
    return text

def _follow_up(history, verbose=False, language="arabic"):
    if verbose:
        print("### Follow up ###")
    return ""

def _schedule(history, verbose=False, language="arabic"):
    schedule = get_schedule()
    text = f"schedule: ```{schedule}```"

    if verbose:
        print("### Schedule ###")
    return text

def _small_talk(history, verbose=False, language="arabic"):
    if verbose:
        print("### Small talk ###")
    return ""

def _unrelated(history, verbose=False, language="arabic"):
    text = "if the question is unrelated to kfupm, or if the student is asking for homework help them, tell the student you cannot help them, and mention why."

    if verbose:
        print("### Unrelated ###")
    return text

def _ummm(history, verbose=False, language="arabic"):
    text = "Answer the following message if you have enough information, otherwise, tell the student you are having trouble and cannot help them right now."

    if verbose:
        print("### Ummm ###")
    return text

if __name__ == "__main__":
    import pprint
    question = [{"role": "user", "content": "What sound does a fox make?"}]
    
    response = _get_completion_from_messages_full(question)
    pprint.pprint(response)