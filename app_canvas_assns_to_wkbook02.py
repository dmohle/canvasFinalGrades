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

def fetch_students(course_id):
    base_url = f"https://scccd.instructure.com/api/v1/courses/{course_id}/students"
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return a list of students
    else:
        print(f"Failed to fetch students: {response.status_code}")
        return []

def fetch_submission(course_id, assignment_id, student_id):
    base_url = f"https://scccd.instructure.com/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}"
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return the submission details
    else:
        print(f"Failed to fetch submission for student {student_id} in assignment {assignment_id}: {response.status_code}")
        return None

def create_excel_workbook(students, assignments, course_id, filepath):
    wb = Workbook()
    ws = wb.active
    ws.title = "Student Grades"

    # Create columns for student ID and assignment IDs
    columns = ["Student ID"] + [str(assignment['id']) for assignment in assignments]
    ws.append(columns)

    # Fetch and append student grades for each assignment
    for student in students:
        student_id = student['id']
        row = [student_id]
        for assignment in assignments:
            assignment_id = assignment['id']
            submission = fetch_submission(course_id, assignment_id, student_id)
            if submission:
                row.append(submission.get('score', 'N/A'))
            else:
                row.append('N/A')
        ws.append(row)

    # Save the workbook
    wb.save(filepath)
    print(f"Workbook saved at {filepath}")

# Specify the Canvas course ID and path for the Excel file
course_id = '105391'
filepath = 'C:/2024_Spring/grades/experimental/studentGrades.xlsx'

# Fetch assignments, students, and create the workbook
assignments = fetch_assignments(course_id)
students = fetch_students(course_id)
if assignments and students:
    create_excel_workbook(students, assignments, course_id, filepath)
else:
    print("Failed to fetch assignments or students.")
