import os
from flask import Flask, request, abort, jsonify, current_app, g
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
    

def pagination(request, index):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [i.format() for i in index]
    formatted_questions = questions[start:end]
    
    return formatted_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.app_context().push()
    setup_db(app)

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Acces-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization,true')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_cat = { i.id: i.type for i in categories } 

        if len(formatted_cat) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories':formatted_cat,
            })
    
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        
        index = Question.query.order_by(Question.id).all()
        formatted_questions = pagination(request, index)

        categories = Category.query.order_by(Category.id).all()
        formatted_cat = { i.id: i.type for i in categories } 
        
        for k in formatted_questions:
            current_category = k['category']

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions':formatted_questions,
            'categories': formatted_cat,
            'total_questions':len(index),
            'current_category': current_category,
            })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(400)

            question.delete()
            index = Question.query.order_by(Question.id).all() 
            current_questions = pagination(request, index)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions':current_questions,
                })
        except:
            abort(422)
        
        
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_questions():
        
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        search = body.get("search", None)

        try:
            if search:
                index = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                    .all()
                ) 

                current_questions = pagination(request, index)

                return jsonify({
                'success': True,
                'questions':current_questions,
                'total_questions':len(index),
                })

            else:
                question = Question(
                    question = new_question, 
                    answer = new_answer, 
                    category = new_category,
                    difficulty = new_difficulty
                    )
                question.insert()

                index = Question.query.order_by(Question.id).all() 
                current_questions = pagination(request, index)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions':current_questions,
                'total_questions':len(index),
                })

        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def get_questions_by_search():

        body = request.get_json()

        search_question = body.get('searchTerm')
        index = Question.query.filter(Question.question.ilike('%'+search_question+'%')).all()
        total_questions = len(index)
        
        if index:
            current_questions = pagination(request, index)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': total_questions,
            })
        else:
            abort(404)
    
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:question_category>/questions')
    def get_questions_by_cat(question_category):
        categories = Category.query.filter(
            Category.id == question_category
        ).one_or_none()

        if categories == 0:
            abort(404)

        try:
            question = Question.query.filter(Question.category == question_category).all()
            formatted_questions = [i.format() for i in question]
            for k in formatted_questions:
                current_category = k['category']

            return jsonify({
                        'success': True,
                        'questions':formatted_questions,
                        'current_category': current_category,
                        })
        except Exception as e:
            print(e)
            abort(422)
            
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        body = request.get_json()

        index = []
        prev_question = body.get('previous_questions',[])
        quiz_category = body.get('quiz_category')
        print(quiz_category)
        try:
            if quiz_category:
                category_id = int(quiz_category['id'])
                if category_id == 0:
                    question = Question.query.all()
                else:
                    question = Question.query.filter_by( category = quiz_category['id']).all()
            else:
                abort(400)
            print(category_id)
            for i in question:
                if i.id not in prev_question:
                    index.append(i)
            
            formatted_index = [i.format() for i in question]
            #print(formatted_index)
            if len(index) != 0:
                random_question = random.choice(formatted_index)
                print(random_question)
                return jsonify({
                    'success':True,
                    'questions': random_question,
                })
            else:
                return jsonify({
                    'success':False,
                    'questions': []
                })

        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(500)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 500, "message": "server error"}),
            500,
        )
   
    return app

