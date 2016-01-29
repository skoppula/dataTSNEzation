
# coding: utf-8

# To distinguish Pam's and Skanda's save paths

# In[568]:

import getpass

if getpass.getuser() == 'skoppula':
    data_base_path = '/home/skoppula/mit/codeforgood/data/'
elif getpass.getuser() == 'pamelawang':
    data_base_path = '/Users/pamelawang/Documents/MIT/IAP/CodeForGood/data/'


# Read in data: the survey question topics/question IDs

# In[569]:

with open(data_base_path + 'survey-questions.tsv') as f:
    lines = f.readlines()

# Strip the top headers
lines = lines[5:]
question_topics = {}
def return_question_tuple(line):
    parts = line.split('\t')
    qid = int(parts[2])
    question = parts[3].strip()
    topic = parts[1]
    category = parts[0]
    if category.startswith('Scorecard I:'):
        category = 'Organization Profile'
    elif category.startswith('Scorecard II:'):
        category = 'Leadership Profile'
    elif category.startswith('Scorecard III:'):
        category = 'Managerial Transitions'
    elif category.startswith('Scorecard IV:'):
        category = 'Board-Leader Dynamic'
    elif category.startswith('Scorecard V:'):
        category = 'Miscellaneous'

    return (qid,question,topic,category)

for line in lines:
    (qid,question,topic,category) = return_question_tuple(line)
    if qid not in question_topics:
        question_topics[qid] = (topic,category)
    else:
        # print 'Collision! ' + str(qid) + ' ' + str((question,topic,category)) + ' ' + str(questions[qid])
        pass


# Read in data: the survey responses

# In[570]:

def delete_question(index, questions):
    del questions[index]
    
with open(data_base_path + 'responses.tsv') as f:
    lines = f.readlines()
    
raw = [[part.strip() for part in line.split('\t')] for line in lines]

original_questions = [(int(line[3]),line[4]) for line in raw[1:]]
questions = [(int(line[3]),line[4]) for line in raw[1:]]
    
# Convert raw cells to response dictionary
# One entry per surveyed person
responses = dict()
for i in range(5,len(raw[0])):
    responses[raw[0][i]] = []
    for line in raw[1:]:
        responses[raw[0][i]].append(line[i])
        
list_of_fields = dict()
# 'pid':[number] in final JSON file


# Helper functions

# In[571]:

def uniq_ans(question_index, responses):
    if type(responses.values()[0][question_index]) is list:
        poss_responses = set()
        for response in responses.values():
            poss_responses = poss_responses.union(set(response[question_index]))
        return True, list(poss_responses)
    else:
        return False, list(set([str(response[question_index]) for response in responses.values()]))

    
def get_qindices_exact(query, questions):
    return [(i,a) for i,a in enumerate(questions) if query == a[1]]


def get_qindices(query, questions):
    return [(i,a) for i,a in enumerate(questions) if query in a[1]]


def check_sizes():
    return len(set(list_of_fields.keys())) == len(list_of_fields.values()) and             len(questions) == len(responses[responses.keys()[0]])


# Export to JSON helper functions (for D3 visualization)

# In[572]:

import json

hardcoded_order = {
    2: ['18-24', '25-34', '35-44', '45-54', '55-64', '65 or Above', 'Prefer Not to Answer'],
    5: ['Bachelors', 'High School', "MBA/Management Master's", "Other Master's Degree", 'PhD, JD, or other advanced degree', 'None of the above'],
    6: ['Less than $50,000', '$50,000 - $99,999', '$100,000 - $149,999', '$150,000 - $199,999', '$200,000 - $249,999', '$250,000 and over','No response'],
    11: ['Less than $250,000', '$250,000 - $999,999', '$1,000,000 - $2,499,999', '$2,500,000 - $9,999,999', '$10,000,000 - $24,999,999','$25,000,000 and over'],
    12: ['0','1-5','6-10','11-15','16-20','21-25','26-30','31-35','36-40','41-45','46-50','51+','No response'],
    13: ['0','1-5','6-10','11-15','16-20','21-25','26-30','31-35','36-40','41-45','46-50','51+','No response'],
    14: ['0', '1-10','11-21','21-30','31-40','41-51','51-100','101-250','251-500','500+','No response'],
    16: ['None','One month or less','Two to three months','Four to six months','Seven to nine months','Ten months to a year','Over a year','No response'],
    17: ['Less than 1 Year', '1-2 Years','10-19 years','20+ Years','3-5 years','6-9 years'],
    18: range(1,51) + ['50+','No response'],
    24: ['0-2 hours','3-5 hours','5-8 hours','8-10 hours','10+ hours','20-30 hours','30-40 hours','40-50 hours','50-60 hours','60-70 hours','70+ hours'],
    25: ['I am very happy in my job','I have more good days than bad days','My experience is neutral/evenly mixed between bad and good','I have more bad days than good days','I  am very unhappy in my job','No response'],
    27: ['Completely', 'Mostly', 'Somewhat', 'Slightly', 'Not at all'],
    28: ['Completely', 'Mostly', 'Somewhat', 'Slightly', 'Not at all'],
    29: ['Completely', 'Mostly', 'Somewhat', 'Slightly', 'Not at all']
    
}

def create_persons_list(responses, lst_fields):
    persons = []
    for pid, response in responses.iteritems():
        person_dict = {}
        person_dict['pid'] = pid
        for i,field in lst_fields.iteritems():
            person_dict[field] = response[i]
        persons.append(person_dict)
    return persons
        
def create_questions_dict(questions, lst_fields):
    questions_dict = {}
    for i, field in lst_fields.iteritems():
        try:
            qid, question = questions[i]
        except ValueError:
            print questions[i]
            raise ValueError
        multiple, options = False, hardcoded_order[i] if i in hardcoded_order else uniq_ans(i, responses)
        if qid in question_topics:
            topic = question_topics[qid][0]
            category = question_topics[qid][1]
        else:
            topic, category = '', ''
        questions_dict[field] = [qid, question, topic, category, multiple, options]
    return questions_dict

