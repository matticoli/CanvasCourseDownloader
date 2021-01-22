import os

import canvasapi.course, canvasapi.folder

from src.util import safe_name


class FileSystem:
    def __init__(self, canvas_course: canvasapi.course.Course):
        self.course = canvas_course
        self.root_folder = None

        for folder in self.course.get_folders():
            # There's always a "course files" directory that is the root of the Canvas filesystem
            if folder.name == "course files":
                self.root_folder = folder
                break

        if self.root_folder is not None:
            # We handle the root directory specially since we don't need another nested folder
            self.files = []
            self.folders = []
            for folder in self.root_folder.get_folders():
                self.folders.append(Folder(folder, self.course))

            for file in self.root_folder.get_files():
                self.files.append(file)
        else:
            print("Couldn't find root folder of filesystem; skipping file download")

    def download(self, directory: str, make_subdir: bool = True):

        # If we couldn't find the root folder (no files or permission denied), skip trying
        if not self.root_folder:
            return

        for folder in self.folders:
            folder.download(directory, make_subdir)

        for file in self.files:
            path = f"{directory}/" + safe_name(file.id, file.display_name)
            print(f"Downloading {path}")
            file.download(path)


class Folder:
    def __init__(self, canvas_folder: canvasapi.folder.Folder, canvas_course: canvasapi.course.Course):
        self.folder = canvas_folder
        self.course = canvas_course

        self.id = self.folder.id
        self.name = self.folder.name

        # self.due_date = self.assignment.due_at
        # self.created_date = self.assignment.created_at

        # TODO: This info can be stored like this but we should also dump JSON or pickles or something, I think

        self.files = []
        self.subfolders = []
        for subfolder in self.folder.get_folders():
            self.subfolders.append(Folder(subfolder, canvas_course))

        for file in self.folder.get_files():
            self.files.append(file)

    def download(self, directory: str, make_subdir: bool = True):

        folder_safe = safe_name(self.id, self.name)

        if make_subdir:
            base_path = f"{directory}/{folder_safe}/"
            if not os.path.exists(base_path):
                os.makedirs(base_path)
        else:
            base_path = f"{directory}/"

        for folder in self.subfolders:
            folder.download(base_path)

        for file in self.files:
            path = base_path + safe_name(file.id, file.display_name)
            print(f"Downloading {path}")
            file.download(path)
