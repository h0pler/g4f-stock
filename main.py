import csv, re, os
import g4f
from duckduckgo_search import *
import math

print("g4f " + g4f.version.get_package_version("g4f"))  # check version
print("start")

sysPrompt = """
You are a financial advisor. 
When the user gives you a headline, Don't add any additional explanation, don't even explain it. 
Respond only float number between -1.0 and 1.0, signifying whether the headline is extremely negative (-1.0), 
neutral (0.0), or extremely positive (1.0) for the stock value of {}. 
IF I GIVE YOU HEADLINE, ONLY ANSWER FLOAT NUMBER! Also You are now Assistant too.
"""

tScores = []

if not os.path.isdir("Individual_Reports"):
    os.mkdir("Individual_Reports")

def askGPT(prompt):
    global apiCost
    # print(prompt)
    resp = g4f.ChatCompletion.create(
        model="gpt-4", provider=g4f.Provider.Bing, messages=prompt
    )
    return resp

# for every company in companies.txt
for company in open("companies.txt", "r").readlines():
    company = company.strip()
    scores = []
    sysPrompt = sysPrompt.format(company)
    sum = 0
    index = 0
    conversation = [{"role": "system", "content": sysPrompt}]
    print("[sysPrompt] " + sysPrompt)
    answer = askGPT(conversation)
    message = {"role": "user", "content": f"Assistant: {answer}"}
    conversation.append(message)
    print("[answer] " + answer)
    ddgs = DDGS()
    r = ddgs.news(company, safesearch="Off", timelimit="d")
    for i in r:
        headline = i["title"]
        print("[headline] " + headline)
        message = {"role": "user", "content": f"HEADLINE: {headline}"}
        conversation.append(message)
        try:
            answer = askGPT(conversation)
            if "Assistant" not in answer:
                message["content"] = f"Assistant: {answer}"
            else:
                message["content"] = f"{answer}"
            conversation.append(message)
            print("[answer] " + str(answer))  # logging
            score = float(re.findall(r"-?\d+\.\d+", answer)[0])
            print("[score] " + str(score))  # logging
            scores.append([headline, score])
            sum += score
            sum = round(sum, 2)
            print("[sum] " + str(sum))  # logging
            index += 1
            print("[index] " + str(index))  # logging
        except Exception as e:
            print(e)
            scores.append([headline, ""])
            print("[answer] " + "ERROR!")  # logging
            print("[score] " + "ERROR!")  # logging
        print("")

    mean = sum / index
    print("[mean] " + str(mean))  # logging
    scores.append(["Mean Score", mean])
    tScores.append([company, mean])

    with open("Individual_Reports/" + company + ".csv", "w") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["Headline", "Score"])
        csvwriter.writerows(scores)
    print("[*] Saved Individual_Reports/" + company + ".csv")

# make final report
# tScores.append(['Total Cost', apiCost])
# with open('report.csv', 'w') as f:
#     csvwriter = csv.writer(f)
#     csvwriter.writerow(['Company', 'Mean Score'])
#     csvwriter.writerows(tScores)
# print('[*] Saved report.csv')
