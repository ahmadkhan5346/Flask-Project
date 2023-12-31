from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps


app = Flask(__name__)


app.config['SECRET_KEY'] = 'thisiskey'
# pip install flask_mysqldb
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/test_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(250))
    admin = db.Column(db.Boolean)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)

@app.route('/create-data-base', methods=['GET'])
def create_database():
    with app.app_context():
        db.create_all()
    return jsonify({'msg': 'Database created'})

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # if 'x-access-token' in request.headers:
        #     token = request.headers['x-access-token']

        token = request.cookies.get('CurrentUser')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({'Message': 'Cannot perfom that function!'})
    users = User.query.all()

    output = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)
    return jsonify({'users': output})

@app.route('/user/<public_id>', methods=['GET'])
def get_one_user(public_id):
    user = User.query.filter_by(public_id=public_id, ).first()

    if not user:
        return jsonify({'message': 'No user found!'})
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return jsonify({'user': user_data})

@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'})

@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user ,public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found'})
    user.admin = True
    db.session.commit()
    return jsonify({'message': 'The user has been promoted!'})

@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first( )
    if not user:
        return jsonify({'message': 'No user found'})
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user has been deleted!'})

@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW-Authentcate': 'Basic realm="Login required!"'})
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('could not verify', 401, {'WWW-Authentcate': 'Basic realm="User required!"'})
    
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=500)}, app.config['SECRET_KEY'])
        response = make_response(token)
        response.set_cookie(
            "CurrentUser", token, secure=app.config.get("SECURE_COOKIE")
        )
        return response
        # return jsonify({'token': token})
    return make_response('could not verify', 401, {'WWW-Authentcate': 'Basic realm="Password required!"'})

@app.route('/todo', methods=['GET', 'POST'])
@token_required
def get_all_todos(current_user):
    if request.method == 'POST':
        data = request.get_json()

        new_todo = Todo(text=data['text'], complete=False, user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
        return jsonify({'Message': 'Todo created!'})
    

    if request.method == 'GET':
        todos = Todo.query.filter_by(user_id=current_user.id).all()

        output = []
        for todo in todos:
            todo_data = {}
            todo_data['id'] = todo.id
            todo_data['text'] = todo.text
            todo_data['complete'] = todo.complete
            output.append(todo_data)

        return jsonify({'Todo': output})


@app.route('/todo/<todo_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def get_one_todo(current_user, todo_id):
        if request.method == 'GET':
            todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
            if not todo:
                return jsonify({'Message': 'No todo found'})
            
            todo_data = {}
            todo_data['id'] = todo.id
            todo_data['text'] = todo.text
            todo_data['complete'] = todo.complete

            return jsonify(todo_data)
        
        if request.method == 'PUT':
            todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
            if not todo:
                return jsonify({'Message': 'No todo found'})
            
            todo.complete = True
            db.session.commit()
            return jsonify({'Message': 'Todo item has been completed!'})
        
        if request.method == 'DELETE':
            todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
            if not todo:
                return jsonify({'Message': 'Todo not found for delete'})
            db.session.delete(todo)
            db.session.commit()
            return jsonify({'Message': 'Todo item deleted'})




if __name__ == '__main__':
    app.run(debug=True)