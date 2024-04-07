import json
from typing import Optional
import numpy as np
from dotenv import load_dotenv
import logging
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS, cross_origin

from pentagonPlotting import generateRadar
from llm import checkContent, compareEmbeddings, fastEmbedding, getAnswerability, getSummary
from db import get_user, update_user

load_dotenv()
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

with open('profileQns.json', 'r') as file:  # TODO yet to use
    profileQnsBank = json.load(file)

with open('qnsBank.json', 'r') as file:
    qnsBank = json.load(file)

numQns = len(qnsBank)
nonNegotiableQns = [13]  # vices, budget
cookieBank = {}
compatibilityThreshold = 5

# number is userId
with open('user.json', 'r') as file:
    usersStruct = json.load(file)

with open('compatibility.json', 'r') as file:
    compatibilitiesStruct = json.load(file)


@app.route("/", methods=["GET"])
@cross_origin()
def hello_world():
    return jsonify({"message": "Hello, World!"})


def handle_cookie(cookie):
    userId = "0"
    if cookie not in cookieBank:
        cookieBank[cookie] = {"userId": userId, "qnsId": 0}
        # usersStruct[len(usersStruct)] = {
        #     "profile": {}, "responses": {}, "leadingPrompt": "", "HighWeightage": [], "LowWeightage": []}
        # compatibilitiesStruct[len(usersStruct)] = {}
        # for user in usersStruct:
        #     if user != len(usersStruct):
        #         compatibilitiesStruct[len(usersStruct)][user] = {
        #             "compatibilityScore": 0, "qnsRanking": [], "answer": "", "isBlacklisted": False, "answerable": False}
        #         compatibilitiesStruct[user][len(usersStruct)] = {
        #             "compatibilityScore": 0, "qnsRanking": [], "answer": "", "isBlacklisted": False, "answerable": False}


@app.route("/user/profile", methods=["POST"])
@cross_origin()
def update_profile():
    data = request.get_json()
    cookie = str(data["cookie"])
    handle_cookie(cookie)
    currUserId = cookieBank[cookie]["userId"]
    usersStruct[currUserId]["profile"]["name"] = data["name"]
    usersStruct[currUserId]["profile"]["age"] = int(data["age"])
    usersStruct[currUserId]["profile"]["gender"] = data["gender"]
    usersStruct[currUserId]["profile"]["occupation"] = data["occupation"]
    usersStruct[currUserId]["profile"]["location"] = data["location"]
    usersStruct[currUserId]["profile"]["budget"] = int(data["budget"])
    usersStruct[currUserId]["profile"]["room"] = bool(data["room"])
    # curr_user_id = cookieBank[cookie]["userId"]
    # profile_info = {
    #     "name": data.get("name", "Unnamed"),
    #     "age": data.get("age", 0),
    #     "gender": data.get("gender", "PNTS"),
    #     "occupation": data.get("occupation", ""),
    #     "location": data.get("location", ""),
    #     "budget": data.get("budget", 0),
    #     "room": data.get("room", False)
    # }
    # update_user(curr_user_id, profile_info)
    return jsonify({"status": "ok"})

# input:list of userIds
# output: list of dict[**userprofile, compatibilityScore, qnsRanking, answer]


@app.route("/getprofile", methods=["POST"])
@cross_origin()
def get_profile():
    data = request.get_json()
    cookie = str(data["cookie"])
    handle_cookie(cookie)
    currUserId = cookieBank[cookie]["userId"]
    user_ids = data["userIds"]
    userInformation = []
    for id in user_ids:
        id = str(id)
        user = usersStruct[id]
        user["compatibilityScore"] = int(
            compatibilitiesStruct[currUserId][id]["compatibilityScore"])
        user["qnsRanking"] = compatibilitiesStruct[currUserId][id]["qnsRanking"]
        while len(user["qnsRanking"]) < numQns:
            user["qnsRanking"].append(3)
        user["answer"] = str(compatibilitiesStruct[currUserId][id]["answer"])
        userInformation.append(user)
    return jsonify(userInformation)

# qnstypes: 0: binary, 1: scaled, 2: text, 3: weightage, 4: enter your leading prompt, 5: unanswered leading prompt, 6: recommendations
# response: {qnsTypes: int, (optional) content: string, (optional)userId: int} TODO if 6, gdluck
# ONLY 6: list [userIds: int]
# input: cookie


@app.route("/getQuestion", methods=["POST"])
@cross_origin()
def getQuestion() -> dict[int, Optional[str]]:
    data = request.get_json()  # TODO change to cookies
    cookie = str(data["cookie"])
    handle_cookie(cookie)
    currUserId = cookieBank[cookie]["userId"]
    qnsId = 0
    if cookie in cookieBank:
        qnsId = int(cookieBank[cookie]["qnsId"])
    if qnsId == numQns:
        return jsonify({"qnsType": 4, "qnsId": qnsId})
    elif qnsId > numQns:
        recommendations = getRecommendations(currUserId)
        for user in recommendations:
            userId = user[0]
            if user[1]["answerable"] == False:
                return jsonify(({"qnsType": 5, "userId": userId, "content": user[1]["leadingPrompts"], "qnsId": qnsId}))
        onlyRanking = [int(user[0]) for user in recommendations]
        return jsonify({"qnsType": 6, "content": onlyRanking})
    return jsonify({"qnsType": qnsBank[qnsId]["type"], "content": qnsBank[qnsId]["qns"], "qnsId": qnsId})