def write_as_json(persons_list, questions_dict, persons_filepath, questions_filepath):
    persons_json = json.dumps(persons_list, sort_keys=True, indent=4, separators=(',', ': '))
    questions_json = json.dumps(questions_dict, sort_keys=True, indent=4, separators=(',', ': '))
    with open(persons_filepath, 'w') as f:
        f.write(persons_json)
    with open(questions_filepath, 'w') as f:
        f.write(questions_json)
    print 'Wrote to', persons_filepath,'!'
    print 'Wrote to', questions_filepath,'!'

def execute_json_write(questions, responses, list_of_fields):
    final_persons_list = create_persons_list(responses, list_of_fields)
    final_questions_dict = create_questions_dict(questions, list_of_fields)
    persons_filepath = data_base_path + 'persons.json'
    questions_filepath = data_base_path + 'questions.json'
    write_as_json(final_persons_list, final_questions_dict, persons_filepath, questions_filepath)


# Question 0: `job_category`
# 
# 1. Board member
# 2. Organization leader

# In[573]:

def categorize_job_category(line):
    line = line.lower()
    if 'board member' in line:
        return 'Board member'
    else:
        return 'Organization leader'


# In[574]:

for pid, response in responses.iteritems():
    response[0] = categorize_job_category(response[0])
    responses[pid] = response

list_of_fields[0] = 'job_category'


# Question 1: `job_title`
# 
# A possibly empty list with one or more of the following:
# 
# 1. Pastor
# 2. Director
# 3. Founder
# 4. CEO
# 5. CFO
# 6. Board Chairman
# 7. Chief Development Officer
# 8. President
# 9. Consultant
# 10. Manager

# In[575]:

def categorize_job_titles(line1, line2):
    line = line1 + ' ' + line2
    line = line.lower()
    out = []
    if line == '': return ['']
    if 'Member of leadership team' in line:
        return ['Part of a leadership team']

    bp = True
    if 'pastor' in line:
        out.append('Pastor')
    if 'director' in line:
        out.append('Director')
    if 'founder' in line:
        out.append('Founder')
    if 'ceo' in line or 'chief executive office' in line:
        out.append('CEO')
    if 'board president' in line or 'president of the board' in line:
        bp = False
        out.append('Board President')
    if 'cfo' in line:
        out.append('CFO')
    if 'chair' in line:
        out.append('Board Chairman')
    if 'Chief Development Officer' in line:
        out.append('Chief Development Officer')
    if 'president' in line and bp:
        out.append('President')
    if 'consultant' in line:
        out.append('Consultant')
    if 'manager' in line:
        out.append('Manager')

    return out


# In[576]:

for pid, response in responses.iteritems():
    response[1] = categorize_job_titles(response[1], response[2])
    del response[2]
    responses[pid] = response
    
del questions[2]
list_of_fields[1] = 'job_title'


# Question 2: `age`
# 
# 1. 18-24
# 2. 25-34
# 3. 35-44
# 4. 45-54
# 5. 55-64
# 6. 65 or Above
# 7. Prefer Not to Answer

# In[577]:

def get_age(line1, line2):
    assert (line1 == line2) or (line1 and not line2) or (line2 and not line1)
    if line1:
        return line1
    else:
        return line2


# In[578]:

# get_qindices("your age", questions): 2 and 378

for pid, response in responses.iteritems():
    response[2] = get_age(response[2], response[378])
    del response[378]
    responses[pid] = response
    
del questions[378]
list_of_fields[2] = 'age'


# Question 3: `race`
# 
# 1. American Indian or Alaskan Native  
# 2. Asian  
# 3. Black or African American  
# 4. Hispanic or Latino/Latina  
# 5. Native Hawaiian or other Pacific Islander  
# 6. White  
# 7. Decline to state 
# 8. Mix
# 9. Other

# In[579]:

# def interpret_typed_race(text):
#   if 'mix' in text:
#       race = 'Mix'
#   if 'asian' in text:
#       race = 'Asian'
#   elif 'jew' in text or 'white' in text or 'euro' in text or 'azorean' in text:
#       race = 'White'
#   elif 'hesitate' in text:
#       race = 'Decline to state'
#   return 'Other'

def get_race(lines1, lines2):
    conversion = {0:'American Indian or Alaskan Native', 1:'Asian', 2:'Black or African American', 
                  3:'Hispanic or Latino/Latina', 4:'Native Hawaiian or other Pacific Islander',
                  5:'White', 6:'Decline to state'} # Must be same order as in survey
    
    lines = lines1 if '1' in lines1 else lines2

    try:
        index = lines.index('1')  # Remember only works if there is no '1' in the 'Other' text field
        if index in conversion:
            race = conversion[index]
        elif index is len(conversion):
            # race = interpret_typed_race(lines[-1].lower())
            race = 'Other'
            
    except ValueError:
        return ''
    
    return race


# In[580]:

for pid, response in responses.iteritems():
    response[3] = get_race(response[3:12], response[378:387])
    del response[4:12]
    del response[370:379]
    responses[pid] = response
    
questions[3] = (3, 'What is your race/ethnicity?')
del questions[4:12]
del questions[370:379]
list_of_fields[3] = 'race'


# Question 4: `gender`
# 
# 1. Female/Woman
# 2. Male/Man
# 3. Transgender
# 4. Decline to state
# 5. Other

# In[581]:

def get_gender(lines1, lines2):
    conversion = {0:'Female/Woman', 1:'Male/Man', 2:'Transgender', 3:'Decline to state'} # Must be same order as in survey
    
    lines = lines1 if '1' in lines1 else lines2

    try:
        index = lines.index('1') # Remember only works if there is no '1' in the 'Other' text field
        if index in conversion:
            race = conversion[index]
        elif index is len(conversion):
            race = 'Other'
            
    except ValueError:
        return ''
    
    return race


# In[582]:

for pid, response in responses.iteritems():
    response[4] = get_gender(response[4:10], response[370:376])
    del response[5:10]
    del response[365:371]
    responses[pid] = response
    
questions[4] = (4, 'What is your gender?')
del questions[5:10]
del questions[365:371]
list_of_fields[4] = 'gender'


