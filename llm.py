import json
import os
from dotenv import load_dotenv

import faiss
import numpy as np
from fastembed import TextEmbedding as Embedding
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
from openai import Client


load_dotenv()
OPENAI_API = os.getenv('OPENAI_API_KEY')
with open('qnsBank.json', 'r') as file:
    qnsBank = json.load(file)


def checkContent(question, answer):
    response_schemas = [
        ResponseSchema(
            name="isEnough", description="Boolean value indicating whether the answer provides enough content."),
        ResponseSchema(
            name="FollowUpPrompt",
            description="a follow up prompt to ask for more information if the answer does not answer the question.",
        ),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(
        response_schemas)
    format_instructions = output_parser.get_format_instructions()
    prompt = PromptTemplate(
        template="Given a question and an answer, output whether the answer answers the question. Return Boolean whether it answers and if not, add a follow up prompt.\n \
            Heres an  example:\n \
                1. question: Are you an honest person? answer: i am an honest person // isEnough: False, FollowUpPrompt: give an example of why you think you are honest \n \
                2. question: Are you an honest person? answer: i am an honest person as I always ensure the right change is given to me // isEnough: True, FollowUpPrompt: NIL \n \
            {format_instructions}\n{question}\n{answer}",
        input_variables=["question", "answer"],
        partial_variables={"format_instructions": format_instructions},
    )
    model = ChatOpenAI(temperature=0, model="gpt-4-0613")
    chain = prompt | model | output_parser
    return chain.invoke({"question": question, "answer": answer})


def calculateEmbeddings(text):
    client = Client()
    response = client.embeddings.create(
        input=text, model="text-embedding-3-small")
    return response.data[0].embedding


def fastEmbedding(text):
    embedding_model = Embedding(
        model_name="BAAI/bge-large-en-v1.5", max_length=512)
    embedding = embedding_model.embed(text)
    return list(embedding)[0].tolist()


def compareEmbeddings(userEmbedding, embeddingList):  # TODO yet to check
    d = 1024  # dimensionality of your embedding data #1024
    k = 4  # number of nearest neighbors to return
    index = faiss.IndexFlatIP(d)
    for em in embeddingList:
        index.add(em)
    D, I = index.search(userEmbedding, k)
    print(D, I)
    return I


def getSummary(userId):
    with open('user.json', 'r') as file:
        usersStruct = json.load(file)

    userInformation = ""
    userInformation += "Name: " + \
        str(usersStruct[userId]["profile"]["name"])+"\n"
    userInformation += "Gender:" + \
        str(usersStruct[userId]["profile"]["gender"])+"\n"

    for i in range(2, 13):
        question = qnsBank[i]["qns"]
        answer = usersStruct[userId]["responses"][str(i)]["content"]
        userInformation += "\n"+question+":"+"\n"+str(answer)+"\n"
    prompt_template = """Based on the detailed profile and responses provided below, craft a concise, summary of exactly one sentence that encapsulates the individual's key characteristics and perspectives. Aim to highlight what stands out most about the person, integrating insights from their profile and their answers to questions. Limit your response to one short sentence summarising the most interesting information only.
    "Profile and Answers: {text}"
    CONCISE SUMMARY:
"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

    model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")
    chain = prompt | model
    return (chain.invoke({"text": userInformation}).content)


def getAnswerability(userId, qns):
    with open('user.json', 'r') as file:
        usersStruct = json.load(file)
    userInformation = ""
    for fields in usersStruct[userId]["profile"]:
        userInformation += fields+": " + \
            str(usersStruct[userId]["profile"][fields])+"\n"

    for i in range(2, 13):
        question = qnsBank[i]["qns"]
        # print(usersStruct[userId]["responses"][str(i)])
        answer = usersStruct[userId]["responses"][str(i)]["content"]
        userInformation += "\n"+question+":"+"\n"+str(answer)+"\n"
    response_schemas = [
        ResponseSchema(
            name="isAnswerable",
            description="Boolean value indicating if the model can use the available user information, past answers, and general knowledge to confidently infer an answer. 'Confidently' means the model has a reasonable basis to provide an answer that is likely to be accurate and relevant, even if the information is not explicitly detailed."
        ),
        ResponseSchema(
            name="inferredAnswer",
            description="The inferred answer to the question, provided when 'isAnswerable' is True. The model should use a combination of the user's provided information, past answers, and, where appropriate, general knowledge or reasonable assumptions to infer an answer. If 'isAnswerable' is False, this field should contain a placeholder or a brief explanation why an answer cannot be provided.",
            optional=True
        ),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(
        response_schemas)
    format_instructions = "Evaluate the question based on the user's provided information and general knowledge. If the answer can be reasonably inferred from what's provided or known, mark 'isAnswerable' as True and provide the 'inferredAnswer'. If the information is insufficient and no reasonable inference can be made, 'isAnswerable' should be False, and 'inferredAnswer' should explain briefly why an answer can't be provided or be a placeholder text."

    prompt = PromptTemplate(
        template="Given the question and the user's information, assess whether a confident and reasonable answer can be provided, leveraging both specific details and general knowledge where applicable.\n\nFormat Instructions:\n{format_instructions}\n\nUser Information:\n{userInformation}\n\nQuestion:\n{question}",
        input_variables=["question", "userInformation"],
        partial_variables={"format_instructions": format_instructions},
    )

    model = ChatOpenAI(temperature=0, model="gpt-4-0613")
    chain = prompt | model | output_parser
    return (chain.invoke({"question": qns, "userInformation": userInformation}))


if __name__ == '__main__':
    # with open('newUsers.json', 'r') as file:
    #     usersStruct = json.load(file)
    # currUserId = "0"
    # embeddingList = [np.array([usersStruct[user]["responses"]["3"]["embedding"]])
    #                  for user in usersStruct if user != currUserId]
    # compareEmbeddings(np.array(
    #     [usersStruct[currUserId]["responses"]["3"]["embedding"]]), embeddingList)

    # with open('users.json', 'r') as file:
    #     usersStruct = json.load(file)
    # for user in usersStruct:
    #     response= usersStruct[user]["responses"]["3"]
    #     embedding= fastEmbedding(response)
    #     usersStruct[user]["responses"]["3"]={"response": response, "embedding": embedding}
    # with open('newUsers.json', 'w') as json_file:
    #     json.dump(usersStruct, json_file, indent=4)

    # print(prompt)

    print(checkContent("To what extend do you think you are a clean person?",
          "I wash my hands after touching anything and wash all of my shoes everyday and do my dishes the moment they are dirtied everyday hence i think I am a clean person."))
    print(checkContent(
        "To what extend do you think you are a clean person?", "I am a clean person."))

    # print(getAnswerability("1", "What is your star sign and how does it influence your personality?"))
    # print(getAnswerability("1", "What is your biggest strength?"))
    # print(getAnswerability("1", "What is your favourite hobby?"))
    # print(getAnswerability("1", "What is your budget?"))
    # print(getAnswerability("1", "Are you a clean person?"))

    # print(getSummary("1"))
    # print(getSummary("2"))
    # print(getSummary("3"))
