from flask import Flask, render_template, request
import google.generativeai as genai
import os
from markupsafe import Markup

# Установка API ключа для Google Gemini
os.environ["GOOGLE_API_KEY"] = "AIzaSyCrxXOE4h3nfOHGatKQYCxVH089hwmlDZo"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
def format_course_content(raw_content):
    # Очистка ненужных символов
    formatted_content = raw_content.replace("**", "").replace("*", "")

    # Преобразование специальных ключевых слов в HTML-теги
    formatted_content = formatted_content.replace("##", "<h3>").replace(":", "</h3>")
    formatted_content = formatted_content.replace("*", "<li>").replace(".", "</li>")

    # Обернем в теги, чтобы было красиво и удобно читать
    formatted_content = f"<div class='course-content'>{formatted_content}</div>"

    return Markup(formatted_content)

# Функция для генерации курса
def generate_course_content(course_description):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(course_description)

        if response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            return "Ошибка: Ответ не был получен"
    except Exception as e:
        return f"Ошибка: Не удалось подключиться к сервису. Детали: {str(e)}"

# Проверка на ключевые слова, связанные с курсом
def is_course_related(text):
    keywords = ["курс", "учебный", "лекция", "обучение", "тема"]
    return any(keyword in text.lower() for keyword in keywords)

@app.route('/')
def index():
    return render_template('index.html')

# Маршрут для генерации контента
@app.route('/generate-course', methods=['POST'])
def generate_course():
    course_title = request.form['course_title']  # Получаем название курса
    course_description = request.form['course_description']
    content_type = request.form.get('contentType', 'course')

    if content_type == "course" and not is_course_related(course_description):
        course_description = f"Создай учебный курс по теме: {course_description}"
    elif content_type == "lecture":
        course_description = f"Создай лекцию по теме: {course_description}"
    elif content_type == "answer":
        course_description = f"Ответь на вопрос: {course_description}"

    # Генерация курса
    raw_content = generate_course_content(course_description)
    # Форматирование
    course_content = format_course_content(raw_content)
    return render_template("result.html", course_title=course_title, course_content=course_content)

if __name__ == '__main__':
    app.run(debug=True)
