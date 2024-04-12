from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()


users=[{
        "id":"0",
        "name": "user0 name",
        "isMale":True,
        "age": 23,
        "occupation": "user0 Occupation/School",
        "location": "user0 Location",
        "budget": 1000,
        "hasRoom": True
    },
    {
        "id":"1",
        "name": "user0 name",
        "isMale": False,
        "age": 25,
        "occupation": "user0 Occupation/School",
        "location": "user0 Location",
        "budget": 2000,
        "hasRoom": False
    }
]


qnsBank=[
    {
        "id":0,
        "question":"Do you have a room?",
        "type":3
    },
    {
        "id":1,
        "question":"What is your budget?",
        "type":2
    },
    {
        "id":2,
        "question":"What is love",
        "type":1
    }
]
customQns=[
    {
        "id":"0",
        "question":"Do you have a room?",
        "questionerId":"0",
    },
    {
        "id":"1",
        "question":"Do you have a room?",
        "questionerId":"0",
    },
]
customResponses=[
    {
        "id":"0",
        "questionerId":"0",
        "userId":"0",
        "response":"Yes",
        "encoding":[]
    },
    {
        "id":"1",
        "questionerId":"0",
        "userId":"1",
        "response":"No",
        "encoding":[]
    }
]

stdResponses=[
    {
        "id":"0",
        "qnsId":"0",
        "userId":"0",
        "response":"Yes",
        "encoding":[]
    },
    {
        "id":"1",
        "qnsId":"0",
        "userId":"1",
        "response":"No",
        "encoding":[]
    }
]
#database
#qnsBank
#ProfileQns
#Profile
#Responses
# "0": {
#     "profile": {
#       "name": "user0 name",
#       "gender": "user0 gender",
#       "age": "user0 age",
#       "Occupation/School": "user0 Occupation/School",
#       "Location": "user0 Location",
#       "Budget": "user0 Budget",
#       "Do you have a room?": "user0 Do you have a room?"
#     },
#     "responses": {
#       "0": "answer",
#       "1": "answer",