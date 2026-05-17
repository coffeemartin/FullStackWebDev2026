from unittest import TestCase
from app.ai_service import normalize_exercise_name, normalize_training_plan
from app import create_app, db
from config import TestingConfig
from app.controllers import calculate_bmi_result, get_bmi_fitness_points
from app.controllers import normalise_ai_generation_options

class BasicTests(TestCase):
    def setUp(self):
        testApp =  create_app(TestingConfig)
        self.app_context = testApp.app_context()
        self.app_context.push()
        db.create_all()
        return super().setUp()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()
        # Franco Notes: Originally below code was not needed cuz I used in-memory SQLite for testing, 
        # but I had to switch to file-based SQLite for testing due to the issues with in-memory SQLite and Selenium tests.
        import os
        if os.path.exists("test.db"):
            os.remove("test.db")

        return super().tearDown()
    

# Franco Notes: these are some testing for the testing of AI generation, without calling OpenAI . 
    def test_ai_options_accept_valid_values(self):
        days, temperature = normalise_ai_generation_options("45", "0.7")

        self.assertEqual(days, 45)
        self.assertEqual(temperature, 0.7)


    def test_ai_options_clamp_days_and_temperature(self):
        days, temperature = normalise_ai_generation_options("999", "2")

        self.assertEqual(days, 90)
        self.assertEqual(temperature, 1.0)


    def test_ai_options_default_invalid_values(self):
        days, temperature = normalise_ai_generation_options("abc", "not-a-number")

        self.assertEqual(days, 30)
        self.assertEqual(temperature, 0.0)


    def test_ai_options_minimum_values(self):
        days, temperature = normalise_ai_generation_options("-5", "-0.8")

        self.assertEqual(days, 1)
        self.assertEqual(temperature, 0.0)
    
# Franco Notes: this is AI service related tests, because I had issues where the plan AI generated had exercise names like "Pushups or / Bench Press" 
# These are not standard training exercises names. Because these names (when it is new and didn't appear in exercise dimension table ) 
# these new names will be added into the dimention table.
# So to avoid the exercise naming explosion, I performed the normalization of AI generated exercise name. 

# trim the name when sees OR. 
    def test_normalize_exercise_name_or_pattern(self):
        result = normalize_exercise_name(
            "Pushups or Bench Press"
        )

        self.assertEqual(result, "Pushups")
# trim the name when sees /. 
    def test_normalize_exercise_name_slash_pattern(self):
        result = normalize_exercise_name(
            "Push-up / Incline Push-up"
        )

        self.assertEqual(result, "Push-up")

# trim the white space, otherwise it will be added into the exercise dimension table as "   Squat   " which is not good.
    def test_normalize_exercise_name_trim_whitespace(self):
        result = normalize_exercise_name(
            "   Squat   "
        )

        self.assertEqual(result, "Squat")

    def test_normalize_training_plan(self):

        plan = {
            "weekly_training_plan": [
                {
                    "day": "Monday",
                    "focus": "Chest",
                    "exercises": [
                        {
                            "name": "Pushups or Bench Press"
                        },
                        {
                            "name": "Plank / Side Plank"
                        }
                    ]
                }
            ]
        }

        normalized = normalize_training_plan(plan)

        exercises = normalized["weekly_training_plan"][0]["exercises"]

        self.assertEqual(exercises[0]["name"], "Pushups")
        self.assertEqual(exercises[1]["name"], "Plank")


    
    def test_calculate_bmi_result_healthy_weight(self):
        bmi, category, quote = calculate_bmi_result(180, 75)

        self.assertEqual(bmi, 23.1)
        self.assertEqual(category, "Healthy weight")
        self.assertEqual(
            quote,
            "Great shape! Keep maintaining your healthy lifestyle!"
        )

    def test_calculate_bmi_result_invalid_height(self):
        with self.assertRaises(ValueError):
            calculate_bmi_result(0, 75)

    def test_get_bmi_fitness_points_healthy_weight(self):
        points = get_bmi_fitness_points("Healthy weight")

        self.assertEqual(len(points), 5)
        self.assertIn("Maintain your current habits", points[0])