import telebot
import psycopg2
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

#pip install requests beautifulsoup4
#pip install unidecode



from telebot import types
from io import BytesIO
from telegram.ext import MessageHandler, CommandHandler, CallbackContext
from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging




# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="delo",
    user="postgres",
    port="5432",
    password="12345"
)
cursor = conn.cursor()






# Bot Token
TOKEN = "6828508465:AAE-JRWJL-mX1D0oMHRwuVU4BSYRByvK3k0"
bot = telebot.TeleBot(TOKEN)

# In-memory storage for registration and login steps
user_data = {}
# Start command


@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup()
    reg = types.KeyboardButton("/register")
    help = types.KeyboardButton('/help')
    login_button = types.KeyboardButton('/login') 
    markup.add(reg, help, login_button)
    bot.reply_to(message, "Привет! Зарегистрируйся или войди в систему, используя команды /register или /login.", reply_markup=markup)  # Fix: pass message, not message.chat.id

@bot.message_handler(commands=['register'])
def handle_register(message):
    msg = bot.send_message(message.chat.id, "Введите имя пользователя:")
    bot.register_next_step_handler(msg, process_username_step)

def process_username_step(message):
    try:
        username = message.text
        user_data[message.chat.id] = {'username': username}
        msg = bot.send_message(message.chat.id, "Введите пароль:")
        bot.register_next_step_handler(msg, process_password_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка')

def process_password_step(message):
    try:
        password = message.text
        user_data[message.chat.id]['password'] = password
        user_id = message.from_user.id

        # Save to DB
        cursor.execute("INSERT INTO main_user (username, password, user_id) VALUES (%s, %s, %s);", (user_data[message.chat.id]['username'], password, user_id))
        conn.commit()

        bot.send_message(message.chat.id, "Вы успешно зарегистрированы!")
        msg = bot.send_message(message.chat.id, "снова /login")
    except Exception as e:
        # Rollback the transaction on error
        conn.rollback()
        bot.send_message(message.chat.id, f'Ошибка при регистрации: {e}')
        print(f"Error during registration: {e}")



# Login command
@bot.message_handler(commands=['login'])
def handle_login(message):
    msg = bot.send_message(message.chat.id, "Введите имя пользователя:")
    bot.register_next_step_handler(msg, process_login_username_step)

def process_login_username_step(message):
    try:
        username = message.text
        user_data[message.chat.id] = {'username': username}
        msg = bot.send_message(message.chat.id, "Введите пароль:")
        bot.register_next_step_handler(msg, process_login_password_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка')
def process_login_password_step(message):
    try:
        password = message.text
        cursor.execute("SELECT * FROM main_user WHERE username = %s AND password = %s;", (user_data[message.chat.id]['username'], password))
        user = cursor.fetchone()
        if user is None:
            bot.send_message(message.chat.id, "Неправильное имя пользователя или пароль.")
        else:
            user_id = message.from_user.id
            user_data[message.chat.id]['user_id'] = user_id
            bot.send_message(message.chat.id, "Вы успешно вошли в систему!")

            # Получаем анкету
            cursor.execute("SELECT name, age, city, gender, file_url, phone_number, job FROM main_anketa WHERE user_id = %s;", (user_id,))
            anketa = cursor.fetchone()

            if anketa:
                name, age, city, gender, photo_url, phone_number, job = anketa

                gender_text = {'gender_male': 'мужской', 'gender_female': 'женский'}.get(gender, 'неопределенный')
                job_text = {'main_jobseeker': 'соискатель', 'employer': 'работодатель'}.get(job, 'неопределенный')

                profile_text = (
                    f"<h2>Твоя сохраненная анкета:</h2>\n"
                    f"<p><strong>Name:</strong> {name}</p>\n"
                    f"<p><strong>Age:</strong> {age}</p>\n"
                    f"<p><strong>City:</strong> {city}</p>\n"
                    f"<p><strong>Gender:</strong> {gender_text}</p>\n"
                    f"<p><strong>Contact Phone Number:</strong> {phone_number}</p>\n"
                    f"<p><strong>Job:</strong> {job_text}</p>\n"
                )


                try:
                    response = requests.get(photo_url)
                    if response.status_code == 200:
                        photo = BytesIO(response.content)
                        photo.name = 'profile.jpg'
                        bot.send_photo(message.chat.id, photo, caption=profile_text)
                    else:
                        bot.send_message(message.chat.id, "Error: Unable to retrieve the photo.")
                except requests.exceptions.RequestException as e:
                    bot.send_message(message.chat.id, f"An error occurred while fetching the photo: {e}")
                if job == 'main_jobseeker':
                    cursor.execute("SELECT * FROM main_jobseeker WHERE user_id = %s;", (user_id,))
                    main_jobseeker_entry = cursor.fetchone()
                    
                    if main_jobseeker_entry:
                        # Если есть запись main_jobseeker, выводим все из таблицы main_jobseeker
                        cursor.execute("SELECT * FROM main_jobseeker WHERE user_id = %s;", (user_id,))
                        all_entries = cursor.fetchall()

                        for entry in all_entries:
                            # Выводите информацию из entry в чат, например:
                            bot.send_message(user_id, f"Entry: {entry}")
                        
                        
                            send_confirmation_message(user_id)



                    else:
                        # Если нет записи main_jobseeker, переходим к логике main_jobseeker
                        handle_job_category(message)

                elif job == 'employer':
                    cursor.execute("SELECT * FROM main_employer WHERE user_id = %s;", (user_id,))
                    main_employer_info_entries = cursor.fetchall()

                    if main_employer_info_entries:
                        for entry in main_employer_info_entries:
                            # Получаем имена столбцов
                            column_names = [desc[0] for desc in cursor.description]

                            # Создаем словарь, используя имена столбцов и значения из кортежа
                            entry_dict = dict(zip(column_names, entry))

                            # Теперь вы можете обращаться к значениям по именам столбцов
                            entry_text = (
                                f"ID вакансии : {entry_dict['vacancy_id']}\n"
                                f"Должность: {entry_dict['job_title']}\n"
                                f"специализация: {entry_dict['spec']}\n"
                                f"Название Компании : {entry_dict['company_name']}\n"
                                f"Сфера: {entry_dict['industry']}\n"
                                f"Навыки: {entry_dict['skills']}\n"
                                f"Краткое Описание: {entry_dict['short_description']}\n"
                                f"Описание: {entry_dict['job_description']}\n"
                                f"Зарплата: {entry_dict['salary']}\n"
                                f"Формат: {entry_dict['format_e']}\n"
                                f"Опыт: {entry_dict['experience_e']}\n"



                            )

                            print(f"Type of 'message': {type(message)}")
                            bot.send_message(message.chat.id, entry_text)

                        # Assuming that the 'vacancy_id' is part of the 'entry_dict'
                        vacancy_id = entry_dict.get('vacancy_id')  # Adjust this based on your actual column name

                        # Check if 'vacancy_id' is not None before proceeding
                        if vacancy_id is not None:
                            ask_add_another_vacancy(user_data[user_id]['user_id'], vacancy_id)
                        else:
                            # Handle the case where 'vacancy_id' is None
                            print("Warning: 'vacancy_id' is None")

                    else:
                        # Если нет записей main_employer_info, переходим к логике main_employer_info
                        main_employer_info(message)
                else:
                    # Дополнительная логика для других типов работы
                    pass

            else:
                # Если нет анкеты, переходим к запросу имени и фото
                msg = bot.send_message(message.chat.id, "Введите свое имя:")
                bot.register_next_step_handler(msg, process_name_step, user_id)
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при входе: {e}')


def extract_digits(phone_number):
    return ''.join(filter(str.isdigit, phone_number))


def insert_into_anketa(user_id, name, age, city, gender, photo_url, job, contact_info):
    try:
        # Extract only the numeric part of the phone number
        phone_number = extract_digits(contact_info['phone_number'])

        cursor.execute(
            "INSERT INTO main_anketa (user_id, name, age, city, gender, file_url, phone_number, job) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;",
            (user_id, name, age, city, gender, photo_url, phone_number, job)
        )

        photo_id = cursor.fetchone()[0]
        conn.commit()
        return photo_id
    except Exception as e:
        conn.rollback()
        print(f"Error inserting data into anketa: {str(e)}")




@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = user_data.get(message.chat.id, {}).get('user_id')

    if not user_id:
        bot.send_message(message.chat.id, "Используй /login чтобы войти.")
        return

    try:
        user_data[message.chat.id]['photo_url'] = None  # Initialize photo_url in user_data

    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

def process_name_step(message, user_id):
    try:
        name = message.text
        user_data[message.chat.id]['name'] = name  # Store the name in user_data

        msg = bot.send_message(message.chat.id, "Отлично! Ввeдите возраст.")
        bot.register_next_step_handler(msg, process_age_step, user_id)
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")
def process_age_step(message, user_id):
    try:
        age_str = message.text
        age = int(age_str)  # Преобразование введенного значения в целое число
        if 15 <= age <= 60:  # Проверка, находится ли возраст в допустимом диапазоне
            user_data[message.chat.id]['age'] = age
            msg = bot.send_message(message.chat.id, "Пожаулйста введите ваш город в нижнем регистре(все буквы).Можно на казахском,на русском.Например:'косшы''қосшы'")
            bot.register_next_step_handler(msg, process_city_step, user_id)
        else:
            msg = bot.send_message(message.chat.id, "Пожалуйста, введите допустимый возраст от 15 до 60:")
            bot.register_next_step_handler(msg, process_age_step, user_id)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите свой возраст в виде числа:")
        bot.register_next_step_handler(msg, process_age_step, user_id)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

def get_kazakhstan_cities():
    url = 'https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D0%BE%D0%B2_%D0%9A%D0%B0%D0%B7%D0%B0%D1%85%D1%81%D1%82%D0%B0%D0%BD%D0%B0'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Выбираем первые три ячейки каждой строки
        city_elements = soup.select('.wikitable td:nth-of-type(1), .wikitable td:nth-of-type(2), .wikitable td:nth-of-type(3)')
        cities = [element.get_text(strip=True) for element in city_elements]
        return cities
    else:
        raise Exception("Не удалось получить список городов")

try:
    kazakhstan_cities = get_kazakhstan_cities()
    print("Список городов Казахстана:")
    for city in kazakhstan_cities:
        print(city)
except Exception as e:
    print(f"Произошла ошибка: {str(e)}")


def process_city_step(message, user_id):
    try:
        city = message.text.title()

        if city in kazakhstan_cities:
            user_data[message.chat.id]['city'] = city
            # Запрашиваем пол пользователя с использованием инлайн-клавиатуры
            markup = types.InlineKeyboardMarkup()
            male_button = types.InlineKeyboardButton(text='Мужской', callback_data='gender_male')
            female_button = types.InlineKeyboardButton(text='Женский', callback_data='gender_female')
            markup.add(male_button, female_button)

            # Используем метод send_message бота для ответа пользователю
            bot.send_message(message.chat.id, "Какой у тебя пол?", reply_markup=markup)
        else:
            msg = bot.send_message(message.chat.id, "Введенный город не найден. Пожалуйста, напишите правильно свой город.Город должен быть в Казахстане")
            bot.register_next_step_handler(msg, process_city_step, user_id)

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")


@bot.callback_query_handler(func=lambda call: user_data.get(call.from_user.id, {}).get('user_id') == call.from_user.id and 'gender' not in user_data[call.from_user.id] and call.data.startswith('gender_'))
def handle_gender_callback(call):
    print("Handling gender callback")
    print(f"Callback data: {call.data}")
    print(f"user_data: {user_data}")
    try:
        user_id = call.from_user.id
        print(f"Callback received. Callback data: {call.data}")
        if isinstance(call.data, str):
            gender = call.data.lower()  # Convert to lowercase here
            print(f"Gender selected: {gender}")
            
            gender_text = {'gender_male': 'Мужской', 'gender_female': 'Женский'}.get(gender, 'неопределенный')

            user_data[user_id]['gender'] = gender

            # Изменяем текст сообщения
            bot.edit_message_text(
                chat_id=user_id,
                message_id=call.message.message_id,
                text=f"Вы выбрали пол: {gender_text}",
                reply_markup=None
            )
            msg = bot.send_message(call.message.chat.id, "Отлично! Теперь отправьте свою фотографию.")
            bot.register_next_step_handler(msg, process_photo_step)

            bot.answer_callback_query(callback_query_id=call.id, text=f"You selected {gender}.")

        else:
            bot.send_message(chat_id=user_id, text="Пожалуйста, выберите пол, используя кнопки.")

    except Exception as e:
        print(f"Error in handle_gender_callback: {e}")


def process_received_contact(message):
    try:
        user_id = message.from_user.id

        # Initialize the contact information dictionary if not present
        if 'contact' not in user_data[user_id]:
            user_data[user_id]['contact'] = {}

        # Extract and store contact information
        user_data[user_id]['contact']['phone_number'] = extract_digits(message.contact.phone_number)


        markup = types.InlineKeyboardMarkup()
        main_jobseeker_button = types.InlineKeyboardButton(text='Соискатель', callback_data='main_jobseeker')
        main_employer_button = types.InlineKeyboardButton(text='Работодатель', callback_data='employer')
        markup.add(main_jobseeker_button, main_employer_button)

        # Отправляем сообщение с клавиатурой
        bot.send_message(user_id, "Выберите вашу роль(выбор изменить нельзя):", reply_markup=markup)
    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")
@bot.callback_query_handler(func=lambda call: user_data.get(call.from_user.id, {}).get('user_id') == call.from_user.id and 'gender' in user_data[call.from_user.id] and 'job' not in user_data[call.from_user.id])
def handle_job_callback(call):
    try:
        user_id = call.from_user.id
        print(f"Callback received for find_job. Callback data: {call.data}")
        if isinstance(call.data, str):
            job = call.data.lower()  # Convert to lowercase here
            print(f"Job selected: {job}")

            job_text = {'main_jobseeker': 'соискатель', 'employer': 'работодатель'}.get(job, 'неопределенный')

            user_data[user_id]['job'] = job

            bot.edit_message_text(
                chat_id=user_id,
                message_id=call.message.message_id,
                text=f"Вы выбрали job: {job_text}",
                reply_markup=None
            )

            genders = user_data[user_id]['gender'][:20]
            job = user_data[user_id]['job'][:20]
            photo_id = insert_into_anketa(
                user_id,
                user_data[user_id]['name'],
                user_data[user_id]['age'],
                user_data[user_id]['city'],
                genders,
                user_data[user_id]['photo_url'],
                job,
                user_data[user_id]['contact']  
            )




            gender_text = {'gender_male': 'Мужской', 'gender_female': 'Женский'}.get(genders, 'неопределенный')
            job_text = {'main_jobseeker': 'соискатель', 'employer': 'работодатель'}.get(job, 'неопределенный')

            caption_text = (
                f"Имя: {user_data[user_id]['name']}\n"
                f"Возраст: {user_data[user_id]['age']}\n"
                f"Город: {user_data[user_id]['city']}\n"
                f"Пол: {gender_text}\n"
                f"Контактный номер: {user_data[user_id]['contact']['phone_number']}\n"
                f"Роль: {job_text}\n"
                f"Фото ID: {photo_id}"
            )

            response = requests.get(user_data[user_id]['photo_url'])
            if response.status_code == 200:
                photo = BytesIO(response.content)
                photo.name = 'profile.jpg'  
                bot.send_photo(user_id, photo, caption=caption_text)


                if job == 'main_jobseeker':
                    category_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                    for category in categories_skills.keys():
                        category_markup.add(types.KeyboardButton(category))

                    bot.send_message(user_id, "Теперь выберите категорию:", reply_markup=category_markup)
                    bot.register_next_step_handler_by_chat_id(user_id, process_category_selection)
                elif job == 'employer':

                    main_employer_info(call.message)

        else:
            bot.send_message(chat_id=user_id, text="Пожалуйста, выберите роль, используя кнопки.")

    except Exception as e:
        print(f"Error in handle_job_callback: {e}")
def send_skill_selection_message(user_id):
    skills_list = list(user_data[user_id]['it_job_skills'])

    skills_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for skill in categories_skills[user_data[user_id]['it_job_category']]:
        skill_button = types.KeyboardButton(skill.replace(' ', '_').replace('/', '').lower())
        if skill_button.text.lower() in skills_list:
            skill_button.request_location = True
        skills_markup.add(skill_button)

    skills_markup.add(types.KeyboardButton('Готово'))

    bot.send_message(user_id, f"Выбранные навыки: {', '.join(skills_list)}", reply_markup=skills_markup)
    bot.register_next_step_handler_by_chat_id(user_id, process_skill_selection)
 
categories_skills = {
    'Разработка': ['Java', 'C# / .NET', 'Front-End', 'Node.js', 'PHP', 'Python', 'Мобильная разработка', 'C / C++', 'Golang', 'Другие языки', 'CMS платформы'],
    'Другие технические': ['Дизайнеры / UI / UX', 'Тестирование', 'Аналитика', 'Product Manager', 'Project Manager', 'Architect / Tech Lead', 'Data Science', 'DevOps / Sysadmin', 'Gamedev / Unity', 'SQL / DBA', 'Security'],
    'Нетехнические': ['Рекрутеры и HR', 'Маркетинг', 'Продажи', 'Поддержка'],
}

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('job') == 'main_jobseeker')
def handle_job_category(message):
    try:
        user_id = message.from_user.id

        category_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for category in categories_skills.keys():
            category_markup.add(types.KeyboardButton(category))

        bot.send_message(user_id, "Выберите категорию:", reply_markup=category_markup)
        bot.register_next_step_handler_by_chat_id(user_id, process_category_selection)

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")

def process_category_selection(message):
    try:
        user_id = message.from_user.id
        selected_category = message.text

        user_data[user_id] = {'it_job_category': selected_category, 'it_job_skills': set()}

        send_skill_selection_message(user_id)

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")
def process_skill_selection(message):
    try:
        user_id = message.from_user.id
        selected_skill = message.text.lower()

        if selected_skill == 'готово':
            format_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            format_markup.add(
                types.KeyboardButton('Полный рабочий день'),
                types.KeyboardButton('Гибкий график'),
                types.KeyboardButton('Удаленно'),
            )
            bot.send_message(user_id, "Выберите формат работы:", reply_markup=format_markup)
            bot.register_next_step_handler_by_chat_id(user_id, process_job_format)
            return

        user_data[user_id]['it_job_skills'].add(selected_skill)

        send_skill_selection_message(user_id)
        print(f"user_data after process_skill_selection: {user_data}")

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")

def process_job_format(message):
    try:
        user_id = message.from_user.id
        selected_format = message.text

        user_data[user_id]['format'] = selected_format

        experience_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        experience_markup.add(
            types.KeyboardButton('Нет опыта'),
            types.KeyboardButton('1-3 года'),
            types.KeyboardButton('3-5 лет'),
            types.KeyboardButton('Более 5 лет'),
        )

        bot.send_message(user_id, "Выберите опыт работы:", reply_markup=experience_markup)
        bot.register_next_step_handler_by_chat_id(user_id, process_experience)

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")

def process_experience(message):
    try:
        user_id = message.from_user.id
        selected_experience = message.text

        # Save selected experience to user_data
        user_data[user_id]['experience_j'] = selected_experience
        salary_markup = types.ReplyKeyboardRemove(selective=False)

        # Ask for the salary
        bot.send_message(user_id, "Выберите желаемую зарплату:", reply_markup=salary_markup)
        bot.register_next_step_handler_by_chat_id(user_id, process_salary)

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")


def process_photo_step(message):
    try:
        if 'photo_url' not in user_data[message.chat.id] or user_data[message.chat.id]['photo_url'] is None:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path
            photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

            user_data[message.chat.id]['photo_url'] = photo_url  

            # Отправляем фото
            response = requests.get(photo_url)
            if response.status_code == 200:
                photo = BytesIO(response.content)
                photo.name = 'profile.jpg'  # Присваиваем имя файлу

                user_id = message.from_user.id


                updated_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                updated_markup.add(types.KeyboardButton('Ваш номер телефона', request_contact=True))

                bot.send_message(user_id, "Отправьте ваш номер телефона:", reply_markup=updated_markup)

                bot.register_next_step_handler_by_chat_id(user_id, process_received_contact)

            else:
                bot.send_message(message.chat.id, "Ошибка: Не удалось получить фото.")
        else:
            bot.send_message(message.chat.id, "Фото уже было загружено ранее.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")




# main_employer !!!!!
@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('job') == 'employer')
def main_employer_info(message):  
    try:
        user_id = message.from_user.id


        questions = [
            "Введите должность:",
            "Введите название компании:",
            "Введите отрасль:",
            "Введите навыки:",
            "Введите краткое описание работы:",
            "Введите полное описание работы:",
            "Введите заработную плату:",
            "Выберите формат работы:",
            "Выберите опыт работы:",
            "Выберите специализацию:"
        ]


        user_data[user_id]['employer_info'] = {}

        #  рекурсивный процесс задания вопросов
        ask_question(user_id, questions)

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")

