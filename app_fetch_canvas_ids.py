import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
canvas_api_token = os.getenv('CANVAS_API_TOKEN')

# Headers for authentication
headers = {"Authorization": f"Bearer {canvas_api_token}"}

def fetch_course_components(course_id):
    base_url = f"https://scccd.instructure.com/api/v1/courses/{course_id}"
    components = {}

    # Fetch assignments
    assignments_response = requests.get(f"{base_url}/assignments", headers=headers)
    if assignments_response.status_code == 200:
        components['assignments'] = assignments_response.json()
    else:
        print(f"Failed to fetch assignments: {assignments_response.status_code}")

    # Fetch quizzes
    quizzes_response = requests.get(f"{base_url}/quizzes", headers=headers)
    if quizzes_response.status_code == 200:
        components['quizzes'] = quizzes_response.json()
    else:
        print(f"Failed to fetch quizzes: {quizzes_response.status_code}")

    # Fetch discussions
    discussions_response = requests.get(f"{base_url}/discussion_topics", headers=headers)
    if discussions_response.status_code == 200:
        components['discussions'] = discussions_response.json()
    else:
        print(f"Failed to fetch discussions: {discussions_response.status_code}")

    return components

def display_component_ids(components):
    for component_type, items in components.items():
        print(f"\n{component_type.capitalize()}:")
        for item in items:
            # Handle different keys for the item's name/title
            name = item.get('name') or item.get('title') or "No Title Available"
            print(f"ID: {item['id']}, Name: {name}")

# Specify the Canvas course ID
course_id = '105391'

# Fetch and display the IDs for components
components = fetch_course_components(course_id)
display_component_ids(components)
