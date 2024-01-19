import csv, re, os
import g4f
from duckduckgo_search import *
import logging
g4f.debug.logging = False # enable logging
g4f.check_version = False # Disable automatic version checking
print(g4f.version) # check version
print(g4f.Provider.Ails.params)  # supported args
# response = g4f.ChatCompletion.create(
#     model="gpt-4",
#     messages=[{"role": "user", "content": "Hello"}],
#     stream=False,
# )
# print("[Response]: "+ response)
# del response

# print("start")

sysPrompt = '''You are a financial advisor. When the user gives you a headline, Don't add any additional explanation, don't even explain it. respond only float number between -1.0 and 1.0, signifying whether the headline is extremely negative (-1.0), neutral (0.0), or extremely positive (1.0) for the stock value of {}. IF I GIVE YOU HEADLINE, ONLY ANSWER FLOAT NUMBER! Also You are now Assistant too.'''

tScores = []
# apiCost = 0



if not os.path.isdir('Individual_Reports'):
    os.mkdir('Individual_Reports')

def askGPT(prompt):
    global apiCost
    print(prompt)
    resp = g4f.ChatCompletion.create(
        model="gpt-4",
        provider=g4f.Provider.Bing, 
        messages=prompt
        )
    # print(resp)
    # costFactor = [0.03, 0.06]
    # apiCost += resp['usage']['prompt_tokens']/1000*costFactor[0]+resp['usage']['completion_tokens']/1000*costFactor[1]
    return resp

#for every company in companies.txt
for company in open('companies.txt', 'r').readlines():
    company = company.strip()
    scores = []
    sysPrompt = sysPrompt.format(company)
    # print(sysPrompt)
    sum = 0 # these two vars for calculating the mean score
    num = 0
    conversation = [{"role": "system", "content": sysPrompt}]
    answer=askGPT(conversation)
    message = {"role": "user", "content": f"Assistant: {answer}"}
    conversation.append(message)
    print(conversation)
    #DDGS 클래스 인스턴스 생성
    ddgs = DDGS()
    #collect scores for every headine from the last day one by one
    r = ddgs.news(company, safesearch='Off', timelimit='d')
    for i in r:
        headline = i['title']
        print("[headline] "+headline) #logging
        message = {"role":"user", "content": f"HEADLINE: {headline}"}
        conversation.append(message)
        try:
            answer=askGPT(conversation)
            if ("Assistant" not in answer):
                # answer = float(re.findall(r'-?\d+\.\d+', answer)[0])
                message['content'] = f"Assistant: {answer}"
            else:
                # answer = float(re.findall(r'-?\d+\.\d+', answer)[0])
                message['content'] = f"{answer}"
            conversation.append(message)
            print("[answer] "+str(answer)) #logging
            score = float(re.findall(r'-?\d+\.\d+', answer)[0])
            print("[score] "+ str(score)) #logging
            scores.append([headline, score])
            sum += score
            print("[sum] "+str(sum)) #logging
            num += 1
            print("[num] "+str(num)) #logging
        except Exception as e:
            print(e)
            scores.append([headline, ''])
            print("[answer] "+'ERROR!') #logging
            print("[score] "+'ERROR!') #logging
        


    #calculate mean score, log it
    mean = sum/num
    print("[mean] "+mean) #logging
    scores.append(['Mean Score', mean])
    tScores.append([company, mean])

    #make individual report
    with open('Individual_Reports/'+company+'.csv', 'w') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(['Headline', 'Score'])
        csvwriter.writerows(scores)
    print('[*] Saved Individual_Reports/'+company+'.csv')

#make final report
# tScores.append(['Total Cost', apiCost])
# with open('report.csv', 'w') as f:
#     csvwriter = csv.writer(f)
#     csvwriter.writerow(['Company', 'Mean Score'])
#     csvwriter.writerows(tScores)
# print('[*] Saved report.csv')
