from api import apikey
from flask import Flask, request, jsonify
import pandas as pd
from csv import writer

import os
import time
import openai
import json
import jsonpickle

apikeys = apikey

app = Flask(__name__)


############## GPT PROMPT ####################
def gpt(inp):
    systems = {"role":"system","content":"""
    you are an Health Assistant your task is to help. 
               USER will pick one of the three problems:
HIV, PreP, Mental health
you have to follow these cases according to the user needs
1.Hiv:
    1.1 user can ask about HIV your have to provide him answer
    1.2 if user ask for list of clinics near him for HIV testing or consultancy. you have to ask him the city and after  return a json 
               in ``` ``` eg: 
            ```
              [
               {"city":"Kualalampur","problem":"HIV"}
              ] 

              ``` 



2.PrEP:
	2.1 If he said He already on Prep then you have to appreciate him
	
	2.2  if user said he wants to get on Prep then ask him locatoin
		 you have to ask him the city and after  return a json 
               in ``` ``` eg: 
            ```
              [
               {"city":"Kualalampur","problem":"PrEP"}
              ] 

              ``` 
	2.3 if user ask How PrEP works? give him good answer
		
	2.4	if user ask this 


		-Can I take PrEP?:
               
            IMPORTANT ask all  these question one by one, one question at a time.
			1.Do you have a sex partner who is HIV+ but are not on successful treatment?
			2. Do you have sex partners whose HIV status you don't know?
			3.Do you sometimes have sex without condom?
			4.Have you had a sexually transmitted infection in the previous 12 months?
			5.Have you ever used post-exposure prophylaxis (PEP)?
			6.Do you ever share equipment for injection drug use?
		------------IF any one YES => Take Prep


3. Mental Health:
               -Do you want to test your Depression!
                ask all these questions one by one 
                and test it from his answers.
			
				Q1/ Over the last two weeks, how often have you been bothered by the following problem: 1.Little interest or pleasure in doing things
				Q2/ Over the last two weeks, how often have you been bothered by the following problem: 2.Feeling down, depressed or hopeless
				Q3/ Over the last two weeks, how often have you been bothered by the following problem: 3.Trouble falling or staying asleep, or sleeping too much?
				Q4/ Over the last two weeks, how often have you been bothered by the following problem: 4.Feeling tired or having little energy
				Q5/ Over the last two weeks, how often have you been bothered by the following problem: 5.Poor appetite or overeating
				Q6/ Over the last two weeks, how often have you been bothered by the following problem: 6.Feeling bad about yourself - or that you are a failure or have let yourself or your family down
				Q7/ Over the last two weeks, how often have you been bothered by the following problem: 7.Trouble concentrating on things, such as reading the newspaper or watching television
				Q8/ Over the last two weeks, how often have you been bothered by the following problem:	8.Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual		
				Q9/ Over the last two weeks, how often have you been bothered by the following problem: 9.Thoughts that you would be better off dead, or of hurting yourself
			------------If score < 4 => test pass
			------------If score < 15 => Mild and Moderate
			------------If score < 27 => Severe 


		Q2/Screen for depression:
			-ASk Upper Questions

		Q3/Counseling services:
			 you have to ask him the city and after  return a json 
               in ``` ``` eg: 
            ```
              [
               {"city":"Kualalampur","problem":"mental"}
              ] 

              ```
    """}
    new_inp = inp
    new_inp.insert(0,systems)
    print("inp : \n ",new_inp)
    openai.api_key = apikeys
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=new_inp
    )
    return completion

############    GET CHATS BY USER ID ##################
def get_chats(id):
    path = str(os.getcwd())+'\\chats\\'+id+'.json'
    isexist = os.path.exists(path)
    if isexist:
        data = pd.read_json(path)
        chats = data.chat
        return  list(chats)
    else:
        return "No Chat found on this User ID."





############### APPEND NEW CHAT TO USER ID JSON FILE #################
def write_chat(new_data, id):
    with open("chats/"+id+".json",'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["chat"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)



################################ CHECK IF USER IS ALREADY EXIST IF NOT CREATE ONE ELSE RETURN GPT REPLY ##################
@app.route('/chat', methods=['POST'])
def check_user():
    
    ids = request.json['user_id']
    prompt = request.json['prompt']
    print("asd")
    path = str(os.getcwd())+'\\chats\\'+ids+'.json'
    # path = str(os.getcwd())+'\\'+"5467484.json"
    isexist = os.path.exists(path)
    if isexist:
        # try:
        print(path," found!")
        write_chat({"role":"user","content":prompt},ids)
        # print()
        chats = get_chats(ids)
        print(chats)
        send = gpt(chats)
        reply = send.choices[0].message
        print("reply    ",reply.content)
        write_chat({"role":"assistant","content":reply.content},ids)
        return {"message":reply,"status":"OK"}
        # except:
        #     return {"message":"something went wrong!","status":"404"}

    else:
        print(path," Not found!")
        dictionary = {
        "user_id":ids,
        "chat":[]


        }
        
        # Serializing json
        json_object = json.dumps(dictionary, indent=4)
        
        # Writing to sample.json
        with open(path, "w") as outfile:
            outfile.write(json_object)
        reply = check_user()
        return reply

####################   NEW ENPOINT GET CHATS ##############################
@app.route('/get_chats', methods=['POST'])
def get_chatss():
    ids = request.json['user_id']
    return jsonpickle.encode(get_chats(ids))

######################################################### clear chats
@app.route('/delete_chats', methods=['POST'])
def clear_chatss():
    ids = request.json['user_id']

    try:
        path =os.remove(str(os.getcwd())+'\\chats\\'+ids+'.json')
     
        return {"status":"OK","message":"success"}
 
    except :
        return { "status":"error","message":"Something went wrong,chat doesn't exist" }



if __name__ == '__main__':
    app.run()
    
