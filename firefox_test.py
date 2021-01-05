import webbrowser

url = "https://canvas.wpi.edu"

if __name__ == "__main__":
    webbrowser.register("firefox", None,
                        webbrowser.BackgroundBrowser("C://Program Files//Mozilla Firefox//firefox.exe"))

    webbrowser.get("firefox").open_new_tab(url)
