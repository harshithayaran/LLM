import os
import json
from pypdf import PdfReader
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

#Funtion to read pdf
def readPdf(pdf_path):
  reader = PdfReader(pdf_path)
  pdf_text = ""
  for page in reader.pages:
    text = page.extract_text()
    if text:
      pdf_text += text + "\n"
  return pdf_text

#Reading resume from specific path
resume_path = r"C:\Users\91770\AI_Course\Project Files\Resume.pdf"
resume_text = readPdf(resume_path)
#print(resume_text)

#Reading skillset from path
skillSet_pdf = r"C:\Users\91770\AI_Course\Project Files\Job_Description_Sample.pdf"
skill_text = readPdf(skillSet_pdf)
#print(skill_text)

# Main working of resume skillset checker
my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
  raise ValueError("api key shi nhi hai")
model = "llama-3.3-70b-versatile"
client = Groq(api_key = my_api_key)
role = "system"
prompt = f""" You are an experienced technical recruiter.
You have been given skill set of candidate {resume_text} and skill set required for the job {skill_text}
Compare the candidate's resume with the job description.

Return:

1. Overall Match (%)
2. Matching Skills
3. Missing Skills
4. Strengths
5. Weaknesses
6. Suggestions for Improvement.
"""
#Structuring the output 
from pydantic import BaseModel
class skillParameter(BaseModel):
  matching_skills: list[str]
  missing_skills: list[str]
  strengths: list[str]
  weaknesses: list[str]
  suggestions: list[str]
  overall_match_percentage: int

schema = skillParameter.model_json_schema()

system_prompt = f""" You are an AI Resume Screening Assistant.
  Compare the resume with the job description.
  Return ONLY valid JSON that follows this schema.
{schema} """

message_system = {
  "role" : "system",
  "content" : system_prompt
}
response_format = {
  "type" : "json_object"
}
message = {
  "role" : role,
  "content" : prompt
}
my_messages = [message_system, message]
response = client.chat.completions.create(model=model, messages = my_messages, response_format = response_format)
answer = response.choices[0].message.content

#Validating Json file agains the schema
json_file = json.loads(answer)
result = skillParameter(**json_file)

#Printing result
print(f"\nOverall Match: {result.overall_match_percentage}%")
print("\nMatching Skills:")
for skill in result.matching_skills:
  print("-", skill)
print("\nMissing Skills:")
for skill in result.missing_skills:
  print("-", skill)
print("\nStrengths:")
for strength in result.strengths:
  print("-", strength)
print("\nWeaknesses:")
for weakness in result.weaknesses:
  print("-", weakness)
print("\nSuggestions:")
for suggestion in result.suggestions:
  print("-", suggestion)
print("\n")