def ask_question(user_id, questions):
    if questions:
        next_question = questions.pop(0)

        if next_question == "Выберите формат работы:":
            markup = get_format_markup()
            msg = bot.send_message(user_id, next_question, reply_markup=markup)
            bot.register_next_step_handler(msg, lambda m, q=next_question: process_format_input(m, user_id, q, questions))
        elif next_question == "Выберите опыт работы:":
            markup = get_experience_markup()
            msg = bot.send_message(user_id, next_question, reply_markup=markup)
            bot.register_next_step_handler(msg, lambda m, q=next_question: process_experience_input(m, user_id, q, questions))
        elif next_question == "Выберите специализацию:":
            markup = get_specialization_markup()
            msg = bot.send_message(user_id, next_question, reply_markup=markup)
            bot.register_next_step_handler(msg, lambda m, q=next_question: process_specialization_input(m, user_id, q, questions))
        else:
            msg = bot.send_message(user_id, next_question)
            bot.register_next_step_handler(msg, lambda m, q=next_question: process_employer_info_input(m, user_id, q, questions))
    else:
        save_employer_info(user_id, user_data[user_id]['employer_info'])




def process_format_input(message, user_id, question, remaining_questions):
    try:
        user_data[user_id]['employer_info'][question] = message.text

        ask_question(user_id, remaining_questions)

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")

