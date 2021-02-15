import typer
from Bb_rest_helper import Bb_Utils
from Bb_rest_helper import Get_Config
from Bb_rest_helper import Auth_Helper
from Bb_rest_helper import Bb_Requests
from Auto_Submission import Auto_submission

#'sub_test_002'
#'_1641_1'

def main(course_id_external:str = typer.Option(...,help='Course external id, as a string, format is: "sub_test_002"'),
    course_id:str = typer.Option(...,help= 'Course Id, as a string, format is: "_1641_1"')):
    # Learn.
    learn_conf = Get_Config('./learn_config.json')
    learn_url = learn_conf.get_url()
    learn_key = learn_conf.get_key()
    learn_secret = learn_conf.get_secret()

    # Authenticate and get the token (Learn).
    learn_auth = Auth_Helper(learn_url, learn_key, learn_secret)
    learn_token = learn_auth.learn_auth()

    # Rest API calls
    reqs = Bb_Requests()
    a = Auto_submission(learn_url, learn_token)
    assignments = a.yield_assessment_list(course_id_external)
    s_text = 'Bacon ipsum dolor amet tri-tip cow pork loin alcatra bacon jowl. Tenderloin ground round biltong, ribeye rump pig brisket meatball beef bresaola turducken ham hock fatback ham. Turkey andouille kevin kielbasa ham hock shankle. Brisket ball tip andouille meatball beef ribs corned beef prosciutto shank. Sausage chislic ball tip pork loin. Jowl andouille pork belly burgdoggen tail sausage tenderloin alcatra tongue picanha doner. Cupim biltong venison, doner meatball beef ribs ham hock bresaola landjaeger.'
    for ass in assignments:
        ass_id = ass[0]
        students = a.yield_student_list(course_id_external)
        for stu in students:
            a.create_attempt(
                stu[1],
                stu[1],
                course_id,
                ass_id,
                s_text,
                './files/Submission_test.docx')

if __name__ == '__main__':
    typer.run(main)