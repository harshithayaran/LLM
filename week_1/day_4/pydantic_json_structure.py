import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
  raise ValueError("api key shi nhi hai")

model = "llama-3.3-70b-versatile"

#Structure the response
from pydantic import BaseModel
class Ticket(BaseModel):
  name : str
  email : str
  mobile : str
  date_of_complain : str
  complain_catagory : str

schema = Ticket.model_json_schema()

system_prompt = f""" Extract the personal information from the ticket strictly based on this schema and give a json output.
{schema}
"""

message_system = {
  "role" : "system",
  "content" : system_prompt
}

response_format = {
  "type" : "json_object"
}

text = "Hi, my name is harshit hayaran. I am from india. My mobile number is 767897667. My email is abc@email.com. I am having issue with my laptop. My girlfriend has broke up with me and married to someone else. please take my complain so that my laptop issue can be resolved. date of complain is of today"

prompt = f""" This is a customer ticket extract the name, mobile number, email, date of complain and complain cataogory based on {text}
"""
role = "system"

client = Groq(api_key = my_api_key)
messages = {
  "role" : role,
  "content" : prompt
}
my_messages = [message_system, messages]
#response = client.chat.completions.completions.create(model = model, messages = my_messages)
response = client.chat.completions.create(model = model, messages = my_messages, response_format=response_format)
answer = response.choices[0].message.content
print(answer)


#how to read json file
import json
raw_json = answer
json_file = json.loads(raw_json)
ticket = Ticket(**json_file)

print(ticket.name)
print(ticket.email)