# Question 5: `highest_education`
# 
# 1. High School
# 2. Bachelors
# 3. Masters
# 4. MBA/Nonprofit Management Masters
# 5. PhD, JD, or other advanced degree
# 6. No response

# In[583]:

def get_education(text1, text2):
    assert text1 == '' or text2 == '' or text1 == text2
    text = text1 if len(text1) > len(text2) else text2
    
    if not text: return 'No response'
    if 'MBA' in text: return "MBA/Management Master's"
    elif 'Master' in text: return "Other Master's Degree"
    elif 'PhD' in text: return "PhD, JD, or other advanced degree"
    else: return text


# In[584]:

for pid, response in responses.iteritems():
    response[5] = get_education(response[5], response[365])
    del response[365]
    responses[pid] = response
    
del questions[365]
list_of_fields[5] = 'highest_education'


# Question 6: `income`
# 
# 1. Less than \$50,000  
# 2. \$50,000 - \$99,999  
# 3. \$100,000 - \$149,999  
# 4. \$150,000 - \$199,999  
# 5. \$200,000 - \$249,999  
# 6. $250,000 and over
# 7. No response
# 

# In[585]:

def get_income(text1, text2): 
    text = text1 if len(text1) > len(text2) else text2
    if text == '':
        return 'No response'
    elif 'Up to $49,999' in text:
        return 'Less than $50,000'
    else:
        return text


# In[586]:

for pid, response in responses.iteritems():
    response[6] = get_income(response[6], response[365])
    del response[365]
    responses[pid] = response

questions[6] = (7, 'What is your annual income?')
del questions[365]
list_of_fields[6] = 'income'


# Question 7: `zip_code`  
# Question 8: `city`  
# Question 9: `state`  

# In[587]:

import BeautifulSoup
import requests
import os
import warnings

warnings.filterwarnings("ignore")

def u2a(ustr):
    return ustr.encode('ascii', 'ignore')

def filter_texts(text1, text2):
    text = text1 if len(text1) > len(text2) else text2
    text = text.strip()
    if len(text) < 4 or len(text) > 5:
        print text
        return ('','','')
    elif len(text) == 4: 
        text = '0' + text
    return text

def get_location(zip_text):
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    url = "http://www.getzips.com/cgi-bin/ziplook.exe?What=1&Zip=%s&Submit=Look+It+Up" % zip_text
    r = s.get(url)
    soup = BeautifulSoup.BeautifulSoup(r.text)
    # print soup
    try:
        city_state = soup.findAll('table')[-1].findAll('td')[-3].findAll('p')[0].text
        state = city_state.split(', ')[1]
        city = city_state.split(', ')[0]
    except IndexError:
        print 'Problem:', zip_text
        return (zip_text, 'BAD ZIPCODE', 'BAD ZIPCODE')
        
    return (u2a(zip_text), u2a(city), u2a(state))

def create_or_populate_memo(memo_file_path, delete=False):
    if not os.path.isfile(memo_file_path) or delete:
        print 'Querying internet source!'
        memo = {}
        for pid, response in responses.iteritems():
            zip_text = filter_texts(response[7], response[191])
            if zip_text in memo:
                city, state = memo[zip_text]
            else:
                zipcode, city, state = get_location(zip_text)
                memo[zipcode] = (city, state)
            print zipcode, city, state
        with open(memo_file_path, 'w') as f:
            f.write(json.dumps(memo, sort_keys=True, indent=4, separators=(',', ': ')))
        return memo
    else:
        with open(memo_file_path, 'r') as f:
            memo = json.loads(f.read())
        return memo


# In[588]:

memo_file_path = data_base_path + 'zipcode_lookup.json'
memo = create_or_populate_memo(memo_file_path)

for pid, response in responses.iteritems():
    zc = filter_texts(response[7], response[191])
    if zc not in memo:
        zc, city, state = 'No response', 'No response', 'No response'
    else:
        city, state = memo[zc]
        if city == 'BAD ZIPCODE':
            zc, city, state = 'No response', 'No response', 'No response'
    response[7] = zc
    response.insert(8, city)
    response.insert(9, state)
    del response[193]
    responses[pid] = response

questions[7] = (108, "What is your organization's zip code?")
questions.insert(8, (108, "What is your organization's city?"))
questions.insert(9, (108, "What is your organization's state?"))
del questions[193]

list_of_fields[7] = 'zip_code'
list_of_fields[8] = 'city'
list_of_fields[9] = 'state'


# Question 10: `organization_area`
# 
# A list with one or more of the following as strings:
# 
# 1. Animal-related"
# 2. Arts, Culture & Humanities
# 3. Civil Rights, Social Action & Advocacy
# 4. Community Improvement & Capacity Building
# 5. Community Neighborhood Development
# 6. Crime & Legal
# 7. Disorders, Diseases & Medical Disciplines
# 8. Education
# 9. Employment
# 10. Environment
# 11. Food, Agriculture & Nutrition
# 12. Government & Public
# 13. Health Care
# 14. Housing & Shelter
# 15. Human Services
# 16. International Affairs, Development & Policy
# 17. LGBTQIA
# 18. Medical Research
# 19. Mental Health & Crisis Intervention
# 20. Philanthropy, Foundations & Grantmaking
# 21. Public Safety, Disaster & Relief
# 22. Recreation & Sports
# 23. Science & Technology
# 24. Social Science & Research
# 25. Spiritual & Religious
# 26. Youth Development
# 

# In[589]:

