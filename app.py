from flask import Flask, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

mongo_uri = 'mongodb+srv://Carlos:Carlos3040@tabsks.h7pwx.mongodb.net/?retryWrites=true&w=majority&appName=tabsks'
client = MongoClient(mongo_uri)
db = client['task_manager_db'] 
tasks_collection = db['tasks']  

@app.route('/')
def index():
    tasks = list(tasks_collection.find())
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    notes = request.form.get('notes')
    new_task = {
        'title': title,
        'notes': notes,
        'progress': 0,
        'completed': False
    }
    tasks_collection.insert_one(new_task)
    return redirect(url_for('index'))

@app.route('/update/<task_id>', methods=['POST'])
def update_task(task_id):
    task = tasks_collection.find_one({'_id': ObjectId(task_id)})
    if task:
        progress = int(request.form.get('progress'))
        completed = request.form.get('completed') == 'on'
        tasks_collection.update_one(
            {'_id': ObjectId(task_id)},
            {'$set': {'progress': progress, 'completed': completed}}
        )
    return redirect(url_for('index'))

@app.route('/edit/<task_id>')
def edit_task(task_id):
    task = tasks_collection.find_one({'_id': ObjectId(task_id)})
    return render_template('edit_task.html', task=task)

if __name__ == '__main__':
    app.run(debug=True)
