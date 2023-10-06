from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    profile = db.relationship('Profile', uselist=False, back_populates='user')


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', uselist=False, back_populates='profile')
    

with app.app_context():
    db.create_all()


@app.route('/user-add')
def addUser():
    user = User(name='Test user')
    profile = Profile(bio='Test user profile')

    user.profile = profile
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'user added successfully'})


@app.route('/users')
def getUser():
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'bio': user.profile.bio
        }
        user_list.append(user_data)
    return jsonify(user_list)


@app.route('/profiles')
def getProfile():
    profiles = Profile.query.all()
    print(profiles)
    profile_list = []
    for profile in profiles:
        profile_data = {
            'id':profile.id,
            'bio':profile.bio,
            'user_name': profile.user.name
        }
        profile_list.append(profile_data)
    return jsonify(profile_list)


@app.route('/')
def index():
    return jsonify({'message': 'Home page'})



if __name__ == '__main__':
    app.run(debug=True)