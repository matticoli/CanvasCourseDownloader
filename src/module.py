import os
from typing import List

import canvasapi.module, canvasapi.course, canvasapi.file
from bs4 import BeautifulSoup, Tag

from src.util import safe_name


class Module:
    def __init__(self, canvas_module: canvasapi.module.Module, canvas_course: canvasapi.course.Course):
        self.module = canvas_module
        self.course = canvas_course

        self.id = self.module.id
        self.name = self.module.name

        # self.due_date = self.assignment.due_at
        # self.created_date = self.assignment.created_at

        # TODO: This info can be stored like this but we should also dump JSON or pickles or something, I think

        self.items = []
        for module_item in self.module.get_module_items():
            self.items.append(ModuleItem(module_item, self.course))

    def download(self, directory: str, make_subdir: bool = True):
        # TODO: Are there any module things to download that aren't the items? Body text?

        module_safe = safe_name(self.id, self.name)

        if make_subdir:
            base_path = f"{directory}/{module_safe}/"
            if not os.path.exists(base_path):
                os.makedirs(base_path)
        else:
            base_path = f"{directory}/"

        for item in self.items:
            item.download(base_path)


class ModuleItem:
    def __init__(self, canvas_module_item: canvasapi.module.ModuleItem, canvas_course: canvasapi.course.Course):
        self.item = canvas_module_item
        self.course = canvas_course

        self.id = self.item.id
        self.name = self.item.title  # ModuleItems don't have names, apparently, but they do have titles

        self.page_body = None
        self.links = []
        self.files = []
        # TODO: Handle the other ModuleItem types ('Discussion', 'Assignment', 'Quiz', 'SubHeader',
        #  'ExternalUrl', 'ExternalTool')
        if self.item.type == 'File':
            # This is essentially the contents of Canvas.get_file. It doesn't seem possible to find
            # out the verifier query string from the ModuleItem metadata, and we need that there to
            # download the file and bypass the verification flow
            file = self.course.get_file(self.item.content_id)
            self.files.append(file)
        elif self.item.type == 'Page':
            module_page = self.course.get_page(self.item.page_url)
            try:
                self.page_body = BeautifulSoup(module_page.body, "lxml")
                # print(f"Body: {self.page_body.prettify()}")  # The description is an HTML document
                self.links = self.page_body.find_all('a', href=True)  # type: List[Tag]
            except AttributeError:
                print(module_page)
                # TODO: I wonder if this is what's causing module items that are just files not working
                print(f"Body: None")

    def download(self, directory: str):
        if self.files:
            for file in self.files:
                path = directory + safe_name(file.id, file.display_name)
                file.download(path)

        if self.page_body:
            path = directory + safe_name(self.id, self.name) + ".html"
            with open(path, 'w', encoding='utf-8', newline='\n') as item_file:
                item_file.write(self.page_body.prettify())
