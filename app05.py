import streamlit as st
import openai
import requests
from dotenv import load_dotenv
import os
from openpyxl import Workbook
import tempfile

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
canvas_api_token = os.getenv('CANVAS_API_TOKEN')

# Configure the OpenAI library with your API key
openai.api_key = openai_api_key

# Initialize global variable to store component IDs
component_ids = {}

# Function to get Canvas data
def get_canvas_data(api_token, course_id, ids):
    headers = {"Authorization": f"Bearer {api_token}"}
    base_url = f"https://scccd.instructure.com/api/v1/courses/{course_id}"
    endpoints = {
        "students": "/users",
        "final_exam": f"/assignments/{ids['final_exam_id']}/submissions",
        "quizzes": f"/quizzes/{ids['quiz_id']}/submissions",
        "discussions": f"/discussion_topics/{ids['discussion_id']}/entries",
        "study_plans": f"/assignments/{ids['study_plan_id']}/submissions",
        "extra_credit": f"/assignments/{ids['extra_credit_id']}/submissions"
    }
    data = {}
    for key, endpoint in endpoints.items():
        full_url = base_url + endpoint
        print(full_url)
        response = requests.get(full_url, headers=headers)
        print(response)
        if response.status_code == 200:
            data[key] = response.json()
        else:
            st.error(f"Failed to fetch {key}: {response.status_code} - {response.text}")
            data[key] = None
    return data

# Function to fetch course components
def fetch_course_components(course_id):
    headers = {"Authorization": f"Bearer {canvas_api_token}"}
    base_url = f"https://scccd.instructure.com/api/v1/courses/{course_id}"
    component_types = ['assignments', 'quizzes', 'discussion_topics']
    components = {}
    for ctype in component_types:
        response = requests.get(f"{base_url}/{ctype}", headers=headers)
        if response.status_code == 200:
            components[ctype] = {item['id']: item.get('name', item.get('title', "No Title Available")) for item in response.json()}
        else:
            st.error(f"Failed to fetch {ctype}: {response.status_code} - {response.text}")
            components[ctype] = {}
    return components

# Function to create a grade sheet summary
def create_grade_sheet_summary(data):
    summary = "Grade Sheet Summary:\n\n"
    print(data)
    for key, value in data.items():
        summary += f"{key.capitalize()}:\n"
        if value:
            for item in value:
                # Use .get() to handle missing keys more gracefully
                student_id = item.get('user_id', 'Unknown User ID')
                score = item.get('score', 'N/A')
                summary += f"Student: {student_id}, Score: {score}\n"
        else:
            summary += "No data available\n"
        summary += "\n"
    return summary

# Function to create Excel workbook
def create_excel_workbook(data, workbook_name):
    path = tempfile.gettempdir()
    full_path = os.path.join(path, f"{workbook_name}.xlsx")
    wb = Workbook()
    ws = wb.active
    ws.title = "Grade Sheet Summary"
    headers = ["Category", "Student ID", "Score"]
    ws.append(headers)
    for key, value in data.items():
        if value:
            for item in value:
                ws.append([key.capitalize(), item['user_id'], item.get('score', 'N/A')])
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

# Streamlit interface
st.title("Canvas Grade Sheet and Chatbot Assistant")
canvas_course_id = st.text_input("Enter Canvas Course ID")

if st.button("Fetch Component IDs"):
    component_ids.update(fetch_course_components(canvas_course_id))
    st.session_state['component_ids'] = component_ids  # Storing in session state if needed across reruns

if 'component_ids' in st.session_state and st.session_state['component_ids']:
    ids = {}
    ids['final_exam_id'] = st.selectbox('Select Final Exam ID', list(st.session_state['component_ids'].get('assignments', {}).keys()))
    ids['quiz_id'] = st.selectbox('Select Quiz ID', list(st.session_state['component_ids'].get('quizzes', {}).keys()))
    ids['discussion_id'] = st.selectbox('Select Discussion ID', list(st.session_state['component_ids'].get('discussion_topics', {}).keys()))
    ids['study_plan_id'] = st.selectbox('Select Study Plan ID', list(st.session_state['component_ids'].get('assignments', {}).keys()))
    ids['extra_credit_id'] = st.selectbox('Select Extra Credit ID', list(st.session_state['component_ids'].get('assignments', {}).keys()))

    excel_workbook_name = st.text_input("Enter Excel Workbook Name (without .xlsx extension)")

    if st.button("Get Summary and Create Workbook"):
        if canvas_course_id and excel_workbook_name and ids:
            data = get_canvas_data(canvas_api_token, canvas_course_id, ids)
            if all(value is not None for value in data.values()):
                summary = create_grade_sheet_summary(data)
                st.text_area("Grade Sheet Summary", summary)
                workbook_path = create_excel_workbook(data, excel_workbook_name)
                st.success(f"Workbook created at {workbook_path}")
            else:
                st.error("Data retrieval failed for some components. Check errors above.")
        else:
            st.error("Please provide all required information.")

# Separate section for the OpenAI chatbot
st.title("Python Programming Assistant")
user_input = st.text_input("Ask me anything about Python programming:", "")
if st.button("Submit Question"):
    if user_input:
        answer = call_openai_api(user_input)
        st.write("Answer:", answer)
    else:
        st.error("Please enter a question.")
