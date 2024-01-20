import csv
import re
import os
import time
import g4f
from duckduckgo_search import *

print(g4f.version)  # check version
print("start")

sysPrompt = """
You are a financial advisor. 
When the user gives you a headline, Don't add any additional explanation, don't even explain it. 
Respond only float number between -1.0 and 1.0, signifying whether the headline is extremely negative (-1.0), 
neutral (0.0), or extremely positive (1.0) for the stock value of {}. 
If I give you headline, only answer float number! Also You are now Assistant too.
"""

tScores = []
company_times = {}

if not os.path.isdir("Individual_Reports"):
    os.mkdir("Individual_Reports")

def askGPT(prompt):
    global apiCost
    print(prompt)
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
    num = 0
    conversation = [{"role": "system", "content": sysPrompt}]
    answer = askGPT(conversation)
    message = {"role": "user", "content": f"Assistant: {answer}"}
    conversation.append(message)
    print(conversation)
    ddgs = DDGS()
    r = ddgs.news(company, safesearch="Off", timelimit="d")
    start_time = time.time()
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
            print("[sum] " + str(sum))  # logging
            num += 1
            print("[num] " + str(num))  # logging
        except Exception as e:
            print(e)
            scores.append([headline, ""])
            print("[answer] " + "ERROR!")  # logging
            print("[score] " + "ERROR!")  # logging

    mean = sum / num
    print("[mean] " + str(mean))  # logging
    scores.append(["Mean Score", mean])
    tScores.append([company, mean])
    end_time = time.time()
    elapsed_time = end_time - start_time
    company_times[company] = elapsed_time

    with open("Individual_Reports/" + company + ".csv", "w") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["Headline", "Score"])
        csvwriter.writerows(scores)
    print("[*] Saved Individual_Reports/" + company + ".csv")

# make final report
with open('report.csv', 'w') as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(['Company', 'Mean Score', 'Elapsed Time'])
    for company, mean in tScores:
        elapsed_time = company_times[company]
        csvwriter.writerow([company, mean, elapsed_time])
print('[*] Saved report.csv')