def process_experience_input(message, user_id, question, remaining_questions):
    try:
        user_data[user_id]['employer_info'][question] = message.text

        ask_question(user_id, remaining_questions)

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")

def process_specialization_input(message, user_id, question, remaining_questions):
    try:
        user_data[user_id]['employer_info'][question] = message.text

        ask_question(user_id, remaining_questions)

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")


def get_format_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("Полный рабочий день"))
    markup.add(types.KeyboardButton("Гибкий график"))
    markup.add(types.KeyboardButton("Удаленная работа"))
    return markup

def get_experience_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("Нет опыта"))
    markup.add(types.KeyboardButton("1-3 года"))
    markup.add(types.KeyboardButton("3-5 лет"))
    markup.add(types.KeyboardButton("Более 5 лет"))
    return markup

def get_specialization_markup():
    specialization_list = [
        'Java', 'C# / .NET', 'Front-End', 'Node.js', 'PHP', 'Python', 'Мобильная разработка', 'C / C++', 'Golang', 'Другие языки',
        'CMS платформы', 'Дизайнеры / UI / UX', 'Тестирование', 'Аналитика', 'Product Manager', 'Project Manager',
        'Architect / Tech Lead', 'Data Science', 'DevOps / Sysadmin', 'Gamedev / Unity', 'SQL / DBA', 'Security',
        'Рекрутеры и HR', 'Маркетинг', 'Продажи', 'Поддержка'
    ]

    # Convert specialization names to lowercase
    specialization_list_lower = [specialization.lower() for specialization in specialization_list]

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for specialization in specialization_list_lower:
        markup.add(types.KeyboardButton(specialization))

    return markup
