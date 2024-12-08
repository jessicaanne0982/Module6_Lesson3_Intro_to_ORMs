from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+mysqlconnector://root:my_password@localhost/fitness_center_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class Meta:
        fields = ("id", "name", "age")

class WorkoutSchema(ma.Schema):
    session_id = fields.Integer(required=True)
    member_id = fields.Integer(required=True)
    session_date = fields.String(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)
    duration_minutes = fields.Integer(required=True)
    calories_burned = fields.Integer(required=True)

    class Meta:
        fields = ("session_id", "member_id", "session_date", "session_time", "activity", "duration_minutes", "calories_burned")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    workouts = db.relationship('WorkoutSession', backref = 'Member')

class WorkoutSession(db.Model):
    __tablename__ = 'WorkoutSessions'
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'))
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.String, nullable=False)
    activity = db.Column(db.String, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer, nullable=False)

# GET operation - retrieve all members
@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

# POST operation - add a new member
@app.route('/members', methods=['POST']) 
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_member = Member(name=member_data['name'], age=member_data['age'], id=member_data['id'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message':'New member successfully added'}), 201

# PUT operation - update a member
@app.route('/members/<int:id>', methods=["PUT"])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    member.name = member_data['name']
    member.age = member_data['age']
    member.id = member_data['id']

    db.session.commit()
    return jsonify({'message':'Member details successfully updated'})

# DELETE operation - remove a member
@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message':'The member has successfully been removed.'}), 200


# Route to retrieve all workout sessions for a specific member
@app.route('/workouts/by-name', methods=['GET'])
def query_workouts_by_member():
    name = request.args.get('name')
    member =  Member.query.filter_by(name=name).first()

    if member:
        workout_sessions = WorkoutSession.query.filter_by(member_id=member.id).all()

    if workout_sessions:
        return workout_schema.jsonify(workout_sessions, many=True)
    else:
        return jsonify({'message':'Member not found'}), 404

# Route to retrieve all workout sessions
@app.route('/workouts', methods=["GET"])
def get_workouts():
    workouts = WorkoutSession.query.all()
    return workouts_schema.jsonify(workouts)

# Route to "schedule" or add workout sessions
@app.route('/workouts', methods=["POST"])
def add_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_workout = WorkoutSession(session_id=workout_data['session_id'],
                         member_id=workout_data['member_id'], 
                         session_date=workout_data['session_date'], 
                         session_time=workout_data['session_time'],
                         activity = workout_data['activity'],
                         duration_minutes = workout_data['duration_minutes'],
                         calories_burned=workout_data['calories_burned']
                         )
    
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({'message':'New workout successfully scheduled'}), 201

# PUT operation - update a workout
@app.route('/workouts/<int:id>', methods=["PUT"])
def update_workout(id):
    workout = WorkoutSession.query.get_or_404(id)
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    workout.session_id = workout_data['session_id']
    workout.member_id = workout_data['member_id']
    workout.session_date = workout_data['session_date']
    workout.session_time = workout_data['session_time']
    workout.activity = workout_data['activity']
    workout.duration_minutes = workout_data['duration_minutes']
    workout.calories_burned = workout_data['calories_burned']
    
    db.session.commit()
    return jsonify({'message':'Workout details successfully updated'}), 200

# Initialize and create tables
with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True)