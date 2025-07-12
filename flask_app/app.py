from flask import Flask, request, jsonify, render_template_string
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

app = Flask(__name__)

load_dotenv('.env.deployment')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
print(f"{POSTGRES_DB} /t {POSTGRES_HOST} /t {POSTGRES_PORT} /t {POSTGRES_USER} /t {POSTGRES_PASSWORD}")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()


# HTML template for the frontend
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Task Manager</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .task { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .completed { background-color: #f0f8f0; }
        button { padding: 5px 10px; margin: 5px; cursor: pointer; }
        input, textarea { width: 100%; padding: 8px; margin: 5px 0; }
        .delete-btn { background-color: #ff4444; color: white; border: none; }
        .edit-btn { background-color: #4CAF50; color: white; border: none; }
        .toggle-btn { background-color: #2196F3; color: white; border: none; }
    </style>
</head>
<body>
    <h1>Task Manager</h1>
    
    <div id="add-task-form">
        <h2>Add New Task</h2>
        <input type="text" id="title" placeholder="Task title" required>
        <textarea id="description" placeholder="Task description"></textarea>
        <button onclick="addTask()">Add Task</button>
    </div>

    <div id="tasks-container">
        <h2>Tasks</h2>
        <div id="tasks-list"></div>
    </div>

    <script>
        // Load tasks on page load
        document.addEventListener('DOMContentLoaded', loadTasks);

        async function loadTasks() {
            try {
                const response = await fetch('/api/tasks');
                const tasks = await response.json();
                displayTasks(tasks);
            } catch (error) {
                console.error('Error loading tasks:', error);
            }
        }

        function displayTasks(tasks) {
            const container = document.getElementById('tasks-list');
            container.innerHTML = '';
            
            tasks.forEach(task => {
                const taskDiv = document.createElement('div');
                taskDiv.className = `task ${task.completed ? 'completed' : ''}`;
                taskDiv.innerHTML = `
                    <h3>${task.title}</h3>
                    <p>${task.description || 'No description'}</p>
                    <small>Created: ${new Date(task.created_at).toLocaleString()}</small>
                    <br>
                    <button class="toggle-btn" onclick="toggleTask(${task.id}, ${task.completed})">
                        ${task.completed ? 'Mark Incomplete' : 'Mark Complete'}
                    </button>
                    <button class="edit-btn" onclick="editTask(${task.id})">Edit</button>
                    <button class="delete-btn" onclick="deleteTask(${task.id})">Delete</button>
                `;
                container.appendChild(taskDiv);
            });
        }

        async function addTask() {
            const title = document.getElementById('title').value;
            const description = document.getElementById('description').value;
            
            if (!title.trim()) {
                alert('Title is required');
                return;
            }

            try {
                const response = await fetch('/api/tasks', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: title,
                        description: description
                    })
                });

                if (response.ok) {
                    document.getElementById('title').value = '';
                    document.getElementById('description').value = '';
                    loadTasks();
                } else {
                    alert('Error adding task');
                }
            } catch (error) {
                console.error('Error adding task:', error);
                alert('Error adding task');
            }
        }

        async function toggleTask(id, currentStatus) {
            try {
                const response = await fetch(`/api/tasks/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        completed: !currentStatus
                    })
                });

                if (response.ok) {
                    loadTasks();
                } else {
                    alert('Error updating task');
                }
            } catch (error) {
                console.error('Error updating task:', error);
                alert('Error updating task');
            }
        }

        async function editTask(id) {
            const newTitle = prompt('Enter new title:');
            const newDescription = prompt('Enter new description:');
            
            if (newTitle === null) return; // User cancelled

            try {
                const response = await fetch(`/api/tasks/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: newTitle,
                        description: newDescription
                    })
                });

                if (response.ok) {
                    loadTasks();
                } else {
                    alert('Error updating task');
                }
            } catch (error) {
                console.error('Error updating task:', error);
                alert('Error updating task');
            }
        }

        async function deleteTask(id) {
            if (!confirm('Are you sure you want to delete this task?')) return;

            try {
                const response = await fetch(`/api/tasks/${id}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    loadTasks();
                } else {
                    alert('Error deleting task');
                }
            } catch (error) {
                console.error('Error deleting task:', error);
                alert('Error deleting task');
            }
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# CREATE - Add a new task


@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO tasks (title, description) VALUES (%s, %s) RETURNING *',
            (title, description)
        )
        task = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        return jsonify(dict(task)), 201
    except Exception as e:
        logger.exception("Error in create_task")
        return jsonify({'error': str(e)}), 500

# READ - Get all tasks


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM tasks ORDER BY created_at DESC')
        tasks = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify([dict(task) for task in tasks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# READ - Get a specific task


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM tasks WHERE id = %s', (task_id,))
        task = cur.fetchone()
        cur.close()
        conn.close()

        if task:
            return jsonify(dict(task))
        else:
            return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# UPDATE - Update a task


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()

    # Build dynamic update query
    updates = []
    values = []

    if 'title' in data:
        updates.append('title = %s')
        values.append(data['title'])

    if 'description' in data:
        updates.append('description = %s')
        values.append(data['description'])

    if 'completed' in data:
        updates.append('completed = %s')
        values.append(data['completed'])

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400

    updates.append('updated_at = CURRENT_TIMESTAMP')
    values.append(task_id)

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = f'UPDATE tasks SET {", ".join(updates)} WHERE id = %s RETURNING *'
        cur.execute(query, values)
        task = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if task:
            return jsonify(dict(task))
        else:
            return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DELETE - Delete a task


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM tasks WHERE id = %s RETURNING *', (task_id,))
        task = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if task:
            return jsonify({'message': 'Task deleted successfully'})
        else:
            return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


init_db()

if __name__ == '__main__':
    app.run(debug=True)
