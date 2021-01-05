from pathlib import Path

DOWNLOADS_PATH = "C:\\Users\\blward\\Documents\\College\\Canvas Exports\\Downloads"
downloads = Path(DOWNLOADS_PATH)

if __name__ == "__main__":
    course_safe = "00001_testcourse"
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
