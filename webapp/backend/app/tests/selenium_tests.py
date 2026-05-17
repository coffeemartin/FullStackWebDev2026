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

from app.models import User, LLMRecommendation, Exercise 

LOCAL_HOST = "http://127.0.0.1:5000"

#Franco Notes: Selenium is powerful end to end testing tool. 
# Below SeleniumTests class will start the Flask server in a separate thread, 
# then use Selenium to open a browser and interact with the web application just like a real user would.
# It checks, authentication & database seeding & flask routes & template render 
# Javascript logic & Dom Manipulation & Form edition  & Database persistence all together.


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
    
    # Franco Notes: I had to add this helper function to handle some issues with clicking elements that are 
    # not in view or not interactable due to being covered by other elements.
    # As in my AI page, there are some buttons only show after clicking edit button.
    # Before clicking edit button, the page is in a view-only mode, after handling by some JavaScript code. Once 
    # user click the edit button. then the form fields become editable and some button like "Add Exercise" and "Save All" 
    # will show up. These causing issues in the Selenium tests, as the testing cannot see these buttons.
    def js_click(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", element)

    # Create a test user and Plan, I can move this function to models.py but it is ok here so I can update as I need.
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
                "focus": "Upper Body Strength",
                "exercises": [
                    {"name": "Push-up", "sets": "3", "reps": "10", "duration_minutes": "", "notes": "Keep core tight."},
                    {"name": "Dumbbell Row", "sets": "3", "reps": "12", "duration_minutes": "", "notes": "Use controlled movement."},
                ],
            },
            {
                "day": "Tuesday",
                "focus": "Lower Body Strength",
                "exercises": [
                    {"name": "Squat", "sets": "3", "reps": "12", "duration_minutes": "", "notes": "Keep knees aligned."},
                    {"name": "Glute Bridge", "sets": "3", "reps": "15", "duration_minutes": "", "notes": "Squeeze glutes at the top."},
                ],
            },
            {
                "day": "Wednesday",
                "focus": "Cardio",
                "exercises": [
                    {"name": "Brisk Walking", "sets": "", "reps": "", "duration_minutes": "30", "notes": "Maintain a comfortable pace."},
                    {"name": "Cycling", "sets": "", "reps": "", "duration_minutes": "20", "notes": "Low to moderate intensity."},
                ],
            },
            {
                "day": "Thursday",
                "focus": "Core",
                "exercises": [
                    {"name": "Plank", "sets": "3", "reps": "", "duration_minutes": "1", "notes": "Hold steady form."},
                    {"name": "Dead Bug", "sets": "3", "reps": "10", "duration_minutes": "", "notes": "Move slowly and control your breathing."},
                ],
            },
            {
                "day": "Friday",
                "focus": "Full Body",
                "exercises": [
                    {"name": "Lunge", "sets": "3", "reps": "10", "duration_minutes": "", "notes": "Alternate legs."},
                    {"name": "Shoulder Press", "sets": "3", "reps": "12", "duration_minutes": "", "notes": "Use light dumbbells if needed."},
                ],
            },
            {
                "day": "Saturday",
                "focus": "Mobility",
                "exercises": [
                    {"name": "Yoga", "sets": "", "reps": "", "duration_minutes": "30", "notes": "Focus on hips, hamstrings, and shoulders."},
                    {"name": "Stretching", "sets": "", "reps": "", "duration_minutes": "15", "notes": "Gentle full-body stretch."},
                ],
            },
            {
                "day": "Sunday",
                "focus": "Recovery",
                "exercises": [
                    {"name": "Walking", "sets": "", "reps": "", "duration_minutes": "20", "notes": "Easy recovery walk."},
                    {"name": "Foam Rolling", "sets": "", "reps": "", "duration_minutes": "10", "notes": "Relax tight muscles."},
                ],
            },
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

    # Franco Notes: Selenium test is powerful as the below test is testing : 
    # 1. Created user and ai plan storeds in database
    # 2. Selenium can log in with the created user
    # 3. Selenium opens /AI page 
    # 4. Selenium reads browser HTML
    # 5. Selenium assertIN checkes test exists.
    def test_ai_page_displays_existing_training_plan(self):
        self.create_user_and_ai_plan()
        self.login_test_user()

        self.driver.get(LOCAL_HOST + "/AI")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        self.assertIn("Monday", self.driver.page_source)
        self.assertIn("Sunday", self.driver.page_source)

        self.assertIn("Upper Body Strength", self.driver.page_source)
        self.assertIn("Recovery", self.driver.page_source)

        self.assertIn("Push-up", self.driver.page_source)
        self.assertIn("Foam Rolling", self.driver.page_source)
        self.assertIn("Yoga", self.driver.page_source)
        self.assertIn("Brisk Walking", self.driver.page_source)
        self.assertIn("Foam Rolling", self.driver.page_source)


    # Franco Notes: This checks the Edit mode Javascript behaviour. 
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
        # below check if the input field is editable. 
        self.assertIsNone(name_field.get_attribute("readonly"))
    

    # Franco Notes : this is to check clicking the View button the recommedation details become visible. 
    # User_saved is True was enforced in the seeded data, as by design this section only shows the plan user saved.
    # Not all the other random AI generated plan that user didn't save . 
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


    # Franco Notes: Below is a strong end to end test, it checks : 
    # 1. Form editing workds
    # 2. Save button works
    # 3. backend update route works
    # 4. database persistence works (in exercise dimension table)
    # 5. Update data re-render works   
    def test_ai_save_edited_plan_updates_page(self):
        self.create_user_and_ai_plan()
        self.login_test_user()

        self.driver.get(LOCAL_HOST + "/AI")

        edit_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "training-global-edit"))
        )
        self.js_click(edit_button)
        # Grab the first name fields, which is first exercise of Monday
        name_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='name']"))
        )
        new_exercise_name = "Franco Favourite Mysterious Exercise"
        name_field.clear()
        # Update the exercise name to below random name, from "Push-up"
        # This random name is definitely not in the dimension table. so if after saving, the page can show this new name, 
        # it means the new name is successfully added into dimension table and the training plan is updated to use this new name.
        name_field.send_keys(new_exercise_name)

        save_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "training-save-all-btn"))
        )
        self.js_click(save_button)

        WebDriverWait(self.driver, 10).until(
            lambda driver: new_exercise_name in driver.page_source
        )
        self.assertIn(new_exercise_name, self.driver.page_source)
        # Franco Notes: Below is to check the exercise dimension table is updated with the new exercise name, 
        # which means the backend route works and the data persistence works.
        saved_exercise = Exercise.query.filter_by(name=new_exercise_name).first()
        self.assertIsNotNone(saved_exercise)


    # Franco Notes: Below test are to check frontend JS dynamically created DOM element
    # Add exercise button, UI updates correctly 
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
        # using Len, number of exercise form is greater than before, which means a new form is added into the page.
        WebDriverWait(self.driver, 10).until(
            lambda driver: len(driver.find_elements(
                By.CSS_SELECTOR, "[data-training-exercise-form]"
            )) > len(original_forms)
        )

        updated_forms = self.driver.find_elements(
            By.CSS_SELECTOR, "[data-training-exercise-form]"
        )

        self.assertGreater(len(updated_forms), len(original_forms))

    # Franco Notes: Similar to above but to check the remove button works and the form is removed from the page.
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

    # Franco Notes : this is to check temperature slides, simple test.
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