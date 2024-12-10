from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

app = Flask(__name__)

# Configuração do MongoDB
app.config["MONGO_URI"] = 'mongodb+srv://Carlos:Carlos3040@tabsks.h7pwx.mongodb.net/tabsks?retryWrites=true&w=majority'
app.secret_key = "supersecretkey"  # Adicione uma chave secreta para usar mensagens flash
mongo = PyMongo(app)

# Rota para a página principal que lista as tarefas
@app.route('/')
def index():
    tarefas = mongo.db.tarefas.find()  # Carregar as tarefas
    return render_template('index.html', tarefas=tarefas)

# Rota para adicionar tarefas
@app.route('/add_task', methods=['POST'])
def add_task():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        notas = request.form.get('notas')
        if titulo and notas:
            nova_tarefa = {
                'titulo': titulo,
                'notas': notas,
                'progresso': 0  # Inicialmente 0%
            }
            mongo.db.tarefas.insert_one(nova_tarefa)
        return redirect(url_for('index'))

# Rota para atualizar o progresso da tarefa
@app.route('/update_progress/<task_id>', methods=['POST'])
def update_progress(task_id):
    tarefa = mongo.db.tarefas.find_one({'_id': ObjectId(task_id)})
    novo_progresso = min(tarefa['progresso'] + 10, 100)  # Aumenta o progresso em 10%, até 100%
    mongo.db.tarefas.update_one({'_id': ObjectId(task_id)}, {'$set': {'progresso': novo_progresso}})
    return redirect(url_for('index'))

# Rota para marcar uma tarefa como completa
@app.route('/complete_task/<task_id>', methods=['POST'])
def complete_task(task_id):
    mongo.db.tarefas.update_one({'_id': ObjectId(task_id)}, {'$set': {'progresso': 100}})
    return redirect(url_for('index'))

# Rota para página de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = mongo.db.users.find_one({"username": username})

        if user and check_password_hash(user['password'], password):
            flash('Login efetuado com sucesso!')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos!')
            return redirect(url_for('login'))

    return render_template('login.html')

# Rota para página de Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Verifica se o usuário já existe
        existing_user = mongo.db.users.find_one({"username": username})
        
        if existing_user:
            flash('Usuário já existente!')
            return redirect(url_for('register'))

        # Cria o hash da senha
        hashed_password = generate_password_hash(password)

        # Insere o novo usuário no MongoDB
        mongo.db.users.insert_one({
            "username": username,
            "password": hashed_password,
            "email": email
        })

        flash('Registro efetuado com sucesso! Faça login.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Rota para página de Categorias
@app.route('/categories')
def categories():
    return render_template('categories.html')

if __name__ == '__main__':
    app.run(debug=True)
