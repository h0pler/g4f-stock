import csv
import re
import os
import time
import g4f
from duckduckgo_search import *
import datetime
import logmaster as lm

lm.log_start()

print("g4f " + g4f.version.get_package_version("g4f"))
lm.log_print("g4f " + g4f.version.get_package_version("g4f"))
print("start")
lm.log_print("program start")

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
    try:
        resp = g4f.ChatCompletion.create(
            model="gpt-4", provider=g4f.Provider.Bing, messages=prompt
        )
    except Exception as e:
        lm.log_print(e)
        lm.log_end()
        print(e)
        exit(-1)

    return resp


def process_headline(company, sysPrompt):
    scores = []
    sysPrompt = sysPrompt.format(company)
    sum = 0
    index = 0
    conversation = [{"role": "system", "content": sysPrompt}]
    # print("[sysPrompt] \033[92m" + sysPrompt + "\033[0m")
    # lm.log_print("[sysPrompt] " + sysPrompt)
    answer = askGPT(conversation)
    message = {"role": "user", "content": f"Assistant: {answer}"}
    conversation.append(message)
    print("[answer] \033[94m" + answer + "\033[0m")
    lm.log_print("[answer] " + answer)
    print(
        "--------------------------------------Starting Analysis--------------------------------------"
    )
    ddgs = DDGS()
    r = ddgs.news(company, safesearch="Off", timelimit="d")
    start_time = time.time()
    for i in r:
        index += 1
        print("[index] " + str(index))  # logging
        lm.log_print("[index] " + str(index))
        headline = i["title"]
        print("[headline] \033[92m" + headline + "\033[0m")
        lm.log_print("[headline] " + headline)
        message = {"role": "user", "content": f"HEADLINE: {headline}"}
        conversation.append(message)
        try:
            answer = askGPT(conversation)
            if "Assistant" not in answer:
                message["content"] = f"Assistant: {answer}"
            else:
                message["content"] = f"{answer}"
            conversation.append(message)
            answer = answer.replace("\n\n", "\n")
            print("[answer] \033[94m" + str(answer) + "\033[0m")
            lm.log_print("[answer] " + str(answer))
            score = float(re.findall(r"-?\d+\.\d+", answer)[0])
            print("[score] " + str(score))
            lm.log_print("[score] " + str(score))
            scores.append([headline, score])
            sum += score
            sum = round(sum, 2)
            print("[sum] " + str(sum))  # logging
            lm.log_print("[sum] " + str(sum))
        except Exception as e:
            print("\033[91m" + str(e) + "\033[0m")
            lm.log_print(str(e))
            scores.append([headline, ""])
            # print("[answer] " + "\033[31mERROR!\033[0m")  # logging
            # lm.log_print("[answer] " + "ERROR!")
            print("[score] " + "\033[91mERROR!\033[0m")  # logging
            lm.log_print("[score] " + "ERROR!")
        print("")
        lm.log_print("")

    mean = sum / index
    print("[mean] " + str(mean))  # logging
    lm.log_print("[mean] " + str(mean))
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
    lm.log_print("[*] Saved Individual_Reports/" + company + ".csv")


# for every company in companies.txt
for company in open("companies.txt", "r").readlines():
    company = company.strip()
    lm.log_print("[company] " + company)
    process_headline(company, sysPrompt)

# make final report
report_filename = f"report_{datetime.datetime.now().strftime("%y%m%d-%H:%M:%S")}.csv"

if not os.path.isdir("final_reports"):
    os.mkdir("final_reports")
with open("final_reports/" + report_filename, "w") as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(["Company", "Mean Score", "Elapsed Time"])
    for company, mean in tScores:
        elapsed_time = company_times[company]
        csvwriter.writerow([company, mean, elapsed_time])
print("[*] Saved final_reports/" + report_filename)
lm.log_print(
    "", "[*] Saved final_reports/" + report_filename
)

lm.log_end()
