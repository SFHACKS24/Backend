from flask import Flask, jsonify, request, send_file
import json
import numpy as np
from pentagonPlotting import generateRadar
from llm import checkContent, compareEmbeddings
from typing import Optional
app= Flask(__name__)

with open('profileQns.json', 'r') as file: #TODO yet to use
    profileQnsBank = json.load(file)

with open('qnsBank.json', 'r') as file:
    qnsBank = json.load(file)

numQns= len(qnsBank)
nonNegotiableQns=[2]
freeTextQns=[3]
cookieBank={"cookie":{"userId":"0","qnsId":15}}
compatibilityThreshold=10

#number is userId
with open('newUsers.json', 'r') as file:
    usersStruct = json.load(file)

with open('compatibility.json', 'r') as file:
    compatibilitiesStruct = json.load(file)

@app.route("/", methods=["GET"])
def hello_world():
    return jsonify({"message": "Hello, World!"})

#qnstypes: 0: binary, 1: scaled, 2: text, 3: weightage, 4: enter your leading prompt, 5: unanswered leading prompt, 6: recommendations 
#response: {qnsTypes: int, (optional) content: string, (optional)userId: int} TODO if 6, gdluck
#ONLY 6: [(userId,{qnsRanking: list[int], compatibilityScore: int, answerable: bool, answer: str})]
#input: cookie
@app.route("/getQuestion", methods=["POST"])
def getQuestion()-> dict[int, Optional[str]]: 
    data= request.get_json() #TODO change to cookies
    cookie= data["cookie"]
    currUserId= cookieBank[cookie]["userId"]
    qnsId="0"
    if cookie in cookieBank:
        qnsId= cookieBank[cookie]["qnsId"]
        cookieBank[cookie]["qnsId"]= (qnsId)+1
    if qnsId== numQns:
        return jsonify({"qnsType": 4})
    elif qnsId> numQns:
        recommendations= getRecommendations(currUserId)
        for user in recommendations:
            userId= user[0]
            if user[1]["answerable"]==False:
                return jsonify(({"qnsType": 5, "userId": userId,"content": user[1]["leadingPrompts"]}))
        # print(recommendations)
        return jsonify({"qnsType": 6, "content": recommendations})
    return jsonify({"qnsType": qnsBank[qnsId]["type"], "content": qnsBank[qnsId]["qns"]})

#statuscodes: 0: success, 1: failure (answer too short), 2: found a higher threshold
#response: {status: int, (optional) prompt: string, (optional) userId: int}
#input: cookie, answer: str, qnsId: int, isLeadingPromptAns: str, (optional) userId: str. isLeadingPrompt:bool
@app.route("/submitAnswer", methods=["POST"])
def submitAnswer()-> dict[int, Optional[str], Optional[int]]:
    data= request.get_json()
    cookie= data["cookie"]
    currUserId= cookieBank[cookie]["userId"]
    answer= data["answer"]
    qnsId= data["qnsId"]
    isLeadingPromptAns= data["isLeadingPromptAns"] #NEW
    isLeadingPrompt= data["isLeadingPrompt"] #NEW
    maxCompatibilityScore=0
    maxCompatibilityUserId=None
    if isLeadingPromptAns: #TODO apply AI CHECK?
        userId= data["userId"]
        compatibilitiesStruct[currUserId][userId]["answerable"]=True
        compatibilitiesStruct[currUserId][userId]["answer"]=answer
        print("leading prompt answer",compatibilitiesStruct[currUserId][userId]["answer"])
    #if weightage qns
    elif qnsId==0:
        usersStruct[currUserId]["HighWeightage"]=answer
        print("HighWeightage",usersStruct[currUserId]["HighWeightage"])
    elif qnsId==1:
        usersStruct["LowWeightage"]=answer
        print("LowWeightage",usersStruct[currUserId]["LowWeightage"])
    elif qnsId in nonNegotiableQns: #blacklisting
        for user in usersStruct:
            if user!=currUserId and  usersStruct[user]["responses"][str(qnsId)]!=answer:
                compatibilitiesStruct[currUserId][user]["isBlacklisted"]=True
                print("Blacklisted user",user)
        print("final compatiability",compatibilitiesStruct[currUserId])
        usersStruct[currUserId]["responses"][qnsId]=answer
    elif isLeadingPrompt: #leading prompts-> send one at a time or multiple? one time
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
                return jsonify({"status": 1, "prompt": prompt})
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
        return jsonify({"status": 2, "userId": maxCompatibilityUserId})
    return jsonify({"status": 0})

#refer to getQuestion for return types
#to be called when match of higher compatibility is found
@app.route("/getDirectRecommendation", methods=["POST"])
def getDirectRecommendation()-> dict[int, Optional[str]]:
    data= request.get_json()
    cookie= data["cookie"]
    currUserId= cookieBank[cookie]["userId"]
    if usersStruct[currUserId]["leadingPrompt"].length==0:
        return jsonify({"qnsType": 4})
    recommendations= getRecommendations(currUserId)
    filteredRecommendations=[]
    for user in recommendations:
        userId= user[0]
        if user[1]["answerable"]==False: #add leading prompts
            return jsonify(({"qnsType": 5, "userId": userId,"content": user[1]["leadingPrompts"]}))
        if user[1]["compatibilityScore"]>=compatibilityThreshold:
            filteredRecommendations.append(user)
    return jsonify({"qnsType": 6, "content": recommendations})

@app.route('/getPentagon', methods=['POST'])
def get_image():
    data= request.get_json()
    individualRanking= data["individualRanking"]
    traits= ["Communication","Boundaries", "Financial Responsibilities","Compromise", "Ownership", "Cleanliness", "Similar Interests", "Reliability", "Adaptability", "Pets", "Quiet Hours", "Vice Usage"]
    newTraits=traits[:len(individualRanking)]
    data= [newTraits,individualRanking]
    img_buffer = generateRadar(data)
    return send_file(img_buffer, mimetype='image/png')

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
    else: #free text answers
        embeddingList=[np.array([usersStruct[user]["responses"]["3"]["embedding"]]) for user in usersStruct if user!=currUserId]
        relativeRanking= compareEmbeddings(np.array([usersStruct[currUserId]["responses"]["3"]["embedding"]]), embeddingList)[0]
        return [[str(rank+1)] for rank in relativeRanking]

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
    whiteListedTop=[user for user in top5 if user[1]["isBlacklisted"]==False]
    return whiteListedTop #TODO

if __name__ == '__main__':  
   app.run()