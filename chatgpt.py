import requests


import requests

import jsonlines
import re

def ask_question(question):
    # Set your OpenAI API key
    api_key = "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"

    # Define the API endpoint URL
    api_url = "https://api.openai.com/v1/chat/completions"

    # Define the headers with your API key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Define the data payload with the question
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": question}
        ]
    }

    # Make the API request
    response = requests.post(api_url, headers=headers, json=data)

    # Parse the response and extract the generated answer
    if response.status_code == 200:
        response_json = response.json()
        answer = response_json["choices"][0]["message"]["content"]
        return answer
    else:
        print(response.json())
        return None  # Handle API errors


def get_models():
    # Set your OpenAI API key
    api_key = "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"

    # Define the API endpoint URL
    api_url = "https://api.openai.com/v1/models"

    # Define the headers with your API key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # Make the API request
    response = requests.get(api_url, headers=headers)
    # Parse the response and extract the generated answer
    print(response.json())

train_data_path = "data/training_data/Task_1_dev.jsonl"
train_data_path2 = "data/training_data/Tasktry_dev.jsonl"

def train_iter(path):
    with open(path, mode='r', encoding='utf-8') as f:
        reader = jsonlines.Reader(f)
        for instance in reader:
            article = instance["article"]
            question = instance["question"]
            opt0, opt1, opt2, opt3, opt4 = instance["option_0"],instance["option_1"], \
                instance["option_2"],instance["option_3"],instance["option_4"]
            opts = [opt0, opt1, opt2, opt3, opt4]
            label = instance["label"]
            yield (article, question, opts, label)

def discriminative_result(train_data_path):
    unSuccess = 0
    TP =0
    FN =0 
    totalNum =0
    for instance in train_iter(train_data_path):
        article, question, opts, label = instance
        question1 = f"""
            [TASK] Read the passage and fill in the blank in the summary, using one of the options. Please only respond with the chosen option. \n
            [PASSAGE] {article} \n
            [SUMMARY] {question} \n
            [OPTIONS] {opts} \n
        """
        answer = ask_question(question1)
        try:
            answerRe =re.sub('[^a-zA-Z]+', '', answer)
            answerRe = answerRe.lower()
        except:
            unSuccess  = unSuccess + 1

        if answerRe not in opts and opts[label] not in answerRe:
            unSuccess  = unSuccess + 1
            # print(f"wrong answer:{answerRe}")
            # print(f"wrong opts:{opts[label]}\n")
        else:
            if opts[label] in answerRe:
                TP = TP+1
            else:
                FN = FN + 1
        totalNum = totalNum +1
    
    print(f"Discriminative unSuccess: {unSuccess}  ")
    print(f"Discriminative TP: {TP}  ")
    print(f"Discriminative FN: {FN}  ")
    print(f"Discriminative Total Number: {totalNum}\n")

def generative_result(train_data_path):
    TP =0
    FN =0 
    totalNum =0
    unSuccQ3 = 0
    unSuccQ2 = 0
    for instance in train_iter(train_data_path):

        article, question, opts, label = instance
        question2 = f"""
            [TASK] Read the passage and generate the @placeholder in the summary. Please generate only one word. \n
            [PASSAGE] {article} \n
            [SUMMARY] {question} \n
        
        """
        answer2 = ask_question(question2)
        
        if answer2 is not None and " " not in answer2:
            replaceAnswer2 = "**"+answer2+"**"
            replaceQuestion = question.replace("@placeholder",replaceAnswer2)
            question3 = f"""
                [TASK] Which word from the options is most similar to the word **{answer2}** in the following context? You must respond with one word from the options.
                [CONTEXT] {replaceQuestion}\n
                [OPTIONS] {opts} \n
            """
            answer3 = ask_question(question3)
            try:
                answerRe =re.sub('[^a-zA-Z]+', '', answer3)
                answerRe = answerRe.lower()
            except:
                unSuccQ3  = unSuccQ3 + 1
            if answerRe not in opts and opts[label] not in answerRe:
                unSuccQ3  = unSuccQ3 + 1
                print(f"wrong answer:{answerRe}")
                print(f"wrong opts:{opts[label]}\n")
            else:
                if opts[label] in answerRe:
                    TP = TP+1
                else:
                    FN = FN + 1
            totalNum = totalNum +1
        else:
            unSuccQ2 = unSuccQ2 + 1 # unsuccessful Q2 sum
    
    print(f"Generative unSuccess Q2: {unSuccQ2}\n")
    print(f"Generative unSuccess Q3: {unSuccQ3}  ")
    print(f"Generative TP: {TP}  ")
    print(f"Generative FN: {FN}  ")
    print(f"Generative totalNum: {totalNum}\n")



if __name__ == "__main__":
    
    discriminative_result(train_data_path)
    generative_result(train_data_path)
