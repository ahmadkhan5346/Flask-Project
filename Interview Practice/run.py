import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)

app.config['SECRET_KEY'] = 'qgjjbvcxsdfghjnbvcmnbvcjhgfdnbvc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

class Employee(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80),nullable=False)
    email=db.Column(db.String(100),nullable=False)
    phone=db.Column(db.String(10),nullable=False)

class PersonalDeail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer(2), nullable=False)
    father_name = db.Column(db.String(50), nullable=False)
    mother_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    emp_id = db.Column('employee_id', db.Integer, db.ForeignKey('employee.id', ondelete='CASCADE'), nullable=False, unique=True)


@app.route('/create-database',methods=['GET'])
def createTable():
    with app.app_context():
        db.create_all()
    return jsonify({'message':'Table Created'})



@app.route('/emp',methods=['POST', 'PUT'])
def addEmp():
    data=request.get_json()
    if request.method == 'POST':
        emp=Employee.query.filter_by(email=data['email']).first()
        if emp:
            if emp.email==data['email']:
                return jsonify({'message':"Email Allready used"})
        user=Employee(name=data['name'],email=data['email'],phone=data['phone'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'message':"Emp Data Added"})
    else:
        for i in data:
            Employee.query.filter_by(email= i).update({'phone': data[i]})
            db.session.commit()
        return jsonify({'msg': 'emp data updated'})






if __name__=='__main__':
    app.run(debug=True)