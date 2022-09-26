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

    def __init__(self, learn_url, token):
        self._token = token
        self._learn_url = learn_url
        self._req = Bb_Requests()

    def create_folder(self, path):
        self.path = path
        try:
            os.mkdir(self.path, 0o777)
        except FileExistsError:
            pass

    def get_assessment_list(self, course_id):
        self.external_id = f'externalId:{course_id}'
        self.assignment_url = f'/learn/api/public/v1/courses/{self.external_id}/contents'
        self.params = {
            'recursive': True,
            'contentHandler': 'resource/x-bb-asmt-test-link',
            'fields': 'id,title,contentHandler.gradeColumnId'
        }
        assignments = self._req.Bb_GET(
            self._learn_url, self.assignment_url, self._token, self.params)
        return assignments

    def get_student_list(self, course_id):
        self.external_id = f'externalId:{course_id}'
        self.membership_url = f'/learn/api/public/v1/courses/{self.external_id}/users'
        self.params = {
            'role': 'Student',
            'fields': 'userId,user.userName,courseRoleId'
        }
        students = self._req.Bb_GET(
            self._learn_url, self.membership_url, self._token, self.params)
        return students

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
            self.wait = WebDriverWait(self.driver, 100, poll_frequency=5)
            # Get to login page.
            self.driver.get(self._learn_url)
            # Accept cookies.
            self.wait.until(
                ec.element_to_be_clickable(
                    (By.CLASS_NAME, "button-1"))).click()
            # Locate username field and enter username.
            self.username = self.driver.find_element(By.ID, "user_id")
            # find_element_by_id("user_id")
            self.username.clear()
            self.username.send_keys(self.user_name)
            # Locate password field and enter password.
            self.password = self.driver.find_element(By.ID, "password")
            self.password.clear()
            self.password.send_keys(self.user_pass)
            # Click on submitt button to login.
            self.driver.find_element(By.ID, "entry-login").click()
            # Get to the target assignment.
            self.driver.get(
                f'{self._learn_url}/ultra/courses/{self.course_id_internal}/outline/assessment/{self.assessment_id}/overview?courseId={self.course_id_internal}')
            self.wait.until(
                ec.element_to_be_clickable(
                    (By.CLASS_NAME, "label-button-attempt"))).click()
            # Open content editor
            # Wait until content editor is loaded in the page.
            self.wait.until(
                ec.presence_of_element_located(
                    (By.XPATH,
                        "/html/body/div[1]/div[2]/bb-base-layout/div/main/div[5]/div/div/div/div/div/bb-assessment-attempt/div/div/section/div[1]/div[1]/bb-attempt-canvas/div"
                     )))
            # Get to content editor and click on it
            self.content = self.driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div[2]/bb-base-layout/div/main/div[5]/div/div/div/div/div/bb-assessment-attempt/div/div/section/div[1]/div[1]/bb-attempt-canvas/div/div[2]/ng-form/bb-freeform-response-editor/div/div/form/bb-rich-text-editor/div/div/div/div[1]")
            self.content.click()

            # Send submission text and file.
            self.content.send_keys(self.submission_text)
            self.file_abs_path = os.path.abspath(self.submission_file)
            # disable file picker
            self.driver.execute_script("""
            document.addEventListener('click', function(evt) {
            if (evt.target.type === 'file')
                evt.preventDefault();
            }, true)
            """)
            self.driver.find_element(
                By.XPATH, "//span[@class='icon attachment-normal-icon']").click()
            self.wait.until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type=\"file\"]"))).send_keys(
                self.file_abs_path)

            # close file modals
            self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[14]/div[3]/div/div/div[3]/button[2]"))).click()

            # click outside to close the editor and allow the submission button
            # to be enabled.

            self.driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div[2]/bb-base-layout/div/bb-pagehelp/div/bb-ui-pagehelp/div/button").click()
            # Clicks on Submit button
            self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH,
                     "/html/body/div[1]/div[2]/bb-base-layout/div/main/div[5]/div/div/div/div/div/bb-assessment-attempt/div/footer/div/div[2]/div/div/button[2]"))).click()

            # Clicks to confirm and submit the assignment
            self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[14]/div/footer/div/div[2]/span[2]/button"))).click()

            # Clicks to close submission recipt --> update to 3900.48
            self.wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH,
                     "/html/body/div[14]/div/footer/div/div[2]/span[1]/div/button"))).click()

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
                                          'Username': self.user_name,
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
                                          'Username': self.user_name,
                                          'Status': 'OK'})
        except NoSuchElementException:
            self.driver.save_screenshot(
                f'./screenshots/{self.user_name}_{self.assessment_id}_{datetime.now()}.png')
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
