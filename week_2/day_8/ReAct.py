import os
import re
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from time import sleep
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found.")
client = Groq(api_key=api_key)
model = "llama-3.3-70b-versatile"

def productPrice(product):
    product = product.lower()
    if product == "iphone":
        return 1000
    elif product == "macbook":
        return 2000
    else:
        return 0 

def calculator(expression):
    try:
        return eval(expression)
    except:
        return "calculation error"

tools = {
    "productPrice": productPrice,
    "calculator": calculator
}    

system_prompt = """
You are a customer support assistant.

You have these tools:
1) productPrice(product)
2) calculator(expression)

IMPORTANT:
call tools like this:
Action: productPrice("iphone")
Action: calculator("1000-200")
Never write:
productPrice(product="iPhone 17")

1. Think what you need to do next.
2. Call only one tool at a time.
3. Wait untill you get the result of a tool and never guess the answer of the tool.
4. Then decide your next action
5. When task is completed then only give your final answer

FORMAT:
Thought: what you need to do
Action: tool_name(argument)

When finished:
Final Answer: your answer

"""

def execute_agent(ques):
    message=[
        {
            "role" : "system",
            "content" : system_prompt
        },
        {
            "role": "user",
            "content" : ques
        }
    ]
    for i in range(5):
        print("\n----------------------------------")
        print("STEP", i + 1)
        print("------------------------------------")
        response = client.chat.completions.create(model=model, messages=message)
        answer = response.choices[0].message.content
        print(answer)

        #IF FINAL ANSWER IS RECIEVED
        if "Final Answer" in answer:
            break
        
        # Find the Action
        match = re.search(
            r"Action:\s*(\w+)\((.*?)\)",
            answer
        )

        if match:
            toolName = match.group(1)
            toolInput = match.group(2)
            toolInput = toolInput.strip()
            toolInput = toolInput.strip('"')

            #execute the tool
            if toolName in tools:
                tool = tools[toolName]
                observation = tool(toolInput)
            else:
                observation = "Tool not found"

            print("Observation: ", observation)

            #Add LLM response to memory
            message.append({
                "role" : "assistant",
                "content" : answer
            })

            message.append({
                "role" : "user",
                "content" :  "Observation: "
                    + str(observation)
            })

            sleep(5)

prompt = input("Ask question from assistant: ")
execute_agent(prompt)
                
#I wanna buy a macbook, I have currently 10000 rupees, how much will be left if I buy a macbook 