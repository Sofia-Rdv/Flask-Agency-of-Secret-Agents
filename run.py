from app import create_app
import logging

app = create_app()
logger = logging.getLogger("my_app")


if __name__ == '__main__':
    logger.info('Программа "Flask_Agents_Project" запущена.')
    app.run(debug=True)
