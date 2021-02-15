# Autosubmissions for Learn Ultra assignments (BETA)

This is an internal Blackboard CLI tool that creates attempts in Learn Ultra assignments. This tool is built in Python with Selenium and and also leverages the Bb-rest-helper library to get assignment and student information.

The purpose of this tool is to facilitate the creation of multiple "demo" attempts that are required in RFP usability testing as well as easily populating demo courses.

Tested for the following Learn Saas versions: 3900.6

## Main features

- The tool takes a course id and external course id and retrives a list of assignments and students.

- For each one of the assignments, it loops over the student users and uses a selenium script to login, goes to the assingment page, opens a new attempt, inputs assingment text, uploads and attachment and hits submit.

- The tool generates a submission report that gather: Timestamp,Course Id,Assignment Id,Username,Status. If the submissions fails, it takes an screenshot that would allow to troubleshoot the issue.

- The tool currently takes about 45 seconds to create a submission,as it depends on Ultra UX and load times, it is still faster than you, and it does the work on your behalf, so dont complain ;) 

## Known issues

- As with any tool of this nature, we can´t guarantee compatibility between versions as changes in the UX will break the tool. If useful, reasonable effort will be done to maintain the functionality.

- Custom login pages with radical differences to what we currently have in our demo servers could break the tool, also any integration that open modals in the course interface could cause the tool to fail.

- Some users seem to fail for no reason, but still accuracy is quite high

- In this version you will need to have the exact same folder structure, so dont change any file or folder

## Setup (Assumes python 3.8+ installed on your computer)

1. Download or clone the repository
2. In the folder, create a python3 virtual environment with venv (if you dont have venv install with `pip3 install venv`)

    >`python3 -m venv env`

3. Activate the virtual environment

    >`source env/bin/activate`

4. Install the dependencies from the requirements.txt file

    >`pip3 install -r requirements.txt`

5. Create a credentials file named **learn_config.json** in the root folder, with the following structure. Do not change the name of this config file. You will need to create a new app in the developer portal as well as registering it on the target Learn Ultra instance with an user that has enough priviledges to get assignment and student information.

    >`{`
    >
    >`"url":"Learn server url",`
    >
    >`"key":"Learn key",`
    >
    >`"secret":"Learn secret"`
    >
    >`}`

6. Once done using the tool, deactivate the virtual environment

    >`deactivate`

## Usage

This is a command line tool created with typer, so will be launched from the terminal

Open a terminal and navegate to the folder 

call `--help` to get a list of the available options

>`python3 app.py --help`

In order to run the CLI, you will need to provide a `--course-id` and a `--external-course-id`. Here´s an example:

>`python3 app.py --course-id '_1641_1' --course-id-external 'sub_test_002'`

The app will run, creating the "submissions.csv" report and adding lines accordingly as the attempts are created.

## Backlog/Roadmap

If the tool is used, I will update it to provide more granularity, for instance different submission text and files to be randomly uploaded.