def get_area(lines1, lines2):
    conversion = {0: "Animal-related", 1: "Arts, Culture & Humanities", 2: "Civil Rights, Social Action & Advocacy", 
                  3: "Community Improvement & Capacity Building", 4: "Community Neighborhood Development", 
                  5: "Crime & Legal", 6: "Disorders, Diseases & Medical Disciplines", 7: "Education", 
                  8: "Employment", 9: "Environment", 10: "Food, Agriculture & Nutrition", 11: "Government & Public", 
                  12: "Health Care", 13: "Housing & Shelter", 14: "Human Services", 
                  15: "International Affairs, Development & Policy", 16: "LGBTQIA", 17: "Medical Research", 
                  18: "Mental Health & Crisis Intervention", 19: "Philanthropy, Foundations & Grantmaking", 
                  20: "Public Safety, Disaster & Relief", 21: "Recreation & Sports", 22: "Science & Technology", 
                  23: "Social Science & Research", 24: "Spiritual & Religious", 25: "Youth Development"} 
                  # Must be same order as in survey
    
    indices1 = [i for i,line in enumerate(lines1) if line == '1']
    indices2 = [i for i,line in enumerate(lines2) if line == '1']
    
    areas = []
    
    indices = indices1 if len(indices1) > len(indices2) else indices2
    if indices == 0: return []
    for i in indices:
        if i in conversion: areas.append(conversion[i])
    
    return areas


# In[590]:

for pid, response in responses.iteritems():
    response[10] = get_area(response[10:36], response[193:219])
    del response[11:36]
    del response[(193-25):(219-25)]
    responses[pid] = response
    
questions[10] = (8, 'What area(s) would you describe your organization as focusing on?')
del questions[11:36]
del questions[(193-25):(219-25)]

list_of_fields[10] = 'organization_area'


# Question 11: `annual_op_budget`
# 
# 1. Less than \$250,000
# 2. \$250,000 - \$999,999
# 3. \$1,000,000 - \$2,499,999
# 4. \$2,500,000 - \$9,999,999
# 5. \$10,000,000 - \$24,999,999
# 6. \$25,000,000 and over
# 7. No response

# In[591]:

def get_budget(text1, text2):
    text = text1 if text1 else text2
    if not text:
        return 'No response'
    elif 'Up to $249,999' in text:
        return 'Less than $250,000'
    else:
        return text


# In[592]:

for pid, response in responses.iteritems():
    response[11] = get_budget(response[11], response[168])
    del response[168]
    responses[pid] = response
    
del questions[168]
list_of_fields[11] = 'annual_op_budget'


# Question 12: `fulltime_staff_count`  
# Question 13: `parttime_staff_count`  
#  
# 
# 1. No response
# 2. 0
# 3. 1-5
# 4. 6-10
# 5. 11-15
# 6. 16-20
# 7. 21-25
# 8. 26-30
# 9. 31-35
# 10. 36-40
# 11. 41-45
# 12. 46-50
# 13. 51+
# 
# 
# 

# In[593]:

def get_staff_count(text):
    if not text: return 'No response'
    if text == '10-Jun': return '6-10'
    if text == '15-Nov': return '11-15'
    if text == '5-Jan': return '1-5'
    else: return text


# In[594]:

for pid, response in responses.iteritems():
    response[12] = get_staff_count(response[12])
    response[13] = get_staff_count(response[13])
    responses[pid] = response
    
questions[12] = (10, 'How many full-time paid staff does your organization have?')
questions[13] = (10, 'How many part-time paid staff does your organization have?')

list_of_fields[12] = 'fulltime_staff_count'
list_of_fields[13] = 'parttime_staff_count'


# Question 14: `volunteer_count` 
# 
# 1. No response
# 2. 0
# 3. 1-10
# 4. 11-20
# 5. 21-30
# 6. 31-40
# 7. 41-50
# 8. 51-100
# 9. 101-250
# 10. 251-500
# 11. 501+

# In[595]:

def get_volunteer_count(text):
    if not text: return 'No response'
    if text == '10-Jan': return '1-10'
    if text == '100-250': return '101-250'
    if text == '20-30': return '21-30'
    if text == '20-Oct': return '11-21'
    if text == '250-500': return '251-500'
    if text == '30-40': return '31-40'
    if text == '40-50': return '41-51'
    if text == '50-100': return '51-100'
    else: return text


# In[596]:

for pid, response in responses.iteritems():
    response[14] = get_volunteer_count(response[14])
    responses[pid] = response
    
list_of_fields[14] = 'volunteer_count'


# Question 15: `year_founded`
# 
# or 'No response'

# In[597]:

def get_year(text1, text2):
    text = text1 if len(text1) > len(text2) else text2
    if not text or text == '0': return "No response"
    if text == '1074': return '1974'
    if text == '994': return '1994'
    else: return text


# In[598]:

for pid, response in responses.iteritems():
    response[15] = get_year(response[15], response[168])
    del response[168]
    responses[pid] = response
    
del questions[168]

list_of_fields[15] = 'year_founded'


# Question 16: `cash_reserves`  
# 
# 1. No response
# 2. None
# 3. One month or less
# 4. Two to three months
# 5. Four to six months
# 6. Seven to nine months
# 7. Ten months to a year
# 8. Over a year

# In[599]:

def get_cash_reserves(text):
    if not text: return "No response"
    else: return text


# In[600]:

for pid, response in responses.iteritems():
    response[16] = get_cash_reserves(response[16])
    responses[pid] = response
    
list_of_fields[16] = 'cash_reserves'


# Question 17: `num_years_in_curr_pos`  
# (with board or in current management position)
# 
# 1. Less than 1 Year
# 2. 1-2 Years
# 3. 3-5 Years
# 4. 6-9 Years
# 5. 10-19 Years
# 6. 20+ Years

# In[601]:

def get_num_years(text1, text2):
    text = text1 if len(text1) > len(text2) else text2
    if not text: return "No response"
    if text.startswith('1 '): return '1-2 Years'
    if text.startswith('10'): return '10-19 years'
    if text.startswith('3'): return '3-5 years'
    if text.startswith('6 '): return '6-9 years'
    else: return text


# In[602]:

for pid, response in responses.iteritems():
    response[17] = get_num_years(response[17], response[269])
    responses[pid] = response
    del response[269]

questions[17] = (14, 'How many years have you been in your current position (in board or management)?')
del questions[269]

list_of_fields[17] = 'num_years_in_curr_pos'


# Question 18: `years_in_nonprofit`  
# 
# 1. No response
# 2. [Number between 1 and 50]
# 3. '50+'

# In[603]:

