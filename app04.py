import streamlit as st
import openai
from dotenv import load_dotenv
import os
import requests
from openpyxl import Workbook
import tempfile

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
canvas_api_token = os.getenv('CANVAS_API_TOKEN')

# Configure the OpenAI library with your API key
openai.api_key = openai_api_key

# Function to get Canvas data
def get_canvas_data(api_token, course_id, ids):
    headers = {"Authorization": f"Bearer {api_token}"}
    base_url = f"https://scccd.instructure.com/api/v1/courses/{course_id}"
    endpoints = {
        "students": "/users",  # Corrected from /students to /users
        "final_exam": f"/assignments/{ids['final_exam_id']}/submissions",
        "quizzes": f"/quizzes/{ids['quiz_id']}/submissions",
        "discussions": f"/discussion_topics/{ids['discussion_id']}/entries",
        "study_plans": f"/assignments/{ids['study_plan_id']}/submissions",
        "extra_credit": f"/assignments/{ids['extra_credit_id']}/submissions"
    }
    data = {}
    for key, endpoint in endpoints.items():
        full_url = base_url + endpoint
        response = requests.get(full_url, headers=headers)
        if response.status_code == 200:
            data[key] = response.json()
        else:
            st.error(f"Failed to fetch {key}: {response.status_code} - {response.text}")
            data[key] = None
    return data

# Function to create a grade sheet summary
def create_grade_sheet_summary(data):
    summary = "Grade Sheet Summary:\n\n"
    for key, value in data.items():
        summary += f"{key.capitalize()}:\n"
        if value:
            for item in value:
                summary += f"Student: {item['user_id']}, Score: {item.get('score', 'N/A')}\n"
        else:
            summary += "No data available\n"
        summary += "\n"
    return summary

# Function to create Excel workbook
def create_excel_workbook(data, workbook_name):
    path = tempfile.gettempdir()  # Use the system's temp directory
    full_path = os.path.join(path, f"{workbook_name}.xlsx")
    wb = Workbook()
    ws = wb.active
    ws.title = "Grade Sheet Summary"
    headers = ["Category", "Student ID", "Score"]
    ws.append(headers)
    for key, value in data.items():
        if value:
            for item in value:
                ws.append([key.capitalize(), item.get('user_id', 'N/A'), item.get('score', 'N/A')])
        else:
            ws.append([key.capitalize(), "No data", "No data"])
    wb.save(full_path)
    return full_path

# Function to call OpenAI API with the specified chat bot configuration
def call_openai_api(user_input):
    client = openai.OpenAI(api_key=openai_api_key)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    return completion.choices[0].message['content']

# Streamlit interface for grade sheet summary
st.title("Canvas Grade Sheet Summary")
canvas_course_id = st.text_input("Enter Canvas Course ID")
ids = {'final_exam_id': '123', 'quiz_id': '456', 'discussion_id': '789', 'study_plan_id': '101', 'extra_credit_id': '112'}
excel_workbook_name = st.text_input("Enter Excel Workbook Name (without .xlsx extension)")

if st.button("Get Summary and Create Workbook"):
    if canvas_course_id and excel_workbook_name:
        data = get_canvas_data(canvas_api_token, canvas_course_id, ids)
        if all(value is not None for value in data.values()):
            summary = create_grade_sheet_summary(data)
            st.text_area("Grade Sheet Summary", summary)
            workbook_path = create_excel_workbook(data, excel_workbook_name)
            st.success(f"Workbook created at {workbook_path}")
        else:
            st.error("Data retrieval failed for some components. Check errors above.")
    else:
        st.error("Please provide both the Canvas Course ID and Excel Workbook Name")

# Separate section for the OpenAI chatbot
st.title("Python Programming Assistant")
user_input = st.text_input("Ask me anything about Python programming:", "")
if st.button("Submit Question"):
    if user_input:
        answer = call_openai_api(user_input)
        st.write("Answer:", answer)
    else:
        st.error("Please enter a question.")
