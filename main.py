# -*- coding: utf-8 -*-

import sys
import webbrowser
from pathlib import Path
from typing import List

import canvasapi
from canvasapi import course, exceptions, module

from bs4 import BeautifulSoup, Tag

# User ID: 18425

# Canvas API URL
from tee import Tee

API_URL = "https://canvas.wpi.edu"
# Canvas API key
API_KEY = "7782~pu3VLqIb0SGVlQUhEtTlf0aWMVV02Y7WSCpWIZubhlNPRUtxsqWWOKxvVAuWICNh"

DOWNLOADS_PATH = "C:\\Users\\blward\\Documents\\College\\Canvas Exports\\Downloads"
downloads = Path(DOWNLOADS_PATH)

webbrowser.register("firefox", None,
                    webbrowser.BackgroundBrowser("C://Program Files//Mozilla Firefox//firefox.exe"))

def move_downloaded_files(course_safe: str):
    global downloads

    destination_folder = downloads / course_safe
    if not destination_folder.exists():
        destination_folder.mkdir()

    # Move all files from Downloads directory to folder named course_safe
    for child in downloads.iterdir():
        if child.is_dir():
            continue
        destination = destination_folder / child.relative_to(downloads)
        print(f"Moving {child} to {destination}")
        child.rename(destination)

if __name__ == '__main__':
    # Initialize a new Canvas object
    canvas = canvasapi.Canvas(API_URL, API_KEY)
    courses = canvas.get_courses()

    for course in courses:  # type: canvasapi.course.Course
        if course.id in [10187, 10410, 22135]:
            continue
        course_safe = f"{course.id}_{course.name.lower().strip().replace(' ', '_').replace('/', '-')}"
        download_links = []

        with open(f"records/{course_safe}.txt", "w", encoding="utf-8") as course_log:
            t = Tee(sys.stdout, course_log).open()

            print(f"Course: {course.name} ({course.id})")
            print(f"Date: {course.start_at} - {course.end_at} (created {course.created_at})")

            # Unauthorized:
            # students = course.get_users(enrollment_type=['student'])
            # for student in students:
            #     print(student)
            #
            # staff = course.get_users(enrollment_type=['teacher', 'ta'])
            # for member in staff:
            #     print(member)

            assignments = course.get_assignments()
            for assignment in assignments:
                print(assignment)
                print(f"Assignment: {assignment.name} ({assignment.id})")
                print(f"Created: {assignment.created_at}")
                print(f"Due: {assignment.due_at}")
                print(f"Download submission: {assignment.submissions_download_url}")
                if assignment.submissions_download_url:
                    download_links.append(assignment.submissions_download_url)

                if assignment.description:
                    desc_soup = BeautifulSoup(assignment.description, "lxml")
                    print(f"Description: {desc_soup.prettify()}")  # The description is an HTML document

                    desc_links = desc_soup.find_all('a', href=True)  # type: List[Tag]
                    for link in desc_links:
                        download_links.append(link['href'])
                        print(f"Description Link: {link['href']}")


            modules = course.get_modules()
            for module in modules: # type: canvasapi.module.Module
                print(f"Module: {module.name} ({module.id})")
                for module_item in module.get_module_items():
                    print(module_item)
                    if module_item.type == 'Page':
                        module_page = course.get_page(module_item.page_url)
                        print(f"Page: {module_page.title} ({module_page.page_id})")
                        module_page_soup = BeautifulSoup(module_page.body, "lxml")
                        # TODO: This should really go in its own file as well
                        print(f"Body: {module_page_soup.prettify()}")  # The description is an HTML document
                        module_page_links = module_page_soup.find_all('a', href=True)  # type: List[Tag]
                        for link in module_page_links:
                            download_links.append(link['href'])
                            print(f"Body Link: {link['href']}")


            try:
                files = course.get_files()
                for file in files:
                    print(f"File: {file.display_name} ({file.id})")
                    print(f"Date: {file.created_at} (last modified {file.modified_at})")
                    print(f"Type: {file.__getattribute__('content-type')}")
                    print(f"Link: {file.url}")
                    download_links.append(file.url)
            except canvasapi.exceptions.Unauthorized:
                print(f"File listing disabled for course")

            # TODO: Also get_quizzes

            t.close()

        # TODO: Download all collected links (maybe check if they have "canvas.wpi.edu" and "download" in them?)
        # TODO: Change all /preview links to /download?
        # TODO: Use youtube-dl on any video.wpi.edu links
        download_links = list(set(download_links))

        for link in download_links:
            webbrowser.get("firefox").open_new_tab(link)

        # Wait for human here because it will take quite a while to download all of these files
        input("Press any key when all files are downloaded for this course...")

        # Move all files from Downloads directory to folder named course_safe
        move_downloaded_files(course_safe)

        # Exit after the first course, for now
        # exit(1)
