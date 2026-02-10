import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union, List, Dict, Any
import PyPDF2
import pandas as pd


class FileProcessor:
    """Класс для обработки различных типов файлов"""

    @staticmethod
    def read_json(file_path: Path) -> str:
        """Читает JSON файл и возвращает форматированный текст"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"Ошибка чтения JSON файла: {str(e)}")

    @staticmethod
    def read_txt(file_path: Path) -> str:
        """Читает текстовый файл"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Ошибка чтения текстового файла: {str(e)}")

    @staticmethod
    def read_xml(file_path: Path) -> str:
        """Читает XML файл и возвращает форматированный текст"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            def element_to_dict(element):
                result = {element.tag: {}}
                if element.attrib:
                    result[element.tag]['@attributes'] = element.attrib
                if element.text and element.text.strip():
                    if len(element) == 0:
                        return {element.tag: element.text.strip()}
                    result[element.tag]['#text'] = element.text.strip()

                children = {}
                for child in element:
                    child_data = element_to_dict(child)
                    child_tag = list(child_data.keys())[0]
                    if child_tag in children:
                        if not isinstance(children[child_tag], list):
                            children[child_tag] = [children[child_tag]]
                        children[child_tag].append(child_data[child_tag])
                    else:
                        children[child_tag] = child_data[child_tag]

                if children:
                    result[element.tag].update(children)

                return result

            data = element_to_dict(root)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"Ошибка чтения XML файла: {str(e)}")

    @staticmethod
    def read_pdf(file_path: Path) -> str:
        """Читает PDF файл и извлекает текст"""
        try:
            text_content = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(f"--- Страница {page_num + 1} ---\n{text}")

            return "\n\n".join(text_content)
        except Exception as e:
            raise ValueError(f"Ошибка чтения PDF файла: {str(e)}")

    @staticmethod
    def read_csv(file_path: Path) -> str:
        """Читает CSV файл и возвращает форматированный текст"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')

            data = df.to_dict(orient='records')

            result = {
                "metadata": {
                    "rows": len(df),
                    "columns": list(df.columns),
                    "shape": df.shape
                },
                "data": data[:1000]  # Ограничение 1000
            }

            if len(df) > 1000:
                result["note"] = f"Показаны первые 1000 строк из {len(df)}"

            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"Ошибка чтения CSV файла: {str(e)}")

    @staticmethod
    def read_excel(file_path: Path) -> str:
        """Читает Excel файл и возвращает форматированный текст"""
        try:
            excel_file = pd.ExcelFile(file_path)
            result = {
                "metadata": {
                    "sheets": excel_file.sheet_names,
                    "total_sheets": len(excel_file.sheet_names)
                },
                "data": {}
            }

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheet_data = {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "rows": df.to_dict(orient='records')[:1000]  # Ограничение 1000
                }

                if len(df) > 1000:
                    sheet_data["note"] = f"Показаны первые 1000 строк из {len(df)}"

                result["data"][sheet_name] = sheet_data

            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"Ошибка чтения Excel файла: {str(e)}")

    @staticmethod
    def process_file(file_path: Path) -> str:
        """
        Определяет тип файла и обрабатывает его соответствующим образом

        Args:
            file_path: Путь к файлу

        Returns:
            Текстовое представление содержимого файла
        """
        suffix = file_path.suffix.lower()

        processors = {
            '.json': FileProcessor.read_json,
            '.txt': FileProcessor.read_txt,
            '.xml': FileProcessor.read_xml,
            '.pdf': FileProcessor.read_pdf,
            '.csv': FileProcessor.read_csv,
            '.xlsx': FileProcessor.read_excel,
            '.xls': FileProcessor.read_excel,
        }

        processor = processors.get(suffix)
        if not processor:
            raise ValueError(f"Неподдерживаемый тип файла: {suffix}")

        return processor(file_path)

    @staticmethod
    def get_file_info(file_path: Path) -> Dict[str, Any]:
        """Получает информацию о файле"""
        stat = file_path.stat()
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "extension": file_path.suffix,
            "created": stat.st_ctime,
            "modified": stat.st_mtime
        }
