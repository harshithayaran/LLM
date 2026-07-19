import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from docx import Document
import json
load_dotenv()

#Reading pdf or docx files
def readFile(file_path):
  extension = Path(file_path).suffix.lower()
  if extension == ".pdf":
    pdf_text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
      text = page.extract_text()
      if text:
        pdf_text += text + "\n"
    return pdf_text
  elif extension == ".docx":
    doc_text = ""
    document = Document(file_path)
    for para in document.paragraphs:
      input_text = para.text
      if input_text:
        doc_text += input_text + "\n"
    return doc_text
  else : 
    raise ValueError("Please upload only pdf or docx files")
  

my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
  raise ValueError("api key shi nhi hai")
model = "llama-3.3-70b-versatile"
client = Groq(api_key = my_api_key)
job_description = readFile(r"C:\Users\91770\AI_Course\Project Files\AI_Engineer_Job_Description.pdf")

# Structuring job description
from pydantic import BaseModel
class jobDscrptn(BaseModel):
  role: str
  required_skills: list[str]
  preferred_skills: list[str]
  minimum_experience: float | None
  education_requirements: list[str]
  responsibilities: list[str]
jobD_schema = jobDscrptn.model_json_schema()

system_prompt = f"""
You are an expert HR assistant.

Your job is to analyze job descriptions and extract
structured information from them.

Return ONLY valid JSON matching this schema:

{jobD_schema}
IMPORTANT:
Do NOT return the schema itself.
Do NOT return fields like "properties", "title" or "type".
Fill the schema with actual information extracted from the job description.

If minimum experience is not mentioned, return null.
If information for a list is missing, return an empty list.
Do not invent information.
"""

user_prompt = f"""
Analyze the following job description:

{job_description}
"""

message_system={
    "role" : "system",
    "content" : system_prompt
}
message_user={
    "role" : "user",
    "content" : user_prompt
}
response_format={
    "type" : "json_object"
}
my_messages = [message_system, message_user]
response = client.chat.completions.create(model=model, messages=my_messages, response_format=response_format)
answer = response.choices[0].message.content
json_jobD = answer
#print(json_jobD)


# Structuring resumes
class Result(BaseModel):
  candidate_name: str
  score : float
  description : dict

class Experience(BaseModel):
  company : str| None = None
  role : str| None = None
  duration : str| None = None
  skills : list[str] = []
  description : str| None = None

class Resume(BaseModel):
  name : str| None = None
  email : str| None = None
  mobile : str| None = None
  exp : float| None = None
  education : list[str]
  projects : list[str]
  certification : list[str]
  experience : list[Experience]

resume_schema = Resume.model_json_schema()

def fetchFinalScore(job, resume):
  match_schema = Result.model_json_schema()
  prompt = f"""
  You are an HR recruiter.

  Compare the candidate's resume with the job description.

  JOB DESCRIPTION:
  {job.model_dump_json(indent=2)}

  CANDIDATE RESUME:
  {resume.model_dump_json(indent=2)}
  Return JSON matching this schema:

  {match_schema}

  Give me:

  1. Candidate name
  2. Matching skills
  3. Missing important skills
  4. Whether experience requirement is met
  5. Overall match percentage from 0 to 100
  6. A short final verdict

  Keep the response concise and easy to read.
  """
  message={
      "role": "user",
      "content" : prompt
  }
  messages=[message]
  response_format={
      "type": "json_object"
  }
  response = client.chat.completions.create(model=model, messages=messages, response_format=response_format)
  answer = response.choices[0].message.content
  final_json = json.loads(answer)
  return Result(**final_json)

def parsed_resume(resume_text):
  system_prompt = f"""
  You are an expert resume parser.

  Extract information from the resume based on its meaning,
  not only based on exact section headings.

  Different resumes may use different headings.

  For example:
  - Experience
  - Professional Experience
  - Work History
  - Employment
  - Internships

  These may all contain relevant experience.

  Skills may also appear in the skills section, work experience,
  internships or projects.

  Return ONLY valid JSON matching this schema:

  {resume_schema}

  Important rules:

  1. Do not invent information.
  2. If a value is not available, return null.
  3. If a list has no information, return an empty list.
  4. Include internships inside experiences.
  5. Extract skills mentioned across the entire resume.
  """
  user_prompt = f"""
  Parse the following resume:

  {resume_text}
  """
  message_system={
    "role" : "system",
    "content" : system_prompt
  }
  message_user={
    "role" : "user",
    "content" : user_prompt
  }
  messages=[message_system, message_user]
  response_format={
    "type": "json_object"
  }
  response=client.chat.completions.create(model=model, messages=messages, response_format=response_format)
  raw_output = response.choices[0].message.content
  data = json.loads(raw_output)
  resume = Resume(**data)
  return resume

# Final code
all_resume = Path("Resume_Folder")
all_results = []
for resume in all_resume.iterdir():
  if resume.suffix.lower() not in [".pdf", ".docx"]:
    continue
  print("\n File = ", resume)
  job = jobDscrptn(**json.loads(json_jobD))
  resume_text = readFile(resume)
  parse_resume = parsed_resume(resume_text)
  result = fetchFinalScore(job, parse_resume)
  all_results.append({
    "name" : result.candidate_name,
    "score" : result.score,
    "details" : result.description
  })
  all_results.sort(
    key=lambda candidate : candidate["score"],
    reverse = True
  )
  top2 = all_results[: 2]
  bottom2 = all_results[-2 :]
  print("TOP 2 CANDIDATES")
  for candidate in top2:
    print(
      candidate["name"],
      "-",
      candidate["score"],
      "%"
    )
  print(candidate["details"])
  print("LOWEST 2 CANDIDATES")
  for candidate in bottom2:
    print(
      candidate["name"],
      "-",
      candidate["score"],
      "%"
    )
    print(candidate["details"])