def get_num_years(text):
    if not text: return "No response"
    elif text != '50+' and text != 'No response': return int(text)
    return text


# In[604]:

for pid, response in responses.iteritems():
    response[18] = get_num_years(response[18])
    responses[pid] = response
    
list_of_fields[18] = 'years_in_nonprofit'


# Question 19: `past_sectors_worked`  
# 
# 1. Public
# 2. Private
# 3. Non-profit
# 4. Other
# 5. No response

# In[605]:

def get_past_sectors(lines):
    sectors = []
    if lines[0] == '-': return ["No response"]
    if lines[0] == '1': sectors.append("Public")
    if lines[1] == '1': sectors.append("Private")
    if lines[2] == '1':
        text = lines[3].lower()
        if '501' in text or 'nonprofit' in text or 'non profit' in text or 'non-profit' in text             or 'not for profit' in text or 'not-for-profit' in text or 'ymca' in text or 'volunteer' in text:
            sectors.append("Non-profit")
        elif 'consultant' in text:
            sectors.append("Private")
        elif 'public' in text or 'cdc' in text:
            sectors.append("Public")
        else:
            sectors.append("Other")
        
    return list(set(sectors))


# In[606]:

for pid, response in responses.iteritems():
    response[19] = get_past_sectors(response[19:23])
    del response[20:23]
    responses[pid] = response
    
questions[19] = (16, 'What sectors have you held a management position in the last 10 years?')
del questions[20:23]
list_of_fields[19] = 'past_sectors_worked'


# Question 20: `previous_positions`
# 
# 1. No response
# 2. Board member
# 3. Paid staff member
# 4. Volunteer

# In[607]:

def get_prev_positions(lines):
    positions = []
    if lines[0] == '-': return ["No response"]
    if lines[0] == '1': positions.append("Board member")
    if lines[1] == '1': positions.append("Paid staff member")
    if lines[2] == '1': positions.append("Volunteer")
        
    return positions


# In[608]:

for pid, response in responses.iteritems():
    response[20] = get_prev_positions(response[20:23])
    del response[21:23]
    responses[pid] = response
    
questions[20] = (17, 'What positions have you held previous to becoming a leader in the organization?')
del questions[21:23]
list_of_fields[20] = 'previous_positions'


# Question 21: `predecessor`
# 
# 1. No response
# 2. Do not know
# 3. Forced resignation / discharged
# 4. I have no predecessor
# 5. Personal reasons (illness, death, family, etc.)
# 6. Voluntarily (dissatisfied with the organization)
# 7. Voluntarily (not due to dissatisfaction)

# In[609]:

def get_predecessor(text):
    if not text: return 'No response'
    else: return text


# In[610]:

for pid, response in responses.iteritems():
    response[21] = get_predecessor(response[21])
    responses[pid] = response
    
questions[21] = (18, 'What best describes how your predecessor left the position?')
list_of_fields[21] = 'predecessor'


# Question 22: `situation_inherited`
# 
# 1. No response
# 2. [string freeform]

# In[611]:

def get_inherited(text):
    if not text: return 'No response'
    else: return text


# In[612]:

for pid, response in responses.iteritems():
    response[22] = get_inherited(response[22])
    responses[pid] = response
    
questions[22] = (19, 'Please describe the situation you inherited when you assumed your leadership. (Optional)')
list_of_fields[22] = 'situation_inherited'


# Question 23: `highest_priority`
# 
# 1. No response
# 2. [string freeform]

# In[613]:

def get_priority(text):
    if not text: return 'No response'
    else: return text


# In[614]:

for pid, response in responses.iteritems():
    response[23] = get_priority(response[23])
    responses[pid] = response
    
questions[23] = (20, 'What was your highest priority when you assumed leadership? (Optional)')
list_of_fields[23] = 'highest_priority'


# Question 24: `time_spent_on_job`
# 
# 1. 0-20 hours
# 2. 20-30 hours
# 3. 30-40 hours
# 4. 40-50 hours
# 5. 50-60 hours
# 6. 60-70 hours
# 7. 70+ hours
# 8. 0-2 hours
# 9. 3-5 hours
# 10. 5-8 hours
# 11. 8-10 hours
# 12. 10+ hours

# In[615]:

def get_time_spent(text1, text2):
    text = text1 if len(text1) > len(text2) else text2
    if not text: return 'No response'
    elif text.startswith('10+'): return '10+ hours'
    elif '10-Aug' in text: return '8-10 hours'
    elif '8-May' in text: return '5-8 hours'
    elif '5-Mar' in text: return '3-5 hours'
    elif 'Under 2' in text: return '0-2 hours'
    elif 'Under 20' in text: return '0-20 hours'
    elif text.startswith('20'): return '20-30 hours'
    elif text.startswith('30'): return '30-40 hours'
    elif text.startswith('40'): return '40-50 hours'
    elif text.startswith('50'): return '50-60 hours'
    elif text.startswith('60'): return '60-70 hours'
    elif text.startswith('70'): return '70+ hours'
    else: return 'No response'


# In[616]:

for pid, response in responses.iteritems():
    response[24] = get_time_spent(response[24],response[275])
    del response[275]
    responses[pid] = response

del questions[275]
questions[24] = (21, 'On average, how many hours per week do you work?')
list_of_fields[24] = 'time_spent_on_job'


# Question 25: `feel_about_job`
# 
# 1. I  am very unhappy in my job
# 2. I am very happy in my job
# 3. I have more bad days than good days',
# 4. I have more good days than bad days',
# 5. My experience is neutral/evenly mixed between bad and good

# In[617]:

def get_feels(text):
    if not text: return 'No response'
    else: return text


# In[618]:

for pid, response in responses.iteritems():
    response[25] = get_feels(response[25])
    responses[pid] = response
    
list_of_fields[25] = 'feel_about_job'


# Question 26: `feel_about_job_freeform`
# 
# 1. No response
# 2. [string text]

# In[619]:

def get_feels_freeform(text):
    if not text: return 'No response'
    else: return text


# In[620]:

