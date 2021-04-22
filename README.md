# Course Downloader

A simple tool that uses the Instructure Canvas API to download part or all of your Canvas courses. Contributions welcome!

## Description

The Canvas Course Downloader takes advantage of personal API keys, which you can generate under your personal user 
profile settings, to access and download virtually all of the information for any enrolled or past course. This includes
assignment text, submissions, module items, files, etc.

## Getting Started

To run this program, you'll need to generate a personal API key in your user profile settings. Set the following 
environment variables (example values below):

```
API_URL="https://canvas.wpi.edu"
API_KEY="7782~pu3VLqIb0SGVlQUhEtTlf0aWMVV02Y7WSCpWIZubhlNPRUtxsqWWOKxvVAuWICNh"
```

### Dependencies

This tool relies on the public Canvas API, its Python bindings, and BeautifulSoup for HTML parsing. All dependencies and
their versions are described in standard format in `requirements.txt`.

This script is relatively platform-independent and was developed on Windows 10 and several Linux distros.

### Installing

TODO
* How/where to download your program
* Any modifications needed to be made to files/folders

### Executing program

TODO
* How to run the program
* Step-by-step bullets

## Help

TODO
Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Benjamin Ward [@WardBenjamin](https://twitter.com/bwarddev)

Mani Kamali [@maniyar1](https://github.com/maniyar1)

## Version History

* 0.2 (In Progress)
    * Modularized application source to separate Canvas media types
    * Removed hard-coded URLs/keys/etc.
* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
