from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)
app.secret_key = 'batman_secret_access_key'

# Настройка базы данных SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'gotham_intel.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- МОДЕЛЬ ДАННЫХ ---
class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codename = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    access_level = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Agent {self.codename}>'


# Создание базы данных внутри контекста приложения
with app.app_context():
    db.create_all()


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def generate_codename():
    adjectives = ["Shadow", "Ghost", "Dark", "Silver", "Iron", "Silent", "Night"]
    nouns = ["Fox", "Bat", "Hawk", "Wolf", "Spider", "Falcon", "Knight"]
    return f"{random.choice(adjectives)} {random.choice(nouns)}"


# --- МАРШРУТЫ ---

# 1. Список агентов + Поиск + Фильтр
@app.route('/')
def index():
    search_query = request.args.get('search')
    level_filter = request.args.get('level')

    # Базовый запрос
    query = Agent.query

    if search_query:
        query = query.filter(Agent.codename.contains(search_query))

    if level_filter:
        query = query.filter(Agent.access_level == level_filter)

    agents = query.all()
    return render_template('index.html', agents=agents)


# 2. Добавление агента
@app.route('/add', methods=['GET', 'POST'])
def add_agent():
    if request.method == 'POST':
        name = request.form.get('codename') or generate_codename()
        new_agent = Agent(
            codename=name,
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            access_level=request.form.get('access_level')
        )
        db.session.add(new_agent)
        db.session.commit()
        flash(f"Агент {name} добавлен в систему.")
        return redirect(url_for('index'))

    return render_template('add_agent.html', random_name=generate_codename())


# 3. Просмотр досье
@app.route('/agent/<int:id>')
def view_agent(id):
    agent = Agent.query.get_or_404(id)
    return render_template('view_agent.html', agent=agent)


# 4. Редактирование
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_agent(id):
    agent = Agent.query.get_or_404(id)
    if request.method == 'POST':
        agent.codename = request.form.get('codename')
        agent.phone = request.form.get('phone')
        agent.email = request.form.get('email')
        agent.access_level = request.form.get('access_level')
        db.session.commit()
        flash("Досье успешно обновлено.")
        return redirect(url_for('view_agent', id=agent.id))

    return render_template('edit_agent.html', agent=agent)


# 5. Удаление
@app.route('/delete/<int:id>')
def delete_agent(id):
    agent = Agent.query.get_or_404(id)
    db.session.delete(agent)
    db.session.commit()
    flash("Досье уничтожено.")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)