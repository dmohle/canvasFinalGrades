import requests
import os
from dotenv import load_dotenv
from openpyxl import Workbook

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
canvas_api_token = os.getenv('CANVAS_API_TOKEN')

# Headers for authentication
headers = {"Authorization": f"Bearer {canvas_api_token}"}

def fetch_assignments(course_id):
    base_url = f"https://scccd.instructure.com/api/v1/courses/{course_id}/assignments"
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return a list of assignments
    else:
        print(f"Failed to fetch assignments: {response.status_code}")
        return []

def create_excel_workbook(assignments, filepath):
    wb = Workbook()
    ws = wb.active
    ws.title = "Student Grades"

    # Create columns for stuID and up to ten assignment IDs
    columns = ["stuID"] + [str(assignment['id']) for assignment in assignments[:10]]
    ws.append(columns)

    # Save the workbook
    wb.save(filepath)
    print(f"Workbook saved at {filepath}")

# Specify the Canvas course ID and path for the Excel file
course_id = '105391'
filepath = 'C:/2024_Spring/grades/experimental/studentGrades.xlsx'

# Fetch assignments and create the workbook
assignments = fetch_assignments(course_id)
create_excel_workbook(assignments, filepath)
