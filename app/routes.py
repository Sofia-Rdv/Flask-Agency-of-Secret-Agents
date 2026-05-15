from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Agent
from app import db
import random
import logging

logger = logging.getLogger("my_app")

# 1. Создаем объект блюпринта
# 'main' - это имя, по которому мы будем обращаться к нему в url_for
main = Blueprint('main', __name__)


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def generate_codename():
    """
    Генерирует случайное кодовое имя для агента.
    Использует заранее заданные списки прилагательных и существительных.

    :return: str: Строка с кодовым именем.
    """
    adjectives = ["Shadow", "Ghost", "Dark", "Silver", "Iron", "Silent", "Night"]
    nouns = ["Fox", "Bat", "Hawk", "Wolf", "Spider", "Falcon", "Knight"]
    logger.info("Генерация кодового имени.")
    return f"{random.choice(adjectives)} {random.choice(nouns)}"


# --- МАРШРУТЫ ---

# 1. Список агентов + Поиск + Фильтр
@main.route('/')
def index():
    """
    Главная страница: список всех агентов в системе.

    Поддерживает фильтрацию через GET-запросы:
    - search: поиск по кодовому имени (частичное совпадение).
    - level: фильтрация по уровню доступа.

    :return: str: Рендер шаблона index.html со списком агентов.
    """
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
@main.route('/add', methods=['GET', 'POST'])
def add_agent():
    """
    Обработка вербовки нового агента.

    GET: Отображает форму добавления.
    POST: Сохраняет нового агента в базу данных. Если кодовое имя не введено,
          генерирует его автоматически.

    :return: str: Шаблон формы или перенаправление на главную при успехе.
    """
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
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            logger.critical(f"ОШИБКА при добавлении агента: {str(e)}")
            flash("Критическая ошибка при сохранении данных.")

    return render_template('add_agent.html', random_name=generate_codename())


# 3. Просмотр досье
@main.route('/agent/<int:id>')
def view_agent(id):
    """
     Просмотр детальной информации (досье) конкретного агента.

    :param id: int: Уникальный идентификатор агента в базе данных.
    :return: str: Шаблон view_agent.html или ошибка 404, если агент не найден.
    """
    agent = Agent.query.get_or_404(id)
    logger.info(f"ДОСТУП: Просмотр досье ID {id} ({agent.codename})")
    return render_template('view_agent.html', agent=agent)


# 4. Редактирование
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_agent(id):
    """
    Редактирование существующих данных агента.

    GET: Загружает текущие данные агента в форму.
    POST: Обновляет запись в базе данных.

    :param id: int: Идентификатор агента для редактирования.
    :return: str: Шаблон edit_agent.html или переход в досье при успехе.

    """
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
            return redirect(url_for('main.view_agent', id=agent.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"ОШИБКА при обновлении досье ID {id}: {str(e)}")
            flash("Не удалось обновить данные.")

    return render_template('edit_agent.html', agent=agent)


# 5. Удаление
@main.route('/delete/<int:id>')
def delete_agent(id):
    """
    Безвозвратное удаление агента из базы данных.

    :param id: int: Идентификатор агента для удаления.
    :return: Response: Перенаправление на главную страницу (index).
    """
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

    return redirect(url_for('main.index'))


@main.app_errorhandler(404)
def page_for_found(e):
    """
    Обработчик ошибки 404 (Страница не найдена).

    Логирует путь, по которому пытался перейти пользователь,
    и выводит страницу ошибки.

    :param e: Exception: Объект ошибки.
    :return: tuple: Шаблон ошибки и HTTP-статус 404.
    """
    logger.error(f"Ошибка 404: {request.method} {request.path} - Не найдено.")
    return render_template("error.html", title='404 - Потеряно',
                           message="Упс! Страница потерялась в переулках Готэма."), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    """
    Обработчик ошибки 500 (Внутренняя ошибка сервера).

    Логирует критическую ошибку с полной трассировкой стека (traceback)
    и выводит страницу ошибки.

    :param e: Exception: Объект ошибки.
    :return: tuple: Шаблон ошибки и HTTP-статус 500.
    """
    logger.critical(f"500: Ошибка сервера на пути {request.path} | Причина: {str(e)}", exc_info=True)
    return render_template("error.html", title="500 - Сбой системы",
                           message="Наш сервер приуныл. Альфред уже чинит его."), 500