for pid, response in responses.iteritems():
    response[26] = get_feels_freeform(response[26])
    responses[pid] = response
    
questions[26] = (22, 'Describe more about how you feel about your job. (Optional)')
list_of_fields[26] = 'feel_about_job_freeform'


# Question 27: `feel_about_hours`
# 
# 1. No response
# 2. Completely
# 3. Mostly
# 4. Somewhat
# 5. Slightly
# 6. Not at all

# In[621]:

def get_feel_hours(text1, text2):
    text = text1 if len(text1) > len(text2) else text2
    if not text: return "No Response"
    else: return text


# In[622]:

for pid, response in responses.iteritems():
    response[27] = get_feel_hours(response[27], response[275])
    del response[275]
    responses[pid] = response

del questions[275]
questions[27] = (23, 'To what extent do you feel you are putting in the right amount of hours?')
list_of_fields[27] = 'feel_about_hours'


# Question 28: `feel_about_work_life`
# 
# 1. No response
# 2. Completely
# 3. Mostly
# 4. Somewhat
# 5. Slightly
# 6. Not at all

# In[623]:

def get_feel_work_life(text):
    if not text: return "No Response"
    else: return text


# In[624]:

for pid, response in responses.iteritems():
    response[28] = get_feel_work_life(response[28])
    responses[pid] = response

questions[28] = (23, 'To what extent do you feel you have a work-life balance?')
list_of_fields[28] = 'feel_about_work_life'


# Question 29: `feel_burned_out`
# 
# 1. No response
# 2. Completely
# 3. Mostly
# 4. Somewhat
# 5. Slightly
# 6. Not at all

# In[625]:

def get_feel_burnout(text1, text2):
    text = text1 if len(text1) > text2 else text2
    if not text: return "No Response"
    else: return text


# In[626]:

for pid, response in responses.iteritems():
    response[29] = get_feel_burnout(response[29], response[277])
    del response[277]
    responses[pid] = response

questions[29] = (23, 'To what extent do you feel you are burned-out?')
del questions[277]
list_of_fields[29] = 'feel_burned_out'


# Question 30: `effective_lead_self`  
# Question 31: `effective_lead_others`  
# Question 32: `effective_lead_mission`  
# Question 33: `effective_lead_change`  
# Question 34: `effective_lead_external`  
# 
# 1. Very effective
# 2. Effective
# 3. Neutral
# 5. Ineffective
# 4. Very ineffective
# 5. Do not know
# 6. No Response

# In[627]:

def get_effective(text1, text2):
    text = text1 if len(text1) > text2 else text2
    if not text: return "No Response"
    elif text == 'Do not know/ Not sure': return 'Do not know'
    else: return text


# In[628]:

for pid, response in responses.iteritems():
    for i in xrange(5):
        response.insert(30+i, get_effective(response[42+i], response[164]))
        del response[43+i]
        del response[164]
    
    responses[pid] = response

new_q = ['How effective do you think you are in leading your own personal well-being, motivation, and understanding of leadership?',
        'How effective do you think you are in leading other people in your organization?',
        'How effective do you think you are in leading and promoting the mission/objectives in your organization?',
        'How effective do you think you are in leading change within your organization?',
        'How effective do you think you are in leading and working with people external to your organization?']
    
lof = ['effective_lead_self', 'effective_lead_others', 'effective_lead_mission', 'effective_lead_change', 'effective_lead_external']
for i in xrange(5):
    questions.insert(30+i, (26, new_q[i]))
    del questions[43+i]
    del questions[164]
    list_of_fields[30+i] = lof[i]
    hardcoded_order[30+i] = ['Very effective', 'Effective', 'Neutral', 'Ineffective', 'Very ineffective', 'Do not know', 'No Response']


# Question 35: `how_long_leaders`  
# Question 36: `make_stay_longer`  
# Question 37: `make_stay_longer_freeform`  
# 
# For Question 35:  
# ['Less than 1 year', '1-2 years', '3-5 years', '6-10 years', '11 years or more', 'Leader/I am probably not thinking about leaving the organization', 'No response']
# 
# For Question 36, a selection from:  
# ['Feeling less burned out', 
#          'Fundraising supports in place', 
#          'Stronger financial position', 
#          'A higher-performing board of directors',
#          'A clear succession plan',
#          'Less turnover of staff',
#          'Fewer personnel issues',
#          'Higher pay/better benefits for self',
#          'Higher pay/better benefits for employees',
#          'Higher contribution to retirement fund',
#          'A new organizational, field, or community challenge that could recapture your focus',
#          'Other']
# 
# For Question 37:  
# [freeform string]

# In[629]:

def get_hlong(text1, text2):
    text = text1 if len(text1) > text2 else text2
    if not text: return "No Response"
    elif text.startswith('I do not think'): return 'Leader/I am probably not thinking about leaving the organization'
    else: return text
    
def get_reasons(lines):
    r = ['Feeling less burned out', 
         'Fundraising supports in place', 
         'Stronger financial position', 
         'A higher-performing board of directors',
         'A clear succession plan',
         'Less turnover of staff',
         'Fewer personnel issues',
         'Higher pay/better benefits for self',
         'Higher pay/better benefits for employees',
         'Higher contribution to retirement fund',
         'A new organizational, field, or community challenge that could recapture your focus',
         'Other']
    
    if lines[0] == '-': return ['No response']
    else:
        reasons = []
        for i, line in enumerate(lines):
            if line == '1':
                reasons.append(r[i])
        return reasons
    
def get_reason_freeform(text):
    if not text: return "No Response"
    else: return text


# In[630]:

for pid, response in responses.iteritems():
    response.insert(35, get_hlong(response[73], response[196]))
    del response[74]
    del response[196]
    
    response.insert(36, get_reasons(response[74:86]))
    del response[75:87]
    
    response.insert(37, get_reason_freeform(response[75]))
    del response[76]

questions.insert(35, (32, 'How long do you foresee the leaders (you) remaining in their (your) current position?'))
del questions[74]
del questions[196]

questions.insert(36, (33, 'If you are planning to leave within the next two years, what conditions might make you consider staying longer?'))
del questions[75:87]

