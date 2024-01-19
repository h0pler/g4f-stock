import csv, re, os
import g4f
from duckduckgo_search import *

g4f.debug.logging = True # enable logging
g4f.check_version = False # Disable automatic version checking
print(g4f.version) # check version
print(g4f.Provider.Ails.params)  # supported args
print(g4f.Provider)
response = g4f.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    stream=False,
)

print("[Response]: "+ response)

sysPrompt = 'You are a financial advisor. When the user gives you a headline, ' \
            'respond with a number between -1.0 and 1.0, signifying whether the ' \
            'headline is extremely negative (-1.0), neutral (0.0), or extremely ' \
            'positive (1.0) for the stock value of {}.'

tScores = []
apiCost = 0

if not os.path.isdir('Individual_Reports'):
    os.mkdir('Individual_Reports')

def askGPT(prompt):
    global apiCost
    resp = g4f.ChatCompletion.create(
        model="gpt-4", 
        messages=[{'role': 'system', 'content': sysPrompt},
                  {'role': 'user', 'content': prompt}]
        )
    costFactor = [0.03, 0.06]
    apiCost += resp['usage']['prompt_tokens']/1000*costFactor[0]+resp['usage']['completion_tokens']/1000*costFactor[1]
    return resp['choices'][0]['message']['content']

#for every company in companies.txt
for company in open('companies.txt', 'r').readlines():
    company = company.strip()
    scores = []
    sysPrompt = sysPrompt.format(company)
    sum = 0 # these two vars for calculating the mean score
    num = 0
    
    
    #DDGS 클래스 인스턴스 생성
    ddgs = DDGS()
    #collect scores for every headine from the last day one by one
    r = ddgs.news(company, safesearch='Off', timelimit='d')
    for i in r:
        headline = i['title']
        try:
            score = float(re.findall(r'-?\d+\.\d+', askGPT(headline))[0])
            scores.append([headline, score])
            sum += score
            num += 1
        except:
            scores.append([headline, ''])

    #calculate mean score, log it
    mean = sum/num
    scores.append(['Mean Score', mean])
    tScores.append([company, mean])

    #make individual report
    with open('Individual_Reports/'+company+'.csv', 'w') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(['Headline', 'Score'])
        csvwriter.writerows(scores)
    print('[*] Saved Individual_Reports/'+company+'.csv')

#make final report
tScores.append(['Total Cost', apiCost])
with open('report.csv', 'w') as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(['Company', 'Mean Score'])
    csvwriter.writerows(tScores)
print('[*] Saved report.csv')