def process_employer_info_input(message, user_id, question, remaining_questions):
    try:
        # Сохраняем ответ пользователя
        user_data[user_id]['employer_info'][question] = message.text

        # Задаем следующий вопрос
        ask_question(user_id, remaining_questions)

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")
def get_yes_no_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    return markup

def ask_add_another_vacancy(user_id, vacancy_id):
    try:
        markup = get_yes_no_markup()
        msg = bot.send_message(user_id, "Хотите добавить еще одну вакансию?", reply_markup=markup)
        bot.register_next_step_handler(msg, lambda m: process_add_another_vacancy(m, user_id, vacancy_id))
    except Exception as e:
        bot.send_message(user_id, f'Ошибка при запросе о добавлении еще одной вакансии: {e}')

def process_add_another_vacancy(message, user_id, vacancy_id):
    if message.text.lower() == 'да':
        main_employer_info(message)
    else:
        # Пользователь не хочет добавлять еще одну вакансию
        bot.send_message(user_id, "Спасибо за заполнение информации!")

def save_employer_info(user_id, answers):
    try:
        cursor.execute("""
            INSERT INTO main_employer (user_id, job_title, company_name, industry, skills, short_description, job_description, salary, format_e, experience_e, spec)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING vacancy_id, job_title, company_name, industry, skills, short_description, job_description, salary, format_e, experience_e, spec;
        """, (
            user_id,
            answers.get("Введите должность:"),
            answers.get("Введите название компании:"),
            answers.get("Введите отрасль:"),
            answers.get("Введите навыки:"),
            answers.get("Введите краткое описание работы:"),
            answers.get("Введите полное описание работы:"),
            answers.get("Введите заработную плату:"),
            answers.get("Выберите формат работы:"),
            answers.get("Выберите опыт работы:"),
            answers.get("Выберите специализацию:")
        ))

        vacancy_id, job_title, company_name, industry, skills, short_description, job_description, salary, format_e, experience_e, spec = cursor.fetchone()

        entry_text = (
            f"ID вакансии: {vacancy_id}\n"
            f"Должность: {job_title}\n"
            f"Название компании: {company_name}\n"
            f"Сфера: {industry}\n"
            f"Навыки: {skills}\n"
            f"Краткое Описание: {short_description}\n"
            f"Описание: {job_description}\n"
            f"Зарплата: {salary}\n"
            f"Формат: {format_e}\n"
            f"Опыт: {experience_e}\n"
            f"Специализайия: {spec}\n"
        )

        bot.send_message(user_id, entry_text)

        ask_add_another_vacancy(user_id, vacancy_id)

        conn.commit()

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка при сохранении данных: {str(e)}")


