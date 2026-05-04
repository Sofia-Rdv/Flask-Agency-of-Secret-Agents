from flask import render_template, request, redirect, url_for, flash, current_app as app
from app.models import Agent
from app import db
import random
import logging

logger = logging.getLogger("my_app")


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def generate_codename():
    adjectives = ["Shadow", "Ghost", "Dark", "Silver", "Iron", "Silent", "Night"]
    nouns = ["Fox", "Bat", "Hawk", "Wolf", "Spider", "Falcon", "Knight"]
    logger.info("Генерация кодового имени.")
    return f"{random.choice(adjectives)} {random.choice(nouns)}"


# --- МАРШРУТЫ ---

# 1. Список агентов + Поиск + Фильтр
@app.route('/')
def index():
    search_query = request.args.get('search')
    level_filter = request.args.get('level')

    if search_query or level_filter:
        logger.debug(f"Запрос фильтрации: поиск='{search_query}', уровень='{level_filter}'")

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
        try:
            new_agent = Agent(
                codename=name,
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                access_level=request.form.get('access_level')
            )
            db.session.add(new_agent)
            db.session.commit()

            logger.info(f"СИСТЕМА: Добавлен новый агент {name} (Уровень: {new_agent.access_level})")

            flash(f"Агент {name} добавлен в систему.")
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            logger.critical(f"ОШИБКА при добавлении агента: {str(e)}")
            flash("Критическая ошибка при сохранении данных.")

    return render_template('add_agent.html', random_name=generate_codename())


# 3. Просмотр досье
@app.route('/agent/<int:id>')
def view_agent(id):
    agent = Agent.query.get_or_404(id)
    logger.info(f"ДОСТУП: Просмотр досье ID {id} ({agent.codename})")
    return render_template('view_agent.html', agent=agent)


# 4. Редактирование
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_agent(id):
    agent = Agent.query.get_or_404(id)
    if request.method == 'POST':
        old_name = agent.codename
        try:
            agent.codename = request.form.get('codename')
            agent.phone = request.form.get('phone')
            agent.email = request.form.get('email')
            agent.access_level = request.form.get('access_level')
            db.session.commit()

            logger.info(f"ОБНОВЛЕНИЕ: Досье {old_name} (ID {id}) изменено.")

            flash("Досье успешно обновлено.")
            return redirect(url_for('view_agent', id=agent.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"ОШИБКА при обновлении досье ID {id}: {str(e)}")
            flash("Не удалось обновить данные.")

    return render_template('edit_agent.html', agent=agent)


# 5. Удаление
@app.route('/delete/<int:id>')
def delete_agent(id):
    agent = Agent.query.get_or_404(id)
    codename = agent.codename
    try:
        db.session.delete(agent)
        db.session.commit()

        logger.warning(f"УДАЛЕНИЕ: Агент {codename} (ID {id}) удален из системы!")

        flash("Досье уничтожено.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"ОШИБКА при удалении агента ID {id}: {str(e)}")
        flash("Ошибка при попытке удаления.")

    return redirect(url_for('index'))


