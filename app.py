# backend/app.py
import os
import random
import string
from flask import Flask, request, jsonify, send_from_directory
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/todo"
mongo = PyMongo(app)

# Generate a random ID for tasks
def generate_task_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# API endpoint to create a new task
@app.route("/tasks", methods=["POST"])
def create_task():
    task_data = request.get_json()
    task_data["id"] = generate_task_id()
    result = mongo.db.tasks.insert_one(task_data)
    task_data["_id"] = str(result.inserted_id)
    return jsonify(task_data), 201

# API endpoint to retrieve all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = list(mongo.db.tasks.find())
    for task in tasks:
        task["_id"] = str(task["_id"])
    return jsonify(tasks), 200

# API endpoint to retrieve a specific task by ID
@app.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    if task:
        task["_id"] = str(task["_id"])
        return jsonify(task), 200
    return jsonify({"error": "Task not found"}), 404

# API endpoint to update a specific task by ID
@app.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    task_data = request.get_json()
    result = mongo.db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": task_data})
    if result.modified_count > 0:
        return jsonify({"message": "Task updated successfully"}), 200
    return jsonify({"error": "Task not found"}), 404

# API endpoint to delete a specific task by ID
@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    result = mongo.db.tasks.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count > 0:
        return jsonify({"message": "Task deleted successfully"}), 204
    return jsonify({"error": "Task not found"}), 404

# Serve Swagger UI
@app.route("/")
def serve_swagger_ui():
    return send_from_directory("swagger", "index.html")

@app.route("/swagger/<path:path>")
def serve_swagger_assets(path):
    return send_from_directory("swagger", path)

if __name__ == "__main__":
    app.run(debug=True)
