# import multiprocessing
import threading
import time
from unittest import TestCase
import uuid  #this is used for testing to not generate same username and email when creating test user.
from flask import url_for

from app import create_app, db
from config import TestingConfig
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.models import User, LLMRecommendation

LOCAL_HOST = "http://127.0.0.1:5000"

class SeleniumTests(TestCase):
    def setUp(self):
        self.testApp =  create_app(TestingConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        db.create_all()
        # Franco Notes : below lines causing issues for Windows, because of the way multiprocessing works in Windows.
        # because multiprocessing on Windows uses spawn, spawn must pickle/copy the Flask app object ,
        # Flask contains local lambda/internal objects that cannot be pickled
        # Getting error like "AttributeError: Can't pickle local object 'create_app.<locals>.Config'"
        #self.server_thread = multiprocessing.Process(target=self.testApp.run)
        self.server_thread = threading.Thread( target=self.testApp.run,
                                              kwargs={
                                                    "host": "127.0.0.1",
                                                    "port": 5000,
                                                    "use_reloader": False,
                                                    "debug": False,
                                                    },
                                                    daemon=True)

        self.server_thread.start()
        time.sleep(1)  # Wait for the server to start

        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.get(LOCAL_HOST)
        return super().setUp()
    
    def tearDown(self):
        time.sleep(1)
        #self.server_thread.terminate()
        if hasattr(self, "driver"):
            self.driver.quit()
        db.engine.dispose()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        import os
        if os.path.exists("test.db"):
            os.remove("test.db")
        return super().tearDown()
    
    def js_click(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", element)

    def create_user_and_ai_plan(self):
        unique_id = str(uuid.uuid4())[:8]  # Generate a short unique ID for username and email
        self.test_username = f"testuser_{unique_id}"
        self.test_password = "password"
        user = User(
            username=self.test_username,
            email=f"{self.test_username}@example.com",
            name="Franco",
            age=30,
            gender="Male",
            height_cm=180,
            weight_kg=75,
            goal="Build strength",
            activity_level="Moderate",
            injury_notes="None",
        )
        user.set_password(self.test_password)
        db.session.add(user)
        db.session.commit()

        plan = [
            {
                "day": "Monday",
                "focus": "Upper Body",
                "exercises": [
                    {
                        "name": "Push-up",
                        "sets": "3",
                        "reps": "10",
                        "duration_minutes": "",
                        "notes": "Standard push-up",
                    }
                ],
            }
        ]
        reco = LLMRecommendation(
        user_id=user.id,
        llm_comments="Test AI plan",
        input_summary="{}",
        user_saved=True,
        is_current=True,
    )
        reco.set_training_plan(plan)
        reco.set_nutrition_plan([])
        db.session.add(reco)
        db.session.commit()

        return user, reco
    
    def login_test_user(self):
        self.driver.get(LOCAL_HOST + "/login")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        self.driver.find_element(By.NAME, "username").send_keys(self.test_username)
        self.driver.find_element(By.NAME, "password").send_keys(self.test_password)
        self.driver.find_element(
            By.CSS_SELECTOR,
            "input[type='submit'], button[type='submit']"
        ).click()

        WebDriverWait(self.driver, 10).until(
        EC.url_contains("/myprofile")
        )

    def test_ai_page_displays_existing_training_plan(self):
        self.create_user_and_ai_plan()
        self.login_test_user()

        self.driver.get(LOCAL_HOST + "/AI")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        self.assertIn("Push-up", self.driver.page_source)
        self.assertIn("Upper Body", self.driver.page_source)

    def test_ai_edit_button_enables_training_fields(self):
        self.create_user_and_ai_plan()
        self.login_test_user()

        self.driver.get(LOCAL_HOST + "/AI")

        edit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "training-global-edit"))
        )
        
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            edit_button
        )

        time.sleep(1)

        self.driver.execute_script(
            "arguments[0].click();",
            edit_button
        )

        name_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='name']"))
        )

        self.assertTrue(name_field.is_displayed())
        self.assertIsNone(name_field.get_attribute("readonly"))
    


    def test_ai_view_saved_recommendation_details(self):
        self.create_user_and_ai_plan()
        self.login_test_user()

        self.driver.get(LOCAL_HOST + "/AI")

        view_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".view-reco-btn"))
        )

        self.driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        view_button
        )

        time.sleep(1)

        self.driver.execute_script(
            "arguments[0].click();",
            view_button
        )

        details_panel = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "recommendation-details"))
        )

        self.assertTrue(details_panel.is_displayed())

    def test_ai_save_edited_plan_updates_page(self):
        self.create_user_and_ai_plan()
        self.login_test_user()

        self.driver.get(LOCAL_HOST + "/AI")

        edit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "training-global-edit"))
        )
        self.js_click(edit_button)

        name_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='name']"))
        )
        name_field.clear()
        name_field.send_keys("Bench Press")

        save_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "training-save-all-btn"))
        )
        self.js_click(save_button)

        WebDriverWait(self.driver, 10).until(
            lambda driver: "Bench Press" in driver.page_source
        )

        self.assertIn("Bench Press", self.driver.page_source)


    def test_ai_add_exercise_button_creates_new_form(self):
        self.create_user_and_ai_plan()
        self.login_test_user()

        self.driver.get(LOCAL_HOST + "/AI")

        edit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "training-global-edit"))
        )
        self.js_click(edit_button)

        original_forms = self.driver.find_elements(
            By.CSS_SELECTOR, "[data-training-exercise-form]"
        )

        add_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-training-add-exercise]"))
        )
        self.js_click(add_button)

        WebDriverWait(self.driver, 10).until(
            lambda driver: len(driver.find_elements(
                By.CSS_SELECTOR, "[data-training-exercise-form]"
            )) > len(original_forms)
        )

        updated_forms = self.driver.find_elements(
            By.CSS_SELECTOR, "[data-training-exercise-form]"
        )

        self.assertGreater(len(updated_forms), len(original_forms))


    def test_ai_remove_exercise_button_removes_form(self):
        self.create_user_and_ai_plan()
        self.login_test_user()

        self.driver.get(LOCAL_HOST + "/AI")

        edit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "training-global-edit"))
        )
        self.js_click(edit_button)

        original_forms = self.driver.find_elements(
            By.CSS_SELECTOR, "[data-training-exercise-form]"
        )

        remove_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-training-remove-exercise]"))
        )
        self.js_click(remove_button)

        updated_forms = self.driver.find_elements(
            By.CSS_SELECTOR, "[data-training-exercise-form]"
        )

        self.assertLessEqual(len(updated_forms), len(original_forms))


    def test_ai_temperature_slider_updates_display_value(self):
        self.create_user_and_ai_plan()
        self.login_test_user()

        self.driver.get(LOCAL_HOST + "/AI")

        slider = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "temperature-slider"))
        )

        self.driver.execute_script(
            """
            arguments[0].value = 0.75;
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            """,
            slider,
        )

        value_display = self.driver.find_element(By.ID, "temperature-value")

        self.assertEqual(value_display.text, "0.75")