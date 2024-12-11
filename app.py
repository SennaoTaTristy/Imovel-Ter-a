from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from bson import ObjectId
from flask_mail import Mail, Message
import ssl

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuração do MongoDB
mongo_uri = "mongodb+srv://Carlos:Carlos3040@aula.h7pwx.mongodb.net/?retryWrites=true&w=majority&appName=Aula"
client = MongoClient(mongo_uri, tlsAllowInvalidCertificates=True)
db = client['task_manager']

# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'codigopythonflask@gmail.com'
app.config['MAIL_PASSWORD'] = 'ynnj cyxl ruyu lbou'
app.config['MAIL_DEFAULT_SENDER'] = 'codigopythonflask@gmail.com'

mail = Mail(app)

# Rota principal
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('tasks'))
    return redirect(url_for('login'))

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.users.find_one({'username': username, 'password': password})

        if user:
            if not user.get('is_verified', False):
                return 'Seu e-mail ainda não foi confirmado. Verifique sua caixa de entrada.'
            
            session['user_id'] = str(user['_id'])
            return redirect(url_for('tasks'))
        return 'Usuário ou senha inválidos.'
    return render_template('login.html')

# Rota de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Verifica duplicidade
        if db.users.find_one({'email': email}):
            return 'E-mail já registrado.'

        user_id = db.users.insert_one({
            'username': username,
            'email': email,
            'password': password,
            'is_verified': False
        }).inserted_id

        # Envia e-mail de validação
        token = str(user_id)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        msg = Message(
            subject='Confirmação de Cadastro',
            recipients=[email],
            html=f"""
            <h1>Bem-vindo, {username}!</h1>
            <p>Por favor, para continuar clique no botão abaixo:</p>
            <a href="{confirm_url}">Validar E-mail</a>
            <p>Atenciosamente: Equipe Tabsks</p>
            """
        )
        mail.send(msg)
        return 'Registro efetuado com sucesso! Verifique seu e-mail para confirmar o cadastro.'
    return render_template('register.html')

# Rota de confirmação de e-mail
@app.route('/confirm_email/<token>')
def confirm_email(token):
    user = db.users.find_one({'_id': ObjectId(token)})

    if not user:
        return 'Token inválido.'
    
    db.users.update_one({'_id': ObjectId(token)}, {'$set': {'is_verified': True}})
    return 'E-mail confirmado com sucesso!'

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Rota de tarefas
@app.route('/tasks')
def tasks():
    if 'user_id' in session:
        user_tasks = list(db.tasks.find({'user_id': session['user_id']}))
        for task in user_tasks:
            task['_id'] = str(task['_id'])
        return render_template('tasks.html', tasks=user_tasks)
    return redirect(url_for('login'))

# Rota para comentários
@app.route('/task_comments/<task_id>', methods=['GET'])
def task_comments(task_id):
    task = db.tasks.find_one({'_id': ObjectId(task_id)})
    if task:
        task['_id'] = str(task['_id'])
    return render_template('task_comments.html', task=task)

# Novo endpoint para adicionar comentário
@app.route('/add_comment/<task_id>', methods=['POST'])
def add_comment(task_id):
    comment = request.form.get('comment')  # Obtém o comentário enviado pelo formulário
    if comment:
        db.tasks.update_one(
            {'_id': ObjectId(task_id)},
            {'$push': {'comments': comment}}
        )
    return redirect(url_for('task_comments', task_id=task_id))

# Rota para alterar status da tarefa
@app.route('/update_task_status/<task_id>/<status>', methods=['POST'])
def update_task_status(task_id, status):
    if status not in ['Pendente', 'Não Concluído', 'Concluído']:
        return redirect(url_for('tasks'))
    db.tasks.update_one({'_id': ObjectId(task_id)}, {'$set': {'status': status}})
    return redirect(url_for('tasks'))

# Rota para adicionar tarefa
@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task_name = request.form['task_name']
        description = request.form['description']
        user_id = session['user_id']
        db.tasks.insert_one({
            'task_name': task_name,
            'description': description,
            'status': 'Pendente',
            'user_id': user_id,
            'comments': []
        })
        return redirect(url_for('tasks'))
    return render_template('add_task.html')

if __name__ == '__main__':
    app.run(debug=True)
