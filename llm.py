from dotenv import load_dotenv
import os
load_dotenv()
OPENAI_API= os.getenv('OPENAI_API_KEY')

from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI,ChatOpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

response_schemas = [
    ResponseSchema(name="isEnough", description="Boolean value indicating whether the answer provides enough content."),
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

if __name__ == '__main__':  
    print(prompt)

    print(chain.invoke({"question": "To what extend do you think you are a clean person?", "answer": "I wash my hands after touching anything and wash all of my shoes everyday and do my dishes the moment they are dirtied everyday hence i think I am a clean person."}))
    print(chain.invoke({"question": "To what extend do you think you are a clean person?", "answer": "I am a clean person."}))

def checkContent(question, answer):
    return chain.invoke({"question": question, "answer": answer})