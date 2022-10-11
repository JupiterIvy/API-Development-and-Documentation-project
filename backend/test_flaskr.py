import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from flaskr import create_app
from models import setup_db, Question, Category

load_dotenv()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        self.database_name = "trivia_test"
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_HOST = os.getenv("DB_HOST")
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(
            self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.database_name
        )
        setup_db(self.app, self.database_path)

        self.new_question = {'id': 17, 'question': 'La Giaconda is better known as what?', 'answer': 'Mona Lisa', 'category': 2, 'difficulty': 3}
        self.quiz = { 'prev_question': [], 'quiz_category':{'type':'Art', 'id': 2}}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_404_wrong_categories(self):
        res = self.client().get("/categories/6")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_pagination(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["categories"])
        self.assertTrue(data["current_category"])

    def test_pagination_error(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'resource not found')

    def test_questions_by_categories(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["current_category"])

    def test_error_in_questions_by_categories(self):
        res = self.client().get("/categories/1000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'unprocessable')
    
    def test_question_search(self):
        res = self.client().post("/questions/search", json={"searchTerm":"Which"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_invalid_question_search(self):
        res = self.client().post("/questions/search/1", json={"search_question":"actor"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'resource not found')

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(len(data["questions"]))

    def test_error_in_create_new_question(self):
        res = self.client().post("/questions/2", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'method not allowed')

    def test_delete_question(self):
        res = self.client().delete("/questions/4")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 4)

    def test_error_in_delete_question(self):
        res = self.client().delete("questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'unprocessable')

    def test_quiz(self):
        res = self.client().post("/quizzes", json=self.quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_error_in_quiz(self):
        res = self.client().post("/quizzes/1", json={"quiz_category":{'id':10000}, "previous_questions":[]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data["message"], 'resource not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()