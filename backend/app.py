from flask import Flask
from flask_cors import CORS
from config import Config
from api.routes import api_bp
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Создание и конфигурация Flask приложения"""

    app = Flask(__name__)

    # Включаем CORS для всех доменов (в production нужно ограничить)
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    Config.init_directories()
    logger.info("Директории инициализированы")
    logger.info(f"USER_FILES_DIR: {Config.USER_FILES_DIR}")
    logger.info(f"RESPONSES_DIR: {Config.RESPONSES_DIR}")

    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return {
            "message": "Claude Memory Tool API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/health",
                "upload": "/api/upload",
                "files": "/api/files",
                "query": "/api/query",
                "query_stream": "/api/query/stream",
                "responses": "/api/responses"
            }
        }

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Endpoint не найден"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return {"error": "Внутренняя ошибка сервера"}, 500

    return app


if __name__ == '__main__':
    app = create_app()
    logger.info(f"Запуск сервера на {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
