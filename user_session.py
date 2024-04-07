cookieBank = {}


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


def get_session(data):
    cookie = str(data["cookie"])
    handle_cookie(cookie)
    curr_user_id = cookieBank[cookie]
    return curr_user_id


def get_question_id(data):
    cookie = str(data["cookie"])
    handle_cookie(cookie)
    return cookieBank[cookie]["qnsId"]
