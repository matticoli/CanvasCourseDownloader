import os
from typing import List

import canvasapi.assignment, canvasapi.user, canvasapi.file
from bs4 import BeautifulSoup, Tag

from src.util import safe_name


class Assignment:
    # TODO: Take course instead of Canvas
    def __init__(self, canvas_assignment: canvasapi.assignment.Assignment, canvas_user: canvasapi.user.User, canvas_api: canvasapi.Canvas):
        self.assignment = canvas_assignment
        self.user = canvas_user
        self.api = canvas_api

        self.id = self.assignment.id
        self.name = self.assignment.name

        self.due_date = self.assignment.due_at
        self.created_date = self.assignment.created_at

        self.description = self.assignment.description
        self.links = []
        if self.description:
            desc_soup = BeautifulSoup(self.assignment.description, "lxml")
            desc_links = desc_soup.find_all('a', href=True)  # type: List[Tag]
            for link in desc_links:
                self.links.append(link.attrs)

        self.submission = self.assignment.get_submission(self.user)
        self.files = None
        self.text = None
        if not self.submission.missing:
            if not self.submission.submission_type:
                print(f"Assignment submission has no submission type??")
            if self.submission.submission_type == "online_upload":
                # For some reason the API returns dictionaries instead of File objects
                self.files = [canvasapi.file.File(self.submission._requester, file_attributes) for file_attributes in
                              self.submission.attachments]
            elif self.submission.submission_type == "online_text_entry":
                self.text = self.submission.body
            else:
                print(
                    f"Found assignment with unknown submission type {self.submission.submission_type}; can't download")
        else:
            print(f"Submission for assignment {self.assignment} is missing")

    def download(self, directory: str, make_subdir: bool = True):
        assignment_safe = safe_name(self.id, self.name)

        if make_subdir:
            base_path = f"{directory}/{assignment_safe}/"
            if not os.path.exists(base_path):
                os.makedirs(base_path)
        else:
            base_path = f"{directory}/"

        if self.files:
            for file in self.files:
                path = base_path + safe_name(file.id, file.display_name)
                file.download(path)

        if self.text:
            path = base_path + safe_name(self.id, "submission.txt")
            with open(path, 'w', encoding='utf-8', newline='\n') as text_file:
                text_file.write(self.text)

        if self.description:
            path = base_path + assignment_safe + ".html"
            with open(path, 'w', encoding='utf-8', newline='\n') as assignment_file:
                assignment_file.write(self.description)

        for link in self.links:
            try:
                link_href = link['href']
                link_name = link['title']
                link_class = link['class']
            except KeyError:
                print(f"Didn't try to download file from {link} since it was malformed or missing an attribute")
                continue

            if "instructure_file_link" in link_class:
                link_file_id = int(link_href.split('/')[-2])  # Based on the standard download link format
                print(f"Trying to download {link} as a Canvas file")
                path = base_path + safe_name(link_file_id, link_name)
                linkfile = canvasapi.file.File(self.assignment._requester, {"id": link_file_id, "display_name": "link_name", "url": link_href})
                linkfile.download(path)
            else:
                print(f"Didn't try to download file from {link} since it wasn't a Canvas file")
