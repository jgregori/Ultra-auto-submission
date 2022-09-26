import sys
import json
from Bb_rest_helper import Bb_Utils
from Bb_rest_helper import Get_Config
from Bb_rest_helper import Auth_Helper
from Bb_rest_helper import Bb_Requests
from Auto_Submission import Auto_submission
import csv


def main():

    course_list = []

    try:
        with open('./app_config.json') as json_file:
            data = json.load(json_file)
            s_text = data['submission_text']
            path_to_file = data['path_to_file']

        with open('./external_course_id.csv', newline='')as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                course_list.append(row['external_course_id'])
        
    except FileNotFoundError:
        print('ERROR Configuration file not found')
        sys.exit()

    utils = Bb_Utils()
    utils.set_logging()
    # Learn.
    learn_conf = Get_Config('./credentials/learn_config.json')
    learn_url = learn_conf.get_url()
    learn_key = learn_conf.get_key()
    learn_secret = learn_conf.get_secret()

    # Authenticate and get the token (Learn).
    learn_auth = Auth_Helper(learn_url, learn_key, learn_secret)
    learn_token = learn_auth.learn_auth()

    # Rest API calls
    reqs = Bb_Requests()
    a = Auto_submission(learn_url, learn_token)
    a.create_folder('./reports')
    a.create_folder('./screenshots')
    for c in course_list:
        primary_id = utils.learn_convert_external_id(learn_url, learn_token, c)
        assignments = a.get_assessment_list(c)
        for ass in assignments:
            ass_id = ass['id']
            students = a.get_student_list(c)
            default_user_pass = stu['user']['userName']
            for stu in students:

                a.create_attempt(
                    stu['user']['userName'],
                    default_user_pass,
                    primary_id,
                    ass_id,
                    s_text,
                    path_to_file)


if __name__ == '__main__':
    main()