questions.insert(37, (33, 'Please elaborate if you chose "Other" for your staying conditions.'))
del questions[76]
    
list_of_fields[35] = 'how_long_leaders'
list_of_fields[36] = 'make_stay_longer'
list_of_fields[37] = 'make_stay_longer_freeform'

hardcoded_order[35] = ['Less than 1 year', '1-2 years', '3-5 years', '6-10 years', '11 years or more', 'Leader/I am probably not thinking about leaving the organization', 'No response']


# Question 38: `ann_board_perf_eval`  
# Question 39: `ann_board_perf_eval_usefulness`  
# 
# Question 38:  
# ['No response', 'Yes', 'Have not in the past but plan to in the future', 'Have in the past but do not currently', 'No']
# 
# Question 39:  
# ['No response', 'Useful', 'Very useful', 'Somewhat useful', 'Slightly useful', 'Not at all useful']

# In[631]:

def get_perf(text):
    if not text: return "No Response"
    else: return text


# In[632]:

for pid, response in responses.iteritems():
    response.insert(38, get_perf(response[124]))
    del response[125]
                    
    response.insert(39, get_perf(response[125]))
    del response[126]
    
questions.insert(38, questions[124])
del questions[125]

questions.insert(39, questions[125])
del questions[126]

list_of_fields[38] = 'ann_board_perf_eval'
list_of_fields[39] = 'ann_board_perf_eval_usefulness'

hardcoded_order[39] = ['Very useful', 'Useful', 'Somewhat useful', 'Slightly useful', 'Not at all useful', 'No response']


# Question 40: `bench_strength`  
# Question 41: `bench_strength_freeform`
# 
# Question 40 responses:  
# ['Yes', 'Somewhat', 'No', 'No response']
# 
# Question 41 responses:  
# ['No response', [freeform string]]

# In[633]:

def get_bs(text1, text2):
    text = text1 if len(text1) > len(text2) else text2
    if not text: return "No Response"
    elif text.startswith('Somewhat'): return 'Somewhat'
    else: return text


# In[634]:

for pid, response in responses.iteritems():
    response.insert(40, get_bs(response[133], response[218]))
    del response[134]
    del response[218]
                    
    response.insert(41, get_bs(response[134], response[218]))
    del response[135]
    del response[218]


questions.insert(40, (53, 'Do you believe there is enough bench strength in your organization?'))
del questions[134]
del questions[218]

questions.insert(41, (53, 'If you answered "Somewhat" for bench strength, please elaborate.'))
del questions[135]
del questions[218]

list_of_fields[40] = 'bench_strength'
list_of_fields[41] = 'bench_strength_freeform'

hardcoded_order[40] = ['Yes', 'Somewhat', 'No', 'No response']


# Question 42: `staff_racial_diversity`  
# Question 43: `staff_gender_diversity`  
# Question 44: `staff_sexual_diversity`  
# Question 45: `staff_class_diversity`  
# Question 46: `staff_ability_diversity`  
# Question 47: `staff_diversity_freeform`  
# 
# Question 48: `board_racial_diversity`  
# Question 49: `board_gender_diversity`  
# Question 50: `board_sexual_diversity`  
# Question 51: `board_class_diversity`  
# Question 52: `board_ability_diversity`  
# Question 53: `board_diversity_freeform`  
# 
# Question 42-46, 48-52 responses:  
# ['Diverse', 'Somewhat diverse', 'Not at all diverse', 'Do not know/Not sure', 'No response']
# 
# Question 47, 53 responses:  
# ['No response', [freeform string]]

# In[635]:

def get_diversity(text1, text2):
    text = text1 if len(text1) > len(text2) else text2
    if not text: return "No response"
    elif text.startswith('Do not know'): return "Do not know/Not sure"
    else: return text


# In[636]:

for pid, response in responses.iteritems():
    # staff diversity
    for i in range(5):
        response.insert(42+i, get_diversity(response[135+i], response[227]))
        del response[136+i]
        del response[227]

nq = [(54, 'How racially diverse do you feel the staff is?'),
     (54, 'How gender diverse do you feel the staff is?'),
      (54, 'How sexual-orientation diverse do you feel the staff is?'),
      (54, 'How socioeconomic class diverse do you feel the staff is?'),
      (54, 'How ability-wise diverse do you feel the staff is?'),
     ]
        
for i in range(5):
    questions.insert(42+i, nq[i])
    del questions[136+i]
    del questions[227]
    
lf = ['staff_racial_diversity', 'staff_gender_diversity', 'staff_sexual_diversity', 'staff_class_diversity', 'staff_ability_diversity']

for i in range(5):
    hardcoded_order[42+i] = ['Diverse', 'Somewhat diverse', 'Not at all diverse', 'Do not know/Not sure', 'No response']
    list_of_fields[42+i] = lf[i]


# In[637]:

for pid, response in responses.iteritems():
    response.insert(47, get_diversity(response[140], response[227])) #qid 54, qid 86
    del response[141]
    del response[227]
    
questions.insert(47, (54, "Feel free to elaborate on your staff diversity responses")) #qid 54, qid 86
del questions[141]
del questions[227]

list_of_fields[47] = 'staff_diversity_freeform'


# In[638]:

for pid, response in responses.iteritems():
    # board diversity
    for i in range(5):
        response.insert(48+i, get_diversity(response[117+i], response[273]))
        del response[118+i]
        del response[273]

nq = [(41, 'How racially diverse do you feel the board is?'),
     (41, 'How gender diverse do you feel the board is?'),
      (41, 'How sexual-orientation diverse do you feel the board is?'),
      (41, 'How socioeconomically diverse do you feel the board is?'),
      (41, 'How ability-wise diverse do you feel the board is?'),
     ]
        
for i in range(5):
    questions.insert(48+i, nq[i])
    del questions[118+i]
    del questions[273]
    
lf = ['board_racial_diversity', 'board_gender_diversity', 'board_sexual_diversity', 'board_class_diversity', 'board_ability_diversity']

