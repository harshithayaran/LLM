import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found.")

client = Groq(api_key=api_key)

model = "llama-3.3-70b-versatile"

def LLMAnswer(prompt):
  message={
      "role" : "user",
      "content" : prompt
  }
  messages = [message]
  response = client.chat.completions.create(model=model, messages = messages)
  answer = response.choices[0].message.content
  print(answer)


# Calling LLM based on prompts

prompt = """
#Role
You are customer support agent
#Task
Your taks is to classify the issue given by customer
#Constraints
Your have to catagorise the complains of the customers in billing, technical, return only.
#OUTPUT FORMAT
Your answer should be in one word only.
#Example
For example if issue is device not working then answer should be technical.
#Fall Back
If the issue not related to any of the constrains then answer should be Other.
This is a user complain : Hi girlfriend
"""

LLMAnswer(prompt)