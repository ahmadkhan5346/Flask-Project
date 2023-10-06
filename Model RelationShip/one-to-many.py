from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    profile = db.relationship('Profile', uselist=False, back_populates='user')
    posts = db.relationship('Post', backref='author', lazy=True)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', uselist=False, back_populates='profile')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

with app.app_context():
    db.create_all()

@app.route('/post-add')
def addPost():
    # user = db.session.query(User).get(1)
    user = User.query.get(1)
    posts = [
        Post(title='post title1', description='post description1', author=user),
        Post(title='post title2', description='post description2', author=user),
        Post(title='post title3', description='post description3', author=user)
    ]
    # post.author = user
    for post in posts:
        db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'post added successfully'})

@app.route('/posts')
def getPosts():
    posts = Post.query.all()
    post_list = []
    for post in posts:
        post_data = {
            'id':post.id,
            'title':post.title,
            'description': post.description,
            'author':post.author.name
        }
        post_list.append(post_data)
    return jsonify(post_list)



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
            'bio': user.profile.bio,
            'posts':[]
        }

        for post in user.posts:
            post_data = {
                'title':post.title,
                'description':post.description,
            }

            user_data['posts'].append(post_data)

        user_list.append(user_data)
    return jsonify(user_list)

@app.route('/profiles')
def getProfile():
    profiles = Profile.query.all()
    profile_list = []
    for profile in profiles:
        profile_data = {
            'id':profile.id,
            'bio':profile.bio,
            'user_name': profile.user.name
        }
        profile_list.append(profile_data)
    return jsonify(profile_data)


@app.route('/')
def index():
    user = User.query.all()
    print('userrrr:',user[0].posts[0].__dict__)
    return jsonify({'message': 'Home page'})



if __name__ == '__main__':
    app.run(debug=True)





#     [
#   {
#     "bio": "Test user profile",
#     "id": 1,
#     "name": "Test user",
#     "posts": [
#       {
#         "description": "post description1",
#         "title": "post title1"
#       },
#       {
#         "description": "post description2",
#         "title": "post title2"
#       },
#       {
#         "description": "post description3",
#         "title": "post title3"
#       }
#     ]
#   }
# ]