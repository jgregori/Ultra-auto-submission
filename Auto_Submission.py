# imports.
import os
import time
from datetime import datetime
import csv
import requests
import json

from Bb_rest_helper import Bb_Utils
from Bb_rest_helper import Get_Config
from Bb_rest_helper import Auth_Helper
from Bb_rest_helper import Bb_Requests

# Selenium imports.
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class Auto_submission():

    def __init__(self, base_url, token):
        self._token = token
        self._base_url = base_url
        self._req = Bb_Requests()

    def get_primary_course_id(self, course_id):
        self.external_id = f'externalId:{course_id}'
        self.course_url = f'{self._base_url}/learn/api/public/v3/courses/{self.external_id}'
        self.params={
            'fields':'id'
        }
        primary_id = self._req.Bb_GET(self.course_url, self._token, self.params)
        return primary_id['id']

    def yield_assessment_list(self, course_id):
        self.external_id = f'externalId:{course_id}'
        self.assignment_url = f'{self._base_url}/learn/api/public/v1/courses/{self.external_id}/contents'
        self.params = {
            'recursive': True,
            'contentHandler': 'resource/x-bb-asmt-test-link',
            'fields': 'id,title,contentHandler.gradeColumnId'
        }
        assignments = self._req.Bb_GET(
            self.assignment_url, self._token, self.params)
        for a in assignments['results']:
            yield a['id'], a['title'], a['contentHandler']['gradeColumnId']

    def yield_student_list(self, course_id):
        self.external_id = f'externalId:{course_id}'
        self.membership_url = f'{self._base_url}/learn/api/public/v1/courses/{self.external_id}/users'
        self.params = {
            'role': 'Student',
            'fields': 'userId,user.userName,courseRoleId',
        }
        students = self._req.Bb_GET(
            self.membership_url, self._token, self.params)
        try:
            for s in students['results']:
               yield s['userId'], s['user']['userName'], s['courseRoleId']
            
            while students['paging']['nextPage']:
                self.offset_url = students['paging']['nextPage']
                r = requests.get(f'{self._base_url}{self.offset_url}',headers={'Authorization':'Bearer '+self._token})
                students = json.loads(r.text)
                for s2 in students['results']:
                    yield s2['userId'], s2['user']['userName'], s2['courseRoleId']
        except: 
            pass
              

    def get_attempts(self, course_id, column_id):
        self.external_id = f'externalId:{course_id}'
        self.column_id = column_id
        self.attempt_url = f'{self._base_url}/learn/api/public/v2/courses/{self.external_id}/gradebook/columns/{self.column_id}/attempts'
        self.params = {}
        attempts = self._req.Bb_GET(self.attempt_url, self._token, self.params)
        for a in attempts['results']:
            yield a

    def api_attempt(self, course_id, user_id, column_id):
        self.user_id = user_id
        self.external_id = f'externalId:{course_id}'
        self.column_id = column_id
        self.attempt_url = f'{self._base_url}/learn/api/public/v2/courses/{self.external_id}/gradebook/columns/{self.column_id}/attempts'
        self.submission = 'Spicy jalapeno bacon ipsum dolor amet shank tail qui dolore reprehenderit porchetta venison beef ribs beef adipisicing ad. Leberkas aliquip meatloaf ground round doner, buffalo in alcatra laborum non excepteur. Swine minim labore prosciutto pork chop. Nisi beef ribs cupim, deserunt kielbasa irure corned beef do enim culpa. Turducken hamburger pariatur biltong strip steak landjaeger eiusmod venison. Incididunt andouille consequat, beef ribs elit doner proident venison pancetta porchetta.'
        self.payload = {
            "userId": self.user_id,
            "status": "NeedsGrading",
            "studentSubmission": self.submission
        }
        self.params = {}
        submission = self._req.Bb_POST(
            self.attempt_url,
            self._token,
            self.params,
            self.payload)
        print(submission)

    def create_attempt(
            self,
            user_name,
            user_pass,
            course_id_internal,
            assessment_id,
            submission_text,
            submission_file):
        self.user_name = user_name
        self.user_pass = user_pass
        self.course_id_internal = course_id_internal
        self.assessment_id = assessment_id
        self.submission_text = submission_text
        self.submission_file = submission_file
        try:
            # setup driver
            self.driver = webdriver.Chrome("./chromedriver")
            self.wait = WebDriverWait(self.driver,10, poll_frequency=5)
            # Get to login page.
            self.driver.get(self._base_url)
            # Accept cookies.
            self.driver.find_element_by_class_name("button-1").click()
            # Locate username field and enter username.
            self.username = self.driver.find_element_by_id("user_id")
            self.username.clear()
            self.username.send_keys(self.user_name)
            # Locate password field and enter password.
            self.password = self.driver.find_element_by_id("password")
            self.password.clear()
            self.password.send_keys(self.user_pass)
            # Click on submitt button to login.
            self.driver.find_element_by_id("entry-login").click()
            # Get to the target assignment.
            self.driver.get(
                f'{self._base_url}/ultra/courses/{self.course_id_internal}/outline/assessment/{self.assessment_id}/overview?courseId={self.course_id_internal}')
            self.wait.until(
                ec.element_to_be_clickable(
                    (By.CLASS_NAME, "label-button-attempt"))).click()
            # Open content editor
            self.wait.until(
                ec.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[1]/div[2]/bb-base-layout[1]/div[1]/main[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[1]/bb-assessment-attempt[1]/div[1]/div[1]/section[1]/div[1]/div[2]")))
            self.driver.find_element_by_xpath(
                "/html[1]/body[1]/div[1]/div[2]/bb-base-layout[1]/div[1]/main[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[1]/bb-assessment-attempt[1]/div[1]/div[1]/section[1]/div[1]/div[1]/bb-attempt-canvas[1]/div[1]/div[2]/ng-form[1]/bb-freeform-response-editor[1]/div[1]/div[1]/button[1]").click()
            self.wait.until(
                ec.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[1]/div[2]/bb-base-layout[1]/div[1]/main[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[1]/bb-assessment-attempt[1]/div[1]/div[1]/section[1]/div[1]/div[1]/bb-attempt-canvas[1]/div[1]/div[1]/ng-form[1]/bb-freeform-response-editor[1]/div[1]/div[1]/form[1]/bb-rich-text-editor[1]/div[1]")))
            self.content = self.driver.find_element_by_css_selector(
                ".ql-editor")
            self.content.send_keys(self.submission_text)
            self.file_abs_path = os.path.abspath(self.submission_file)
            # disable file picker
            self.driver.execute_script("""
            document.addEventListener('click', function(evt) {
            if (evt.target.type === 'file')
                evt.preventDefault();
            }, true)
            """)
            self.driver.find_element_by_xpath(
                "//span[@class='icon attachment-normal-icon']").click()
            self.wait.until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type=\"file\"]"))).send_keys(
                self.file_abs_path)
            self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH,
                     "/html[1]/body[1]/div[9]/div[1]/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/span[2]/button[1]"))).click()
            # Clicks on Submit button
            self.driver.find_element_by_xpath(
                "/html[1]/body[1]/div[1]/div[2]/bb-base-layout[1]/div[1]/main[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[1]/bb-assessment-attempt[1]/div[1]/footer[1]/div[1]/div[1]/button[2]").click()
            # Clicks to confirm and submit the assignment
            self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[9]/div/footer/div/div[2]/span[2]/button"))).click()
            time.sleep(4)

            if os.path.isfile('./reports/submissions.csv'):
                with open(f'./reports/submissions.csv', 'a', newline='') as csv_file:
                    self.fieldnames = [
                        'Timestamp',
                        'Course Id',
                        'Assignment Id',
                        'Username',
                        'Status']
                    self.writer = csv.DictWriter(
                        csv_file, fieldnames=self.fieldnames)
                    self.writer.writerow({'Timestamp': datetime.now(),
                                          'Course Id': self.course_id_internal,
                                          'Assignment Id': self.assessment_id,
                                          'Username': self.user_pass,
                                          'Status': 'OK'})
            else:
                with open(f'./reports/submissions.csv', 'a', newline='') as csv_file:
                    self.fieldnames = [
                        'Timestamp',
                        'Course Id',
                        'Assignment Id',
                        'Username',
                        'Status']
                    self.writer = csv.DictWriter(
                        csv_file, fieldnames=self.fieldnames)
                    self.writer.writeheader()
                    self.writer.writerow({'Timestamp': datetime.now(),
                                          'Course Id': self.course_id_internal,
                                          'Assignment Id': self.assessment_id,
                                          'Username': self.user_pass,
                                          'Status': 'OK'})
        except BaseException:
            self.driver.save_screenshot(f'./screenshots/{self.user_name}_{self.assessment_id}_{datetime.now()}.png')
            if os.path.isfile('./reports/submissions.csv'):
                with open(f'./reports/submissions.csv', 'a', newline='') as csv_file:
                    self.fieldnames = [
                        'Timestamp',
                        'Course Id',
                        'Assignment Id',
                        'Username',
                        'Status']
                    self.writer = csv.DictWriter(
                        csv_file, fieldnames=self.fieldnames)
                    self.writer.writerow({'Timestamp': datetime.now(),
                                          'Course Id': self.course_id_internal,
                                          'Assignment Id': self.assessment_id,
                                          'Username': self.user_pass,
                                          'Status': 'FAILED'})
            else:
                with open(f'./reports/submissions.csv', 'a', newline='') as csv_file:
                    self.fieldnames = [
                        'Timestamp',
                        'Course Id',
                        'Assignment Id',
                        'Username',
                        'Status']
                    self.writer = csv.DictWriter(
                        csv_file, fieldnames=self.fieldnames)
                    self.writer.writeheader()
                    self.writer.writerow({'Timestamp': datetime.now(),
                                          'Course Id': self.course_id_internal,
                                          'Assignment Id': self.assessment_id,
                                          'Username': self.user_pass,
                                          'Status': 'FAILED'})

        finally:
            self.driver.close()


if __name__ == '__main__':

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

    #a.api_attempt('sub_test_001', '_577_1','_15144_1')
    # a.get_attempts('sub_test_001','_15144_1')
    # a.create_attempt('javier_demo01','javier_demo01','_1638_1','_47144_1',s_text,'./Submission_test.docx')

    assignments = a.yield_assessment_list('javier')
    s_text = 'Bacon ipsum dolor amet tri-tip cow pork loin alcatra bacon jowl. Tenderloin ground round biltong, ribeye rump pig brisket meatball beef bresaola turducken ham hock fatback ham. Turkey andouille kevin kielbasa ham hock shankle. Brisket ball tip andouille meatball beef ribs corned beef prosciutto shank. Sausage chislic ball tip pork loin. Jowl andouille pork belly burgdoggen tail sausage tenderloin alcatra tongue picanha doner. Cupim biltong venison, doner meatball beef ribs ham hock bresaola landjaeger.'
    for ass in assignments:
        ass_id = ass[0]
        students = a.yield_student_list('javier')
        
        for stu in students:
           print(stu)
        
    print(a.get_primary_course_id('javier'))
        
    