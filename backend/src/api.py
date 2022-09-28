from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/get-token')
def get_token():
    return 'Gotten za token!'

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    all_drinks = [drink.short() for drink in drinks]
    return jsonify({'Sucess':True, 'drinks':all_drinks})

'''
DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    
    drinks = Drink.query.all()
    all_drinks = [drink.long() for drink in drinks]    
    return jsonify({'Sucess':True, 'drinks':all_drinks})


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):    
    body = request.get_json() #Get the json data
    
    try:
        

        title =  body.get('title', None) # get the title field
        recipe = body.get('recipe', None) # get the recipe
        str_recipe = f'[{json.dumps(recipe)}]' # convert to str for lazy json blob

        drink = Drink(title=title, recipe=str_recipe)
        drink.insert()

    except:                
        abort(400)
    
    return jsonify({
        "success": True, 
        "drinks": drink.long()   
    })  

'''
@TODO 

implement endpoint
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
def patch_drink(payload, drink_id):
    
    body = request.get_json() #Get the json data

    

    exists = Drink.query.filter_by(id=drink_id).first() is not None # Check the database if the row exists
    
    if exists:
        try:
            title =  body.get('title', None) # get the title field
            recipe = body.get('recipe', None) # get the recipe
            str_recipe = f'[{json.dumps(recipe)}]' # convert to str for lazy json blob

            drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
            drink.title = title
            drink.recipe = str_recipe
            drink.update()

            return jsonify({
                "success": True, 
                "drinks": [drink.long()]
                })
        except:
            abort(400)
    
    else:
        abort(404)

'''
@DONE implement endpoint
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
def method_name(payload, drink_id):
    exists = Drink.query.filter_by(id=drink_id).first() is not None # Check the database if the row exists
    
    if exists:
        try:
            drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
            drink.delete()

            return jsonify({
                "success": True, 
                "delete": drink_id
                })
        except:
            abort(400)
    
    else:
        abort(404)

# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
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
def res_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@app.errorhandler(401)
def not_authorize(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Not Authorize"
    }), 401

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

