# -*- coding: utf-8 -*-

import os
import sys
import webbrowser

from pathlib import Path
from typing import List

import canvasapi
from canvasapi import course, exceptions, module

from bs4 import BeautifulSoup, Tag

from tee import Tee

# Canvas API URL
# TODO: Make this an environment variable or make this script interactive
API_URL = "https://canvas.wpi.edu"

# Canvas API key
# This is not an active key, but yours will be in approximately this format
API_KEY = os.getenv("CANVAS_API_KEY", "NO_API_KEY_SET")

# TODO: Make this an environment variable or make this script interactive
DOWNLOADS_PATH = os.getenv("DOWNLOADS_PATH", "./downloads/")
downloads = Path(DOWNLOADS_PATH)


# TODO: Split up into multiple files for script clarity?
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
    user = canvas.get_current_user()
    courses = canvas.get_courses()

    already_downloaded_courses = []

    # TODO: This should be cleaned and moved to a utility function
    for child in downloads.iterdir():
        if not child.is_dir():
            continue
        child = child.relative_to(downloads)
        try:
            already_downloaded_courses.append(int(str(child).split("_")[0]))
        except:
            continue
        print(child)

    for course in courses:  # type: canvasapi.course.Course
        # Check the downloads directory listing for course IDs and skip them here
        if course.id in already_downloaded_courses:
            continue

        # TODO: This string manipulation should not be inline
        course_safe = f"{course.id}_{course.name.lower().strip().replace(' ', '_').replace('/', '-').replace(':', '')}"

        download_links = []

        # TODO: There can probably be a cleaner API here where the Tee can be opened with a filename and a `with`
        with open(f"records/{course_safe}.txt", "w", encoding="utf-8") as course_log:
            t = Tee(sys.stdout, course_log).open()

            # TODO: This info can be stored like this but we should also dump JSON or pickles or something, I think
            print(f"Course: {course.name} ({course.id})")
            print(f"Date: {course.start_at} - {course.end_at} (created {course.created_at})")

            # TODO: Remove this; the typical student is apparently Unauthorized
            # students = course.get_users(enrollment_type=['student'])
            # for student in students:
            #     print(student)
            #
            # staff = course.get_users(enrollment_type=['teacher', 'ta'])
            # for member in staff:
            #     print(member)

            assignments = course.get_assignments()
            for assignment in assignments:
                # TODO: This info can be stored like this but we should also dump JSON or pickles or something, I think
                print(f"Assignment: {assignment.name} ({assignment.id})")
                print(f"Created: {assignment.created_at}")
                print(f"Due: {assignment.due_at}")
                print(f"Download submission: {assignment.submissions_download_url}")
                if assignment.submissions_download_url:
                    download_links.append(assignment.submissions_download_url)

                if assignment.description:
                    # TODO: This should probably be saved as a separate HTML file
                    desc_soup = BeautifulSoup(assignment.description, "lxml")
                    print(f"Description: {desc_soup.prettify()}")  # The description is an HTML document

                    desc_links = desc_soup.find_all('a', href=True)  # type: List[Tag]
                    for link in desc_links:
                        download_links.append(link['href'])
                        print(f"Description Link: {link['href']}")

            modules = course.get_modules()
            for module in modules:  # type: canvasapi.module.Module
                # TODO: This info can be stored like this but we should also dump JSON or pickles or something, I think
                print(f"Module: {module.name} ({module.id})")
                for module_item in module.get_module_items():
                    print(module_item)
                    # TODO: Also need to support type == File
                    if module_item.type == 'Page':
                        # TODO: This should probably be saved as a separate HTML file
                        module_page = course.get_page(module_item.page_url)
                        print(f"Page: {module_page.title} ({module_page.page_id})")
                        try:
                            module_page_soup = BeautifulSoup(module_page.body, "lxml")
                            # TODO: This should really go in its own file as well
                            print(f"Body: {module_page_soup.prettify()}")  # The description is an HTML document
                            module_page_links = module_page_soup.find_all('a', href=True)  # type: List[Tag]
                            for link in module_page_links:
                                download_links.append(link['href'])
                                print(f"Body Link: {link['href']}")
                        except AttributeError:
                            # TODO: I wonder if this is what's causing module items that are just files not working
                            print(f"Body: None")

            try:
                files = course.get_files()
                for file in files:
                    # TODO: This info can be stored like this but we should also dump JSON or pickles or something, I think
                    print(f"File: {file.display_name} ({file.id})")
                    print(f"Date: {file.created_at} (last modified {file.modified_at})")
                    print(f"Type: {file.__getattribute__('content-type')}")
                    print(f"Link: {file.url}")
                    download_links.append(file.url)
            except canvasapi.exceptions.Unauthorized:
                print(f"File listing disabled for course")

            # TODO: Also get_quizzes

            t.close()

        # TODO: Download all collected links (maybe check if they have "$API_URL" and "download" in them?)
        # TODO: Change all /preview links to /download?
        # TODO: Use youtube-dl on any video.wpi.edu links
        download_links = list(set(download_links))

        for link in download_links:
            webbrowser.get("firefox").open_new_tab(link)

        # Wait for human here because it will take quite a while to download all of these files
        # TODO: This is clunky; we should save files using curl or something directly if we can. Canvas might
        #  rely on a browser cookie though. If we could use curl, we could download right into the course directory.
        input("Press any key when all files are downloaded for this course...")

        # Move all files from Downloads directory to folder named course_safe
        move_downloaded_files(course_safe)
