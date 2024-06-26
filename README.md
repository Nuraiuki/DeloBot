Телеграм-бот DELO предоставляет простой и удобный способ взаимодействия между работодателями, имеющими вакансии, и соискателями, ищущими подходящие вакансии.
Работодатели могут легко размещать вакансии и находить подходящих кандидатов. Соискатели, в свою очередь, могут получать персонализированный список вакансий, соответствующих их профилю, и устанавливать контакт с работодателями.
DELO стремится предоставить удобный и быстрый инструмент для успешного поиска работы и подбора персонала в Казахстане.

Основные функции и возможности для реализации в ПО:

	Регистрация и аутентификация пользователей через логин и пароль.
	Связь учетных данных с Telegram ID для обеспечения уникальности аккаунта.
	Хранение личных данных пользователей в безопасном режиме в админ панели
	Возможность обмена контактами между пользователями по запросу.
	Парсинг введенных городов для проверки их на соответствие списку городов Казахстана.
	Получать авторизированный номер телефона пользователя из Telegram.
	Выбор роли (работодатель или соискатель) с невозможностью изменения в будущем.
	Предоставление соответствующих вопросов и функциональности в зависимости от выбранной роли.
	Заполнение опросных форм для получения персонализированного списка вакансий.
	Фильтрация вакансий по критериям специализации для точного поиска.
	Представление результатов поиска в виде информационных карточек с изображением.
	Создание работодателями нескольких вакансий с указанием всех необходимых деталей.
	Получение персонализированного списка вакансий для соискателей.
	Просмотр и оценка подходящих вакансий.
	Возможность обмена контактами с работодателями.

Сценарии использования
- При запуске телеграмм бота выводится приветственное сообщение с командами  register и login.
- При отправке команды /register, пользователю предлагается заполнить логин и пароль.Система проверяет введенные данные на валидность и отсутствие в базе данных.После успешной проверки создается новый аккаунт с уникальным идентификатором и сохраняется в таблице users в базе данных.
- Для Авторизация пользователь вводит свой логин и пароль, отправляя команду login.
- После регистрации пользователь заполняет анкету с персональной информацией, включая имя, возраст, город, пол, номер телефона и фотографию.
- Используя парсинг  проверяет введенный город на наличие в списке городов Казахстана и отправляет сообщение об ошибке при несоответствии.
- Авторизированный номер телефона, взятый из самого  Telegram пользователя.
- Система выводит анкету с полной информацией и изображением.
- Пользователь выбирает роль (работодатель или соискатель), которую не может изменить в дальнейшем. И на основе выбранной роли предоставляется соответствующие вопросы и функциональности
- Фильтрация по специализации обеспечивает точный поиск.
- Соискатель получает результаты поиска в виде информационных карточек о вакансиях с краткой информацией. Для получения дополнительной информации и контактов о вакансии соискатель нажимает кнопку "Подробнее".Также может оценивать интересующие его вакансии
- Работодатель может выложить несколько вакансии.Получает список подходящих кандидатов на вакансию.Для выбора подходящих кандидатов работодатель просматривает профили соискателей и их резюме.контактну информацию и личные данные может просмотреть только при нажатии на  кнопку Подробнее.
- Все действия пользователя, такие как создание анкеты,резюме,вакансий сохраняются в базе данных.При повторном входе в систему пользователь получает доступ к своим предыдущим действиям


Архитектурный стиль для системы управления вакансиями и резюме на Telegram боте - это Событийно-ориентированная архитектура. Этот выбор обусловлен необходимостью быстрой реакции на действия пользователей, простотой в масштабировании и обслуживании.
Telegram Bot API: Он отвечает за прием входящих сообщений, а также отправку ответов на эти сообщения.
Обработчики событий: Каждый обработчик событий отвечает за обработку конкретного вида события.
База данных: Отвечает за хранение всех данных, необходимых для функционирования ботаё

Взаимосвязь и взаимодействие:
Когда пользователь отправляет сообщение боту через Telegram, Telegram Bot API получает это сообщение и передает его соответствующему обработчику событий.
 Обработчик событий определяет какое действие должно быть выполнено в ответ на это сообщение.
Обработчик событий может взаимодействовать с базой данных для получения необходимой информации или для сохранения новых данных
После выполнения необходимых действий бот может отправить ответное сообщение пользователю через Telegram.

Язык программирования, фреймворки, библиотеки и инструменты:
Python: Основной язык программирования для разработки бэкенда.
Django Admin: Позволяет администраторам управлять данными.
PostgreSQL в качестве системы управления базами данных.
Библиотеки:
telebot: Для взаимодействия с Telegram API и обработки сообщений от пользователей.
requests: Для выполнения HTTP-запросов.
bytesIO: Для работы с изображениями в байтовом формате.
psycopg2: Для взаимодействия с базой данных PostgreSQL.
Beautifulsoup4: Для парсинга и извлечения информации с веб-страниц.

Django Admin:
- Позволяет администраторам управлять данными, включая удаление и изменение информации
- Использует таблицы для хранения данных о пользователях, анкетах, вакансиях и соискателях. Пользователи (id, username, password), Анкета (имя, возраст, город, пол, фото, номер телефона, роль), Вакансии (должность, название компании, индустрия, навыки, краткое описание, полное описание, формат, опыт, зарплата, специализация), Соискатели (категория, навыки, формат, опыт, зарплата).

1.2.	Структура базы данных:<br/>
![image](https://github.com/Nuraiuki/DeloBot/assets/160646532/d2df6bc3-149b-4e46-8e9b-041fbc75be4d)
Основные таблицы:
Пользователи(id, username,password)
Анкета(имя, возраст, город, пол, фото, номер телефона, роль)
Вакансии(должность, название компании, индустрия, навыки, краткое описание, полное описание, формат, опыт, зарплата, специализация)
Соискатели(категория, навыки, формат, опыт, зарплата)
DELO охватывает сферу поиска работы в области информационных технологий. Пользователи могут быть как работодателями, размещающими вакансии, так и соискателями, ищущими подходящие вакансии. Система обеспечивает эффективное взаимодействие между этими двумя категориями участников.
Работодатели:
Создание и управление вакансиями.
Подбор подходящих соискателей.
Получение информации о навыках и кандидатах.
Соискатели:
Поиск и просмотр вакансий.
Просмотр вакансий 
Обмен контактами с работодателями.

