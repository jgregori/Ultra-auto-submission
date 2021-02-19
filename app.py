import json
import typer
from Bb_rest_helper import Bb_Utils
from Bb_rest_helper import Get_Config
from Bb_rest_helper import Auth_Helper
from Bb_rest_helper import Bb_Requests
from Auto_Submission import Auto_submission

#'sub_test_002'
#'_1641_1'

def main(external_id:str = typer.Option(...,help='Course external id, as a string, format is: "sub_test_002"')):
    with open('./app_config.json') as json_file:
        data = json.load(json_file)
        s_text = data['submission_text']
        path_to_file = data['path_to_file']

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
    primary_id = a.get_primary_course_id(external_id) 
    assignments = a.yield_assessment_list(external_id)
    for ass in assignments:
        ass_id = ass[0]
        students = a.yield_student_list(external_id)
        for stu in students:
            a.create_attempt(
                stu[1],
                stu[1],
                primary_id,
                ass_id,
                s_text,
                path_to_file)

if __name__ == '__main__':
    typer.run(main)