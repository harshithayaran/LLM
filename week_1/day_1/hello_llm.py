import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
load_dotenv()         # importing env variables
my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
  raise ValueError("Wrong API Key")
client = Groq(api_key = my_api_key)
model = "llama-3.3-70b-versatile"
role = "user"
prompt = "Do you know rohit sharma"
my_message = {
  "role" : role,
  "content" : prompt
}
my_messages = [my_message]
response = client.chat.completions.create(model = model, messages = my_messages)
#print(response)
answer = response.choices[0].message.content
print(answer)