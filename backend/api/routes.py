from flask import Blueprint, request, jsonify, Response, stream_with_context
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import shutil
from ..config import Config
from ..services.claude_client import ClaudeClient
from ..services.file_processor import FileProcessor

api_bp = Blueprint('api', __name__)

claude_client = None


def init_claude_client():
    global claude_client
    if claude_client is None:
        claude_client = ClaudeClient(
            user_files_dir=Config.USER_FILES_DIR,
            responses_dir=Config.RESPONSES_DIR
        )
    return claude_client


@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "!API!"
    })


@api_bp.route('/upload', methods=['POST'])
def upload_files():
    """
    Загрузка файлов или папки
    """
    try:
        if 'files[]' not in request.files:
            return jsonify({"error": "Файлы не найдены"}), 400

        files = request.files.getlist('files[]')
        uploaded_files = []

        for file in files:
            if file.filename == '':
                continue

            relative_path = request.form.get(f'path_{file.filename}', '')

            filename = secure_filename(file.filename)
            file_ext = Path(filename).suffix.lower()

            if file_ext not in Config.ALLOWED_EXTENSIONS:
                return jsonify({
                    "error": f"Неподдерживаемый тип файла: {file_ext}. "
                            f"Разрешены: {', '.join(Config.ALLOWED_EXTENSIONS)}"
                }), 400

            if relative_path:
                file_path = Config.USER_FILES_DIR / relative_path / filename
            else:
                file_path = Config.USER_FILES_DIR / filename

            file_path.parent.mkdir(parents=True, exist_ok=True)

            file.save(str(file_path))

            uploaded_files.append({
                "name": filename,
                "path": str(file_path.relative_to(Config.USER_FILES_DIR)),
                "size": file_path.stat().st_size,
                "extension": file_ext
            })

        return jsonify({
            "message": f"Загружено файлов: {len(uploaded_files)}",
            "files": uploaded_files
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/files', methods=['GET'])
def list_files():
    """Получение списка загруженных файлов"""
    try:
        client = init_claude_client()
        files = client.get_available_files()
        return jsonify({
            "files": files,
            "total": len(files)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/files/<path:filepath>', methods=['DELETE'])
def delete_file(filepath):
    """Удаление файла"""
    try:
        file_path = Config.USER_FILES_DIR / filepath

        file_path.resolve().relative_to(Config.USER_FILES_DIR.resolve())

        if not file_path.exists():
            return jsonify({"error": "Файл не найден"}), 404

        if file_path.is_file():
            file_path.unlink()
        elif file_path.is_dir():
            shutil.rmtree(file_path)

        return jsonify({"message": "Файл успешно удален"})
    except ValueError:
        return jsonify({"error": "Недопустимый путь"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/files/clear', methods=['POST'])
def clear_all_files():
    """Удаление всех загруженных файлов"""
    try:
        for item in Config.USER_FILES_DIR.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        return jsonify({"message": "Все файлы удалены"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/query', methods=['POST'])
def process_query():
    """
    Обработка запроса пользователя (синхронная версия)
    Body: {"query": "string", "max_tokens": int (optional)}
    """
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({"error": "Запрос не указан"}), 400

        query = data['query']
        max_tokens = data.get('max_tokens', 8000)

        client = init_claude_client()
        result = client.process_query_sync(query, max_tokens)

        if result.get('success'):
            return jsonify({
                "response": result['text'],
                "usage": result['usage']
            })
        else:
            return jsonify({"error": result.get('error', 'Unknown error')}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@api_bp.route('/responses', methods=['GET'])
def list_responses():
    """Получение списка сгенерированных ответов"""
    try:
        client = init_claude_client()
        responses = client.get_response_files()
        return jsonify({
            "responses": responses,
            "total": len(responses)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/responses/<path:filepath>', methods=['GET'])
def get_response(filepath):
    """Получение содержимого сгенерированного ответа"""
    try:
        file_path = Config.RESPONSES_DIR / filepath

        file_path.resolve().relative_to(Config.RESPONSES_DIR.resolve())

        if not file_path.exists() or not file_path.is_file():
            return jsonify({"error": "Файл не найден"}), 404

        content = file_path.read_text(encoding='utf-8')
        return jsonify({
            "filename": file_path.name,
            "content": content
        })
    except ValueError:
        return jsonify({"error": "Недопустимый путь"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/responses/<path:filepath>', methods=['DELETE'])
def delete_response(filepath):
    """Удаление сгенерированного ответа"""
    try:
        file_path = Config.RESPONSES_DIR / filepath

        file_path.resolve().relative_to(Config.RESPONSES_DIR.resolve())

        if not file_path.exists():
            return jsonify({"error": "Файл не найден"}), 404

        file_path.unlink()
        return jsonify({"message": "Ответ удален"})
    except ValueError:
        return jsonify({"error": "Недопустимый путь"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
