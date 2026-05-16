from unittest import TestCase

from app import create_app, db
from config import TestingConfig
from app.controllers import calculate_bmi_result, get_bmi_fitness_points

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
        self.app_context.pop()
        return super().tearDown()
    
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