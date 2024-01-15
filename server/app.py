from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([message.serialize() for message in messages]) if messages else jsonify([])

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    new_message = Message(body=data['body'], username=data['username'])
    db.session.add(new_message)
    db.session.commit()
    response = jsonify(new_message.serialize())
    response.headers['Content-Type'] = 'application/json'  # Explicitly set content type
    return response, 201

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404
    
    data = request.get_json()
    message.body = data.get('body', message.body)
    db.session.commit()
    response = jsonify(message.serialize())
    response.headers['Content-Type'] = 'application/json' 
    return response

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404
    
    db.session.delete(message)
    db.session.commit()
    
    assert not Message.query.get(id)
    
    return jsonify({"message": "Message deleted successfully"}), 200, {'Content-Type': 'application/json'}
if __name__ == '__main__':
    app.run(port=5555)
