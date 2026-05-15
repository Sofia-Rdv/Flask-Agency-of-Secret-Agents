import pytest
from app import create_app, db
from app.models import Agent

@pytest.fixture
def client():
    """Создает экземпляр приложения для каждого теста."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'DEBUG': False,  # Отключаем дебаг, чтобы видеть кастомные ошибки
        'PRESERVE_CONTEXT_ON_EXCEPTION': False
    })

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture
def sample_agent_id(client):
    """Создает тестового агента и возвращает его ID."""
    agent = Agent(
        codename="Silver Bat",
        phone="555-0101",
        email="silver@wayne.com",
        access_level="Секретно"
    )
    db.session.add(agent)
    db.session.commit()
    return agent.id

# --- ТЕСТЫ ---

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "BAT-INTEL" in response.get_data(as_text=True)

def test_add_agent_post(client):
    data = {
        'codename': 'Night Wolf',
        'phone': '999-999',
        'email': 'wolf@bat.com',
        'access_level': 'Совершенно секретно'
    }
    # Используем follow_redirects=True, чтобы проверить результат на главной
    response = client.post('/add', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert "Night Wolf" in response.get_data(as_text=True)

    # Проверяем БД напрямую
    agent = Agent.query.filter_by(codename='Night Wolf').first()
    assert agent is not None

def test_generate_codename_auto(client):
    data = {
        'codename': '',
        'phone': '000',
        'email': 'auto@bat.com',
        'access_level': 'Секретно'
    }
    client.post('/add', data=data)
    agent = Agent.query.filter_by(email='auto@bat.com').first()
    assert agent.codename != ""

def test_view_agent(client, sample_agent_id):
    # Исправлено: убраны лишние скобки в f-строке
    response = client.get(f'/agent/{sample_agent_id}')
    assert response.status_code == 200
    assert "Silver Bat" in response.get_data(as_text=True)

def test_edit_agent(client, sample_agent_id):
    data = {
        'codename': 'Updated Name',
        'phone': '111',
        'email': 'test@bat.com',
        'access_level': 'Только для Бэтмена'
    }
    response = client.post(f'/edit/{sample_agent_id}', data=data, follow_redirects=True)
    assert response.status_code == 200

    agent = Agent.query.get(sample_agent_id)
    assert agent.codename == 'Updated Name'

def test_delete_agent(client, sample_agent_id):
    response = client.get(f'/delete/{sample_agent_id}', follow_redirects=True)
    assert response.status_code == 200
    assert "Досье уничтожено" in response.get_data(as_text=True)
    assert Agent.query.get(sample_agent_id) is None

def test_404_error(client):
    """Проверка кастомной ошибки 404."""
    response = client.get('/agent/9999')
    assert response.status_code == 404
    # Если тест всё еще падает здесь, значит Flask не подхватывает твой @app.errorhandler(404)
    # Попробуй проверить, есть ли в выводе фраза "Страница потерялась"
    assert "Страница потерялась" in response.get_data(as_text=True)