import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    # print('Get Drinks!!!!!')
    drinks = Drink.query.order_by(Drink.id).all()
    # app.logger.info(drinks)
    if len(drinks) == 0:
        # No Drinks Found!
        abort(404)
    drinks_list = [drink.short() for drink in drinks]
    # print(drinks_list)
    return jsonify({
        'success': True,
        'drinks': drinks_list
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.order_by(Drink.id).all()
    # app.logger.info(drinks)
    if len(drinks) == 0:
        # No Drinks Found!
        abort(404)
    drinks_list = [drink.long() for drink in drinks]
    # print(drinks_list)
    return jsonify({
        'success': True,
        'drinks': drinks_list
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
    body = request.get_json()
    # print(body)
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)
    print(new_recipe)
    long_recipe = [{"color": r['color'], "name":r['name'], "parts": r['parts']} for r in new_recipe]

    try:
        drink = Drink(title=str(new_title), recipe=json.dumps(long_recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except:
        abort(422)



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, drink_id):
    body = request.get_json()
    # print(body)
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            # No Drinks found!
            abort(404)
        
        if new_title:
            drink.title = new_title
        if new_recipe:
            long_recipe = [{"color": r['color'], "name":r['name'], "parts": r['parts']} for r in new_recipe]
            drink.recipe = json.dumps(long_recipe)
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            # No Drinks found!
            abort(404)
        
        drink.delete()

        return jsonify({
            'success': True,
            'drinks': drink_id
        })

    except:
        abort(422)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "Unprocessable Request!"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not found!'
    }), 404
      
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request!'
    }), 400
    
@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method not allowed!'
    }), 405

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
#####################
Reference: Auth0 Blog
https://auth0.com/blog/using-python-flask-and-angular-to-build-modern-web-apps-part-2/
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response