for i in range(5):
    hardcoded_order[48+i] = ['Diverse', 'Somewhat diverse', 'Not at all diverse', 'Do not know/Not sure', 'No response']
    list_of_fields[48+i] = lf[i]
    # hardcoded_order[48+i] = ['Diverse', 'Somewhat diverse', 'Not at all diverse', 'Do not know/Not sure', 'No response']


# In[639]:

for pid, response in responses.iteritems():
    response.insert(53, get_diversity(response[122], response[273])) #qid 41, qid 86
    del response[123]
    del response[273]
    
questions.insert(53, (54, "Feel free to elaborate on your board diversity responses"))
del questions[123]
del questions[273]

list_of_fields[53] = 'board_diversity_freeform'


# Question 54: `strengthen_staff`  
# Question 55: `strengthen_staff_other`
# 
# One of:
# 1. Budgeted professional development (training, conferences, etc.) for all staff
# 2. Budgeted professional development (training, conferences, etc.) for some staff
# 3. Key or all staff participate in strategic planning
# 4. Key or all staff participate in budget development
# 5. Staff sometimes represent or co-represent organization/executive director at meetings of collaborations, donors, board, etc.
# 6. The management supports distributed leadership (decisions pushed down to where work is done)
# 7. Other
# 8. Don't know/Not sure

# In[640]:

def get_staff(lines1, lines2, i_dont_know):
    r = ['Budgeted professional development (training, conferences, etc.) for all staff', 
         'Budgeted professional development (training, conferences, etc.) for some staff', 
         'Key or all staff participate in strategic planning', 
         'Key or all staff participate in budget development',
         'Staff sometimes represent or co-represent organization/executive director at meetings of collaborations, donors, board, etc.',
         'The management supports distributed leadership (decisions pushed down to where work is done)',
         'Other'
        ]
    lines = lines1 if lines1[0] != '-' else lines2
    if lines[0] == '-': return ['No response']
    else:
        supports = []
        if i_dont_know == '1': supports.append("Don't know/Not sure")
        for i, line in enumerate(lines):
            if line == '1':
                supports.append(r[i])
        return supports
    
def get_staff_freeform(text1, text2):
    text = text1 if len(text1) > len(text2) else text2
    if not text: return "No Response"
    else: return text


# In[641]:

for pid, response in responses.iteritems():
    freeform = get_staff_freeform(response[148], response[225])
    response.insert(54, get_staff(response[141:148], response[218:225], response[226]))
    del response[142:150]
    del response[211:220]
    response.insert(55, freeform)

questions.insert(54, (55, 'How does your organization strengthen its staff?'))
del questions[142:150]
del questions[211:220]
questions.insert(55, (55, 'If you indicated "Other", please elaborate.'))
    
list_of_fields[54] = 'strengthen_staff'
list_of_fields[55] = 'strengthen_staff_other'


# Question 56: `leader_leave_identify_interim`  
# Question 57: `leader_leave_hire_interim`  
# Question 58: `leader_leave_create_internal_comm_plan`  
# Question 59: `leader_leave_create_external_comm_plan`  
# Question 60: `leader_leave_funding_continuity`  
# Question 61: `leader_leave_transition_plan`  
# Question 62: `leader_leave_fiduciary_integrity`  
# 
# 1. Very prepared
# 2. Prepared
# 3. Neutral
# 4. Unprepared
# 5. Very unprepared
# 6. Do not know/Not sure
# 7. No response

# In[642]:

def get_effective(text):
    if not text: return "No Response"
    elif text == 'Do not know/ Not sure': return 'Do not know'
    else: return text


# In[643]:

for pid, response in responses.iteritems():
    for i in xrange(7):
        response.insert(56+i, get_effective(response[179+i]))
        del response[180+i]
    
    responses[pid] = response

new_q = ['If your leader were to leave suddenly (illness, etc.), do you believe the board is prepared to manage identifying interim leader(s)?',
        'If your leader were to leave suddenly (illness, etc.), do you believe the board is prepared to manage hiring interim executive director(s)?',
        'If your leader were to leave suddenly (illness, etc.) do you believe the board is prepared to manage an internal communications plan for staff?',
        'If your leader were to leave suddenly (illness, etc.) do you believe the board is prepared to manage an external communications plan for stakeholders and media?',
        'If your leader were to leave suddenly (illness, etc.) do you believe the board is prepared to ensure continuity with funding and contractual relationships?',
         'If your leader were to leave suddenly (illness, etc.) do you believe the board is prepared to create a transition plan?',
         'If your leader were to leave suddenly (illness, etc.) do you believe the board is prepared to work with financial staff to ensure fiduciary integrity?'
        ]
    
lof = ['leader_leave_identify_interim', 'leader_leave_hire_interim', 'leader_leave_create_internal_comm_plan', 'leader_leave_create_external_comm_plan', 'leader_leave_funding_continuity', 'leader_leave_transition_plan', 'leader_leave_fiduciary_integrity']

for i in xrange(7):
    questions.insert(56+i, (76, new_q[i]))
    del questions[180+i]
    list_of_fields[56+i] = lof[i]
    hardcoded_order[56+i] = ['Very prepared', 'Prepared', 'Neutral', 'Unprepared', 'Very unprepared', 'Do not know/Not sure', 'No response']


# Question 63: `size_board`

# In[644]:

def get_size_board(text):
    if not text: return 'No response'
    else: return text


# In[645]:

for pid, response in responses.iteritems():
    response.insert(63, get_size_board(response[131]))
    del response[132]
    responses[pid] = response
    
questions.insert(63, (40, 'What is the size of your board?'))
del questions[132]
list_of_fields[63] = 'size_board'
hardcoded_order[63] = sorted([i for i in set(uniq_ans(63, responses)[1]) if len(i) == 1]) + sorted([i for i in set(uniq_ans(63, responses)[1]) if len(i) == 2]) + sorted([i for i in set(uniq_ans(63, responses)[1]) if len(i) == 3]) + ['No response']


# In[646]:

print check_sizes()
execute_json_write(questions, responses, list_of_fields)


# In[647]:

import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(get_qindices("How many people are", questions))

