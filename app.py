# dH 5/25/24
# Fresno, CA
import streamlit as st
import openai
from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
canvas_api_token = os.getenv('CANVAS_API_TOKEN')

# Configure the OpenAI library with your API key
openai.api_key = openai_api_key

# Function to get Canvas data
def get_canvas_data(api_token, course_id):
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    base_url = f"https://canvas.instructure.com/api/v1/courses/{course_id}"
    endpoints = {
        "students": "/students",
        "final_exam": "/assignments/{final_exam_id}/submissions",
        "quizzes": "/quizzes/{quiz_id}/submissions",
        "discussions": "/discussion_topics/{discussion_id}/entries",
        "study_plans": "/assignments/{study_plan_id}/submissions",
        "extra_credit": "/assignments/{extra_credit_id}/submissions"
    }
    data = {}
    for key, endpoint in endpoints.items():
        response = requests.get(base_url + endpoint, headers=headers)
        if response.status_code == 200:
            data[key] = response.json()
        else:
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

# Streamlit interface
st.title("Canvas Grade Sheet Summary")
canvas_course_id = st.text_input("Enter Canvas Course ID")
excel_workbook_name = st.text_input("Enter Excel Workbook Name")

if st.button("Get Summary"):
    if canvas_course_id and excel_workbook_name:
        data = get_canvas_data(canvas_api_token, canvas_course_id)
        summary = create_grade_sheet_summary(data)
        st.text_area("Grade Sheet Summary", summary)
    else:
        st.error("Please provide both the Canvas Course ID and Excel Workbook Name")

# Function to call OpenAI API with the specified chat bot configuration
def call_openai_api(user_input):
    client = openai.OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    return completion.choices[0].message['content']

# Initialize Streamlit application for chatbot
st.title("Python Programming Assistant")
user_input = st.text_input("Ask me anything about Python programming:", "")
st.write("Your question:", user_input)  # Display user input

if user_input:
    answer = call_openai_api(user_input)
    st.write(answer)
