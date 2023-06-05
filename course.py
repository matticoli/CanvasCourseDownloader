import os
import sys

import canvasapi.course, canvasapi.user, canvasapi.file

from src.assignment import Assignment
from src.filesystem import FileSystem
from src.module import Module
from src.util import safe_name

from dotenv import load_dotenv

load_dotenv() 

class Course:
    def __init__(self, canvas_course: canvasapi.course.Course, canvas_user: canvasapi.user.User, canvas_api: canvasapi.Canvas):
        self.course = canvas_course
        self.user = canvas_user
        self.api = canvas_api

        self.id = self.course.id
        self.name = self.course.name
        self.start_date = self.course.start_at
        self.end_date = self.course.end_at
        self.created_date = self.course.created_at

        self.modules = [Module(module, self.course) for module in self.course.get_modules()]
        self.assignments = [Assignment(assignment, self.user, self.api) for assignment in self.course.get_assignments()]

        self.files = FileSystem(self.course)
        print(self.files)


    def download(self):
        dir_name = f"./downloads/{safe_name(self.id, self.name)}"

        # If the course downloads directory doesn't exist, make it
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # Download all course modules and their module items
        for module in self.modules:
            module.download(dir_name + "/modules")

        # Download all of the assignments and their submissions
        for assignment in self.assignments:
            assignment.download(dir_name + "/assignments")

        self.files.download(dir_name + "/files")

        # TODO: Write JSON representation of the course and assignments here
        # self.__dict__  # Make sure this recursively dumps, or do it inside the assignment download too


if __name__ == "__main__":
    import canvasapi

    API_URL = os.getenv("CANVAS_API_URL", "NO_API_URL_SET")
    API_KEY = os.getenv("CANVAS_API_KEY", "NO_API_KEY_SET")
    if API_URL == "NO_API_URL_SET":
        print("Please set an API URL", file = sys.stderr)
        sys.stderr.flush()
        sys.exit(1)
    elif API_KEY == "NO_API_KEY_SET":
        print("Please set an API KEY", file = sys.stderr)
        sys.stderr.flush()
        sys.exit(2)

    canvas = canvasapi.Canvas(API_URL, API_KEY)
    user = canvas.get_current_user()

    courses = canvas.get_courses()
    for course in courses:
        c = Course(course, user, canvas)
        c.download()