@bot.message_handler(commands=['print_employer'])
def print_employer(message):
    try:
        cursor.execute("SELECT * FROM main_employer")

        rows = cursor.fetchall()

        # Выводим результаты на консоль
        for row in rows:
            print(row)

        # Выводим сообщение пользователю
        bot.send_message(message.chat.id, "Результаты запроса SELECT * FROM main_employer выведены в консоль.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

@bot.message_handler(commands=['print_seeker'])
def print_employer(message):
    try:
        cursor.execute("SELECT * FROM main_jobseeker")

        rows = cursor.fetchall()

        for row in rows:
            print(row)

        bot.send_message(message.chat.id, "Результаты запроса SELECT * FROM main_jobseeker выведены в консоль.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

def process_salary(message):
    try:
        user_id = message.from_user.id
        selected_salary = message.text
        selected_category = user_data[user_id]['it_job_category']
        experience_j = user_data[user_id]['experience_j']

        user_data[user_id]['salary'] = selected_salary
        skills_str = ', '.join(user_data[user_id]['it_job_skills'])



        conn.commit()

        info_text = (
            f"Категория: {selected_category}\n"
            f"Навыки: {skills_str}\n"
            f"Формат работы: {user_data[user_id]['format']}\n"
            f"Опыт работы: {experience_j}\n"
            f"Зарплата: {selected_salary}"
        )
        bot.send_message(user_id, f"Информация успешно сохранена:\n{info_text}")
        send_confirmation_message(user_id)

    except Exception as e:
        print(f"Error in process_salary: {str(e)}")
        bot.send_message(user_id, "Произошла ошибка при сохранении информации.")

# ДЛЯ ОТПРАВКИ ВАКАНСИИ 
def get_matching_employers(main_jobseeker_specialization):
    try:
        print("Job Seeker Specialization:", main_jobseeker_specialization)

        if main_jobseeker_specialization:

            cursor.execute("""
                SELECT id, short_description , spec
                FROM main_employer
                WHERE spec IN %s;
            """, (tuple(main_jobseeker_specialization),))

            matching_employers = cursor.fetchall()

            print("Matching main_employers:", matching_employers)

            return matching_employers
        else:
            print("Job Seeker Specialization is empty. Skipping the query.")
            return []

    except Exception as e:
        print(f"Error in get_matching_employers: {str(e)}")
        return []
def send_confirmation_message(user_id):
    try:
        main_jobseeker_specialization = user_data.get(user_id, {}).get('it_job_skills', [])

        matching_employers = get_matching_employers(main_jobseeker_specialization)

        if matching_employers:
            for main_employer in matching_employers:
                message_text = (
                    f"Найден подходящий работодатель:\n"
                    f"ID: {main_employer[0]}\n"
                    f"Описание: {main_employer[1]}\n"
                    f" специализация: {main_employer[2]}\n"

                )

                inline_keyboard = types.InlineKeyboardMarkup()
                details_button = types.InlineKeyboardButton("Подробнее", callback_data=f"details_{main_employer[0]}")
                like_button = types.InlineKeyboardButton("Нравится", callback_data=f"like_{main_employer[0]}")
                dislike_button = types.InlineKeyboardButton("Не нравится", callback_data=f"dislike_{main_employer[0]}")

                inline_keyboard.add(details_button)
                inline_keyboard.add(like_button, dislike_button)

                bot.send_message(user_id, message_text, reply_markup=inline_keyboard)

        else:
            bot.send_message(user_id, "К сожалению, нет подходящих вакансий для ваших навыков и специализации.")

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")
#НАДО ОТ НАЧАЛА ДО КОНЦА ПРОЙТИ В АНКЕТЕ НЕТ ИНФО О РАБОТОДАТЕЛЕ 
def get_vacancy_details(vacancy_id):
    try:
        cursor.execute("""
            SELECT e.job_title, e.company_name, e.industry, e.skills, e.job_description, e.salary, 
                e.format_e, e.experience_e, e.spec, a.user_id, a.phone_number
            FROM main_employer e
            JOIN main_anketa a ON e.user_id = a.user_id
            WHERE e.vacancy_id = %s;
        """, (vacancy_id,))
        vacancy_details = cursor.fetchone()

        if vacancy_details:
            column_names = [column[0] for column in cursor.description]
            vacancy_dict = dict(zip(column_names, vacancy_details))

            details_str = (
                f"Job Title: {vacancy_dict['job_title']}\n"
                f"Company: {vacancy_dict['company_name']}\n"
                f"Industry: {vacancy_dict['industry']}\n"
                f"Skills: {vacancy_dict['skills']}\n"
                f"Job Description: {vacancy_dict['job_description']}\n"
                f"Salary: {vacancy_dict['salary']}\n"
                f"Format: {vacancy_dict['format_e']}\n"
                f"Experience: {vacancy_dict['experience_e']}\n"
                f"Specialization: {vacancy_dict['spec']}\n"
                f"User_id: {vacancy_dict['user_id']}\n"
                f"phone_number: {vacancy_dict['phone_number']}"

            )
            return details_str
        else:
            return "Вакансия не найдена."

    except Exception as e:
        return f"Произошла ошибка при выполнении SQL-запроса: {str(e)}"

@bot.callback_query_handler(func=lambda call: call.data.startswith('details_'))
def vacancy_details_callback(call):
    try:
        vacancy_id = int(call.data.split('_')[1])
        vacancy_details = get_vacancy_details(vacancy_id)

        if vacancy_details:
            keyboard = types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton("Нравится", callback_data=f"like_1_Интересно"),
                 types.InlineKeyboardButton("Не нравится", callback_data=f"dislike_1_Неинтересно")]
            ])

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=vacancy_details,
                reply_markup=keyboard
            )
        else:
            bot.send_message(call.message.chat.id, "Вакансия не найдена.")

    except Exception as e:
        bot.send_message(call.message.chat.id, f"Произошла ошибка: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('like_') or call.data.startswith('dislike_'))
def feedback_callback(call):
    try:
        vacancy_id = int(call.data.split('_')[1])
        action = call.data.split('_')[0]
        user_id = call.from_user.id

        feedback_text = call.data.split('_')[2] if len(call.data.split('_')) > 2 else "Интересно"

        if action in ('like', 'dislike'):
            save_feedback(user_id, vacancy_id, action, feedback_text)

            if action == 'like':
                bot.send_message(user_id, "Вакансия добавлена в ваши предпочтения.")
                notify_employer_about_interest(user_id, vacancy_id)
            elif action == 'dislike':
                bot.send_message(user_id, "Больше не будем предлагать.")

                
        else:
            bot.send_message(user_id, "Произошла ошибка при обработке вашего выбора.")

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")

def save_feedback(user_id, vacancy_id, action, feedback_text):
    try:
        main_feedback_table = 'main_feedback_table'  

        cursor.execute(f"""
            INSERT INTO {main_feedback_table} (user_id_id, vacancy_id_id, action, feedback_text)
            VALUES (%s, %s, %s, %s);
        """, (user_id, vacancy_id, action, feedback_text))

        conn.commit()
    except Exception as e:
        print(f"Error saving feedback to the database: {str(e)}")
        conn.rollback()



def notify_employer_about_interest(user_id, vacancy_id):
    try:
        vacancy_details = get_vacancy_details(vacancy_id)
        main_employer_user_id = vacancy_details.get('user_id')
        # Получаем информацию о соискателе (без контакта и ссылки на фото)
        main_jobseeker_details = get_main_jobseeker_details_without_contact(user_id)


       
        bot.send_message(                                                                                                                                                            
            main_employer_user_id,
            f"Вашей вакансии проявил интерес соискатель (user_id: {user_id}, vacancy_id: {vacancy_id}).\n"
            f"Подробности: {main_jobseeker_details}",
            # reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка при уведомлении работодателя о интересе: {str(e)}")
def get_main_jobseeker_details_without_contact(user_id):
    try:
        cursor.execute("""
SELECT 
    a.name,
    a.age,
    a.city,
    a.gender,
    js.category,
    js.skill,
    js.experience_j,
    js.format,
    js.salary
FROM 
    main_anketa a
JOIN 
    main_jobseeker js ON a.user_id = js.user_id
            WHERE a.user_id = %s ;
        """, (user_id,))

        main_jobseeker_details = cursor.fetchone()

        if main_jobseeker_details:
            details_str = f"Имя: {main_jobseeker_details[0]}\n" \
                        f"Возраст: {main_jobseeker_details[1]}\n" \
                        f"Город: {main_jobseeker_details[2]}\n" \
                        f"Пол: {main_jobseeker_details[3]}\n" \
                        f"Категория: {main_jobseeker_details[4]}\n" \
                        f"Навык: {main_jobseeker_details[5]}\n" \
                        f"Опыт работы: {main_jobseeker_details[6]}\n" \
                        f"Формат работы: {main_jobseeker_details[7]}\n" \
                        f"Зарплата: {main_jobseeker_details[8]}\n"

            print(details_str)

            return details_str
        else:
            return "Информация о соискателе не найдена."

    except Exception as e:
        return f"Произошла ошибка при выполнении SQL-запроса: {str(e)}"

@bot.callback_query_handler(func=lambda call: call.data.startswith('interest_'))
def handle_interest_callback(call):
    try:
        vacancy_id = int(call.data.split('_')[1])
        user_id = call.from_user.id

        save_feedback(user_id, vacancy_id, is_interest=True)

        notify_employer_about_interest(user_id, vacancy_id)

        notify_main_jobseeker(user_id, vacancy_id, is_interest=True)

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    except Exception as e:
        print(f"Error handling interest callback: {str(e)}")
        bot.send_message(user_id, "Произошла ошибка при обработке вашего выбора.")
def notify_main_jobseeker(user_id, vacancy_id, is_interest=True):
    try:
        vacancy_details = get_vacancy_details(vacancy_id)
        
        cursor.execute("""
            SELECT * FROM main_anketa WHERE user_id = %s;
        """, (vacancy_details['user_id'],))
        main_employer_details = cursor.fetchone()

        if main_employer_details and is_interest:
            message_text = f"Ваша анкета понравилась работодателю (вакансия: {vacancy_details['job_title']}).\n" \
                           f"Информация о работодателе:\n" \
                           f"Имя: {main_employer_details['name']}\n" \
                           f"Возраст: {main_employer_details['age']}\n" \
                           f"Город: {main_employer_details['city']}\n" \
                           f"Пол: {main_employer_details['gender']}\n" \
                           f"Телефон: {main_employer_details['phone_number']}"
        else:
            message_text = f"К сожалению, ваша анкета не прошла отбор работодателя (вакансия: {vacancy_details['job_title']}).\n"

        # Отправляем уведомление
        bot.send_message(user_id, message_text)

    except Exception as e:
        print(f"Error notifying job seeker: {str(e)}")


def send_contact_and_photo_info(chat_id, user_id):
    try:
        cursor.execute("""
            SELECT phone_number, file_url FROM main_anketa WHERE user_id = %s;
        """, (user_id,))
        user_info = cursor.fetchone()

        if user_info:
            contact_info = user_info['phone_number']
            photo_url = user_info['file_url']

            # Отправляем контакт и фото
            bot.send_contact(chat_id, contact_info, first_name="Информация о контакте")
            bot.send_photo(chat_id, photo_url, caption="Фото соискателя")
        else:
            bot.send_message(chat_id, "Контакт и фото не найдены.")
    except Exception as e:
        print(f"Error sending contact and photo info: {str(e)}")

if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error in the main loop: {e}")

    conn.commit()
    cursor.close()
    conn.close()
