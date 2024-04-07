from langchain_openai import OpenAI, ChatOpenAI
import faiss
from fastembed import TextEmbedding as Embedding
from openai import Client
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate
import json
from dotenv import load_dotenv
import os
import numpy as np
load_dotenv()
OPENAI_API = os.getenv('OPENAI_API_KEY')


response_schemas = [
    ResponseSchema(
        name="isEnough", description="Boolean value indicating whether the answer provides enough content."),
    ResponseSchema(
        name="FollowUpPrompt",
        description="a follow up prompt to ask for more information if the answer does not answer the question.",
    ),
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
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
model = ChatOpenAI(temperature=0)
chain = prompt | model | output_parser


def checkContent(question, answer):
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


if __name__ == '__main__':
    with open('newUsers.json', 'r') as file:
        usersStruct = json.load(file)
    currUserId = "0"
    embeddingList = [np.array([usersStruct[user]["responses"]["3"]["embedding"]])
                     for user in usersStruct if user != currUserId]
    compareEmbeddings(np.array(
        [usersStruct[currUserId]["responses"]["3"]["embedding"]]), embeddingList)

    # with open('users.json', 'r') as file:
    #     usersStruct = json.load(file)
    # for user in usersStruct:
    #     response= usersStruct[user]["responses"]["3"]
    #     embedding= fastEmbedding(response)
    #     usersStruct[user]["responses"]["3"]={"response": response, "embedding": embedding}
    # with open('newUsers.json', 'w') as json_file:
    #     json.dump(usersStruct, json_file, indent=4)

    # print(prompt)

    # print(chain.invoke({"question": "To what extend do you think you are a clean person?", "answer": "I wash my hands after touching anything and wash all of my shoes everyday and do my dishes the moment they are dirtied everyday hence i think I am a clean person."}))
    # print(chain.invoke({"question": "To what extend do you think you are a clean person?", "answer": "I am a clean person."}))
