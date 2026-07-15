import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
  raise ValueError("api key shi nhi hai")
model = "llama-3.3-70b-versatile"
role = "user"
client = Groq(api_key = my_api_key)
prompt1 = "Hello"
prompt2 = "Give a complete roadmap to become AI Engineer"
prompt3 = "Give a detailed roadmap to become AI Engineer in 1000 words"
prompts = [prompt1, prompt2, prompt3]
for prompt in prompts:
  message = {
    "role" : role,
    "content" : prompt
  }
  my_messages = [message]
  response = client.chat.completions.create(model = model, messages = my_messages)
  print(f"Prompt: {prompt} --> Your prompt tokens = {response.usage.prompt_tokens}  --> Completion tokens = {response.usage.completion_tokens} --> Total tokens = {response.usage.total_tokens} --> Finish reason : {response.choices[0].finish_reason}")
  