from flask import Flask, request
import json
from llm import checkContent

app= Flask(__name__)

with open('profileQns.json', 'r') as file: #TODO yet to use
    profileQnsBank = json.load(file)

with open('qnsBank.json', 'r') as file:
    qnsBank = json.load(file)
#qnstypes: 0: binary, 1: scaled, 2: text, 3: weightage

numQns= len(qnsBank)
nonNegotiableQns=[2]
freeTextQns=[3]
cookieBank={"cookie":{"userId":"0","qnsId":"0"}}
compatibilityThreshold=10

#number is userId
with open('users.json', 'r') as file:
    usersStruct = json.load(file)

with open('compatibility.json', 'r') as file:
    compatibilitiesStruct = json.load(file)


@app.route("/", methods=["GET"])
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/getQuestion", methods=["POST"])
def getQuestion():
    data= request.get_json() #TODO change to cookies
    cookie= data["cookie"]
    qnsId=0
    if cookie in cookieBank:
        qnsId= cookieBank[cookie]["qnsId"]
        cookieBank[cookie]["qnsId"]= qnsId+1
    if qnsId>= numQns:
        return "No more questions" #TODO process for leading prompts
    return qnsBank[qnsId]["qns"], qnsBank[qnsId]["type"]


#statuscodes: 0: success, 1: failure (answer too short), 2: found a higher threshold
@app.route("/submitAnswer", methods=["POST"])
def submitAnswer():
    data= request.get_json()
    cookie= data["cookie"]
    currUserId= cookieBank[cookie]["userId"]
    answer= data["answer"]
    qnsId= data["qnsId"]
    qnsType= qnsBank[qnsId]["type"]
    maxCompatibilityScore=0
    maxCompatibilityUserId=None

    #if weightage qns
    if qnsId==0:
        usersStruct[currUserId]["HighWeightage"]=answer
        print("HighWeightage",usersStruct[currUserId]["HighWeightage"])
    elif qnsId==1:
        usersStruct["LowWeightage"]=answer
        print("LowWeightage",usersStruct[currUserId]["LowWeightage"])
    elif qnsId in nonNegotiableQns: #pop off blacklists
        for user in usersStruct:
            if user!=currUserId and  usersStruct[user]["responses"][str(qnsId)]!=answer:
                compatibilitiesStruct[str(currUserId)].pop(str(user))
                print("removed user from compatiability",user)
        print("final compatiability",compatibilitiesStruct[currUserId])
        usersStruct[currUserId]["responses"][qnsId]=answer
    elif qnsId >= numQns: #leading prompts-> TODO send one at a time or multiple?
        leadingPrompts= usersStruct[currUserId]["leadingPrompt"]
        leadingPrompts.append(answer)
        while len(leadingPrompts)>3:
            leadingPrompts.pop(0)
        usersStruct[currUserId]["leadingPrompt"]=leadingPrompts
        print(usersStruct[currUserId])
   
    else: # normal qns
        #isLong, prompt= checkLength(qnsId,answer) #TODO for particular qns types?
        if qnsType==2:
            print("free text qns",qnsBank[qnsId]["qns"],answer)
            response= checkContent(qnsBank[qnsId]["qns"],answer)
            isLong= response["isEnough"]
            prompt= response["FollowUpPrompt"]
            print(isLong, prompt)
            if not isLong:
                return ["1", prompt]
        #rank all other users ##TODO!! #yet to do- need examples
        userRankings= getRankings(qnsId, answer)
        for idx, user in enumerate(userRankings):
            rank=idx+1
            if user in compatibilitiesStruct[currUserId]:
                compatibilitiesStruct[currUserId][user]["qnsRanking"].append(rank)
                compatibilityScore= calculateScore(currUserId, compatibilitiesStruct[currUserId][user]["compatibilityScore"],qnsId,rank)
                compatibilitiesStruct[currUserId][user]["compatibilityScore"]=compatibilityScore
                if compatibilityScore>compatibilityThreshold:
                    maxCompatibilityUserId=user
                maxCompatibilityScore= max(maxCompatibilityScore,compatibilityScore)
        usersStruct[currUserId]["responses"][qnsId]=answer
    #store answer

    if maxCompatibilityScore>compatibilityThreshold:
        return 2, maxCompatibilityUserId
    return ["0","shld be ignored"]

def checkLength(qnsId, answer):
    if len(answer)<2:
        return False, "Answer too short" #TODO generated by AI
    return True, None

def getRankings(qnsId, answer):
    return [0,1,2] #TODO rankings of all users

def calculateScore(currUserId,currScore, qnsId, rank):
    priority=1
    if qnsId in usersStruct[currUserId]["HighWeightage"]:
        priority=2
    elif qnsId in usersStruct[currUserId]["LowWeightage"]:
        priority=0.5
    return currScore+ 1/(rank)*priority #TODO: adjust formula

def getRecommendations():
    return "Recommendations" #TODO

if __name__ == '__main__':  
   app.run()