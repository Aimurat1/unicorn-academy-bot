import json
# from faq import question_answers

admin_arr = ["1"]

with open("./academy/admin_id.json", "w") as file:
    json.dump(admin_arr, file)

# with open("./academy/question.json", "r") as file:
#     data = json.load(file)
    
# print(data)