from flask import Flask, jsonify, request
import json
from llm import checkContent

app= Flask(__name__)

with open('profileQns.json', 'r') as file: #TODO yet to use
    profileQnsBank = json.load(file)

with open('qnsBank.json', 'r') as file:
    qnsBank = json.load(file)
#qnstypes: 0: binary, 1: scaled, 2: text, 3: weightage, 4: leading prompt, 5: recommendations

numQns= len(qnsBank)
nonNegotiableQns=[2]
freeTextQns=[3]
cookieBank={"cookie":{"userId":"0","qnsId":10}}
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
    currUserId= cookieBank[cookie]["userId"]
    qnsId="0"
    if cookie in cookieBank:
        qnsId= cookieBank[cookie]["qnsId"]
        cookieBank[cookie]["qnsId"]= (qnsId)+1
    if qnsId== numQns:
        return ["shld be ignored", 4]
    elif qnsId> numQns:
        recommendations= getRecommendations(currUserId)
        print(recommendations)
        return [recommendations, 5] #
    return qnsBank[qnsId]["qns"], qnsBank[qnsId]["type"]


#statuscodes: 0: success, 1: failure (answer too short), 2: found a higher threshold
@app.route("/submitAnswer", methods=["POST"])
def submitAnswer():
    data= request.get_json()
    cookie= data["cookie"]
    currUserId= cookieBank[cookie]["userId"]
    answer= data["answer"]
    qnsId= data["qnsId"]
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
                compatibilitiesStruct[str(currUserId)].pop(str(user)) #TODO change to VETO?
                print("removed user from compatiability",user)
        print("final compatiability",compatibilitiesStruct[currUserId])
        usersStruct[currUserId]["responses"][qnsId]=answer
    elif qnsId >= numQns-1: #leading prompts-> send one at a time or multiple? one time
        # leadingPrompts= usersStruct[currUserId]["leadingPrompt"]
        # leadingPrompts.append(answer)
        # while len(leadingPrompts)>3:
        #     leadingPrompts.pop(0)
        usersStruct[currUserId]["leadingPrompt"]=answer
        print("leading prompt", usersStruct[currUserId]["leadingPrompt"])
   
    else: # normal qns
        qnsType= qnsBank[qnsId]["type"]
        if qnsType==2: #free text qns content check
            print("free text qns",qnsBank[qnsId]["qns"],answer)
            response= checkContent(qnsBank[qnsId]["qns"],answer)
            isLong= response["isEnough"]
            prompt= response["FollowUpPrompt"]
            print(isLong, prompt)
            if not isLong:
                return ["1", prompt]
        #rank all other users ##TODO!! #yet to do- need examples
        userRankings= getRankings(qnsId, qnsType, answer, currUserId)
        print("userRankings",userRankings)
        # for idx, user in enumerate(userRankings):
        #     rank=idx+1
        #     if user in compatibilitiesStruct[currUserId]:
        #         compatibilitiesStruct[currUserId][user]["qnsRanking"].append(rank)
        #         compatibilityScore= calculateScore(currUserId, compatibilitiesStruct[currUserId][user]["compatibilityScore"],qnsId,rank)
        #         compatibilitiesStruct[currUserId][user]["compatibilityScore"]=compatibilityScore
        #         if compatibilityScore>compatibilityThreshold:
        #             maxCompatibilityUserId=user
        #         maxCompatibilityScore= max(maxCompatibilityScore,compatibilityScore)
        # usersStruct[currUserId]["responses"][qnsId]=answer
    #store answer

    if maxCompatibilityScore>compatibilityThreshold:
        return 2, maxCompatibilityUserId
    return ["0","shld be ignored"]

def getRankings(qnsId, qnsType, answer, currUserId): #structure: array of userIds, idx corresponding to rank
    #if binary
    if qnsType==0:
        return [[userId for userId in usersStruct if usersStruct[userId]["responses"][str(qnsId)]==answer],[userId for userId in usersStruct if usersStruct[userId]["responses"][str(qnsId)]!=answer]]
    #if scaled
    elif qnsType==1:
        #rank userId based on how similar their answer is to user0's answer
        rankings=[[]for _ in range(10)] #RANGE IS 0-10
        for userId in usersStruct:
            if userId != currUserId:
                rankings[abs(usersStruct[userId]["responses"][str(qnsId)]-answer)].append(userId)
        return [rank for rank in rankings if rank]
    else: #TODO free text answers
        print("work in progress")
    #if text
    return [0,1,2] #TODO rankings of all users

def calculateScore(currUserId,currScore, qnsId, rank):
    priority=1
    if qnsId in usersStruct[currUserId]["HighWeightage"]:
        priority=2
    elif qnsId in usersStruct[currUserId]["LowWeightage"]:
        priority=0.5
    return currScore+ 1/(rank)*priority #TODO: adjust formula

def getRecommendations(currUserId):
    #top 5 compatibilities struct based on compatibility score
    top5= sorted(compatibilitiesStruct[currUserId].items(), key=lambda x: x[1]["compatibilityScore"], reverse=True)[:5]
    # top5_ids = [element[0] for element in top5]
    #return top 5 users
    return top5 #TODO

if __name__ == '__main__':  
   app.run()