@app.route("/getRanking", methods=["POST"])
@cross_origin()
def getRanking():
    data = request.get_json()
    cookie = data["cookie"]
    handle_cookie(cookie)
    currUserId = cookieBank[cookie]["userId"]
    recommendations = getRecommendations(currUserId)
    onlyRanking = [int(user[0]) for user in recommendations]
    return jsonify({"content": onlyRanking})

# statuscodes: 0: success, 1: failure (answer too short), 2: found a higher threshold
# response: {status: int, (optional) prompt: string, (optional) userId: int}
# input: cookie, answer: str, qnsId: int, isLeadingPromptAns: str, (optional) userId: str. isLeadingPrompt:bool


@app.route("/submitAnswer", methods=["POST"])
@cross_origin()
def submitAnswer() -> dict[int, Optional[str], Optional[int]]:
    data = request.get_json()
    cookie = data["cookie"]
    handle_cookie(cookie)
    currUserId = str(cookieBank[cookie]["userId"])
    answer = data["answer"]
    qnsId = int(data["qnsId"])
    isLeadingPromptAns = bool(data["isLeadingPromptAns"])  # NEW
    isLeadingPrompt = bool(data["isLeadingPrompt"])  # NEW
    maxCompatibilityScore = 0
    maxCompatibilityUserId = None
    if isLeadingPromptAns:
        userId = str(data["userId"])
        compatibilitiesStruct[currUserId][userId]["answerable"] = True
        compatibilitiesStruct[currUserId][userId]["answer"] = answer
        print("leading prompt answer",
              compatibilitiesStruct[currUserId][userId]["answer"])
    # if weightage qns
    elif qnsId == 0:
        usersStruct[currUserId]["responses"][str(qnsId)]["content"] = answer
        print("HighWeightage", usersStruct[currUserId]
              ["responses"][str(qnsId)]["content"])
    elif qnsId == 1:
        print(usersStruct[currUserId]["responses"])
        usersStruct[currUserId]["responses"][str(qnsId)]["content"] = answer
        print("LowWeightage", usersStruct[currUserId]["responses"][str(qnsId)])
    elif qnsId in nonNegotiableQns:  # blacklisting
        for user in usersStruct:
            if user != currUserId and usersStruct[user]["responses"][str(qnsId)]["content"] != answer or usersStruct[user]["profile"]["budget"] > 3 * usersStruct[currUserId]["profile"]["budget"]:
                compatibilitiesStruct[currUserId][user]["isBlacklisted"] = True
                print("Blacklisted user", user)
        # print("final compatiability", compatibilitiesStruct[currUserId])
        usersStruct[currUserId]["responses"][str(qnsId)]["content"] = answer
    elif isLeadingPrompt:  # leading prompts-> send one at a time or multiple? one time
        # leadingPrompts= usersStruct[currUserId]["leadingPrompt"]
        # leadingPrompts.append(answer)
        # while len(leadingPrompts)>3:
        #     leadingPrompts.pop(0)
        usersStruct[currUserId]["leadingPrompt"] = answer
        print("leading prompt", usersStruct[currUserId]["leadingPrompt"])

    else:  # normal qns
        qnsType = int(qnsBank[qnsId]["type"])
        print("current qns type is", qnsType)
        if qnsType == 2:  # free text qns content check
            print("free text qns", qnsBank[qnsId]["qns"], answer)
            chat = checkContent(qnsBank[qnsId]["qns"], answer)
            # isLong = chat["isEnough"]
            # prompt = chat["FollowUpPrompt"]
            # print(isLong, prompt)
            # if not isLong:
            #     return jsonify({"status": 1, "prompt": prompt})
            # generate embedding
            embedding = fastEmbedding(answer)
            usersStruct[currUserId]["responses"][str(qnsId)] = {
                "content": answer, "embedding": embedding}
            # print(embedding)
        else:
            usersStruct[currUserId]["responses"][str(
                qnsId)]["content"] = answer
        print("Stored Anser", usersStruct[currUserId]["responses"][str(qnsId)])
        # print('question type', qnsType, qnsId)
        userRankings = getRankings(qnsId, int(qnsType), answer, currUserId)
        print("userRankings", userRankings)
        for idx, userList in enumerate(userRankings):
            rank = idx+1
            for user in userList:
                if compatibilitiesStruct[currUserId][user]["isBlacklisted"] == False:
                    compatibilitiesStruct[currUserId][user]["qnsRanking"].append(
                        rank)
                    compatibilityScore = calculateScore(
                        currUserId, compatibilitiesStruct[currUserId][user]["compatibilityScore"], qnsId, rank)
                    compatibilitiesStruct[currUserId][user]["compatibilityScore"] = compatibilityScore
                    print("compatibilityScore for user",
                          user, compatibilityScore)
                    if compatibilityScore > compatibilityThreshold:
                        maxCompatibilityUserId = user
                    maxCompatibilityScore = max(
                        maxCompatibilityScore, compatibilityScore)
        usersStruct[currUserId]["responses"][qnsId] = answer
    # store answer
    cookieBank[cookie]["qnsId"] = qnsId+1
    if maxCompatibilityScore > compatibilityThreshold:
        return jsonify({"status": 2, "userId": maxCompatibilityUserId})
    return jsonify({"status": 0})

# refer to getQuestion for return types
# to be called when match of higher compatibility is found


@app.route("/getDirectRecommendation", methods=["POST"])
@cross_origin()
def getDirectRecommendation() -> dict[int, Optional[str]]:
    data = request.get_json()
    cookie = data["cookie"]
    handle_cookie(cookie)
    currUserId = str(cookieBank[cookie]["userId"])
    if len(usersStruct[currUserId]["leadingPrompt"]) == 0:
        return jsonify({"qnsType": 4, "qnsId": "999"})
    recommendations = getRecommendations(currUserId)
    filteredRecommendations = []
    for user in recommendations:
        userId = str(user[0])
        if user[1]["answerable"] == False:  # add leading prompts
            # return jsonify(({"qnsType": 5, "userId": userId, "content": user[1]["leadingPrompts"], "qnsId": userId}))
            chat = getAnswerability(
                "2", user[1]["leadingPrompts"])  # TODO change back
            print(chat)
            if chat["isAnswerable"]:
                compatibilitiesStruct[currUserId][userId]["answerable"] = True
                compatibilitiesStruct[currUserId][userId]["answer"] = chat["inferredAnswer"]
                print("Infereed answer", chat["inferredAnswer"])
            else:
                return jsonify(({"qnsType": 5, "userId": userId, "content": user[1]["leadingPrompts"], "qnsId": userId}))
        if user[1]["compatibilityScore"] >= compatibilityThreshold:
            filteredRecommendations.append(user)
    onlyRanking = [int(user[0]) for user in recommendations]
    return jsonify({"qnsType": 6, "content": onlyRanking})


@app.route('/getPentagon', methods=['POST'])
@cross_origin()
def get_image():
    data = request.get_json()
    individualRanking = data["individualRanking"]
    traits = ["Communication", "Boundaries", "Financial Responsibilities", "Compromise", "Ownership",
              "Cleanliness", "Similar Interests", "Reliability", "Adaptability", "Pets", "Quiet Hours", "Vice Usage"]
    newTraits = traits[:len(individualRanking)]
    data = [newTraits, individualRanking]
    img_buffer = generateRadar(data)
    return send_file(img_buffer, mimetype='image/png')


# structure: array of userIds, idx corresponding to rank
def getRankings(qnsId, qnsType, answer, currUserId):
    # if binary
    if qnsType == 0:
        return [[userId for userId in usersStruct if usersStruct[userId]["responses"][str(qnsId)]["content"] == answer and userId != currUserId], [userId for userId in usersStruct if usersStruct[userId]["responses"][str(qnsId)]["content"] != answer and userId != currUserId]]
    # if scaled
    elif qnsType == 1:
        # rank userId based on how similar their answer is to user0's answer
        rankings = [[]for _ in range(11)]  # RANGE IS 0-10
        for userId in usersStruct:
            if userId != currUserId:
                rankings[abs(usersStruct[userId]["responses"]
                             [str(qnsId)]["content"]-answer)].append(userId)
        return [rank for rank in rankings if rank]
    else:  # free text answers
        embeddingList = [np.array([usersStruct[user]["responses"][str(qnsId)]["embedding"]])
                         for user in usersStruct if user != currUserId]
        relativeRanking = compareEmbeddings(np.array(
            [usersStruct[str(1)]["responses"][str(6)]["embedding"]]), embeddingList)[0]
        return [[str(rank+1)] for rank in relativeRanking]


def calculateScore(currUserId, currScore, qnsId, rank):
    priority = 1
    if qnsId in usersStruct[str(currUserId)]["responses"]["0"]["content"]:
        priority = 2
    elif qnsId in usersStruct[currUserId]["responses"]["1"]["content"]:
        priority = 0.5
    return currScore + 1/(rank)*priority  # TODO: adjust formula


def getRecommendations(currUserId):
    # top 5 compatibilities struct based on compatibility score
    top5 = sorted(compatibilitiesStruct[currUserId].items(
    ), key=lambda x: x[1]["compatibilityScore"], reverse=True)[:5]
    # top5_ids = [element[0] for element in top5]
    # return top 5 users
    whiteListedTop = [user for user in top5 if user[1]
                      ["isBlacklisted"] == False]
    return whiteListedTop  # TODO


# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers',
#                          'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods',
#                          'GET,PUT,POST,DELETE,OPTIONS')
#     return response


if __name__ == '__main__':
    app.run()
