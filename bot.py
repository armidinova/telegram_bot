import telebot
import mysql.connector

bot = telebot.TeleBot('1012142701:AAHPoCqUI5BtKbiTgZhRjvS8ijUnjizqtO0')

mydb = mysql.connector.connect(
    host="34.73.1.210",
    user="root",
    passwd="8912044572",
    database="telegram"
)


@bot.message_handler(commands=["start"])
def start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_phone = telebot.types.KeyboardButton(text="Отправить номер телефона ☎️", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id, "Для входа нажмите кнопку 'Отправить номер телефона' ", reply_markup=keyboard)

    # Авторизация


@bot.message_handler(content_types=["contact"])
def read_contact_data(message):
    phone_number = message.contact.phone_number
    name = message.contact.first_name
    cursor = mydb.cursor()
    cursor.execute("SELECT count(*) FROM users WHERE phone = " + phone_number)
    myresult = cursor.fetchone()
    count = myresult[0]

    @bot.message_handler(commands=["detail_incomes"])
    def detail_incomes(message):
        cursor.execute("SELECT id FROM users WHERE  phone = " + phone_number)
        check_pass = cursor.fetchone()
        user_id = check_pass[0]
        cursor.execute("SELECT title, val FROM incomes WHERE user_id = " + str(user_id))
        show_detail = cursor.fetchall()
        bot.send_message(message.from_user.id, "Детализация Ваших доходов: \n")
        for x in show_detail:
            bot.send_message(message.from_user.id, str(x[0]) + ": " + str(x[1]) + " тенге \n")
        bot.send_message(message.from_user.id, "Для добавления пункта нажмите /add_incomes")

    @bot.message_handler(commands=["detail_expenses"])
    def detail_expenses(message):
        cursor.execute("SELECT id FROM users WHERE  phone = " + phone_number)
        check_pass = cursor.fetchone()
        user_id = check_pass[0]
        cursor.execute("SELECT title, val FROM expenses WHERE user_id = " + str(user_id))
        show_detail = cursor.fetchall()
        bot.send_message(message.from_user.id, "Детализация Ваших расходов: \n")
        for x in show_detail:
            bot.send_message(message.from_user.id, str(x[0]) + ": " + str(x[1]) + " тенге \n")
        bot.send_message(message.from_user.id, "Для добавления пункта нажмите /add_expenses")

    if count == 1:
        bot.send_message(message.from_user.id, "Введите пароль:")

        @bot.message_handler(content_types=['text'])
        def pass_or_command(message):
            if message.text == '/add_incomes':
                global table_name
                table_name = 'incomes'
                bot.send_message(message.from_user.id, 'Введите название: ')
                bot.register_next_step_handler(message, set_name)

            elif message.text == '/add_expenses':
                table_name = 'expenses'
                bot.send_message(message.from_user.id, 'Введите название: ')
                bot.register_next_step_handler(message, set_name)

            else:
                global user_id
                password = message.text
                cursor.execute(
                    "SELECT count(*), id FROM users WHERE password like '" + password + "' AND phone = " + phone_number)
                check_pass = cursor.fetchone()
                pass_count = check_pass[0]
                user_id = check_pass[1]

                if pass_count == 1:
                    bot.send_message(message.from_user.id, "Добро пожаловать, " + name)
                    cursor.execute("SELECT sum(val) FROM incomes WHERE user_id = " + str(user_id))
                    all_incomes = cursor.fetchone()
                    incomes_sum = all_incomes[0]
                    cursor.execute("SELECT sum(val) FROM expenses WHERE user_id = " + str(user_id))
                    all_expenses = cursor.fetchone()
                    expenses_sum = all_expenses[0]
                    bot.send_message(message.from_user.id, "Общая сумма Ваших доходов: " + str(incomes_sum) + " тенге")
                    bot.send_message(message.from_user.id,
                                     "Общая сумма Ваших расходов: " + str(expenses_sum) + " тенге")
                    bot.send_message(message.from_user.id, "Для детализации доходов нажмите /detail_incomes")
                    bot.send_message(message.from_user.id, "Для детализации  расходов нажмите /detail_expenses")

                else:
                    bot.send_message(message.from_user.id, "Вы ввели неверный пароль. Введите пароль еще раз: ")



    else:
        bot.send_message(message.from_user.id, "Вы не зарегистрированы, пожалуйста придумайте пароль")

        @bot.message_handler(content_types=['text'])
        def set_password(message):  # получаем пароль
            password = message.text
            bot.send_message(message.from_user.id, "Ваш пароль: " + password)
            cursor1 = mydb.cursor()
            sql = "INSERT INTO users (phone, password) VALUES (%s, %s)"
            val = (phone_number, password)
            cursor1.execute(sql, val)
            mydb.commit()
            print("Добавлено в базу данных")
            bot.send_message(message.from_user.id,
                             "Поздравляем, Вы успешно зарегистрированы! Вы можете пройти к Step 2!")


    def set_name(message):
        global get_name
        get_name = message.text
        bot.send_message(message.from_user.id, 'Введите значение: ')
        bot.register_next_step_handler(message, set_value)

    def set_value(message):
        global message_value
        message_value = message.text
        add_new(message)

    def add_new(message):
        global user_id
        cursor = mydb.cursor()
        cursor.execute("SELECT id FROM users WHERE  phone = " + phone_number)
        user = cursor.fetchone()
        user_id = user[0]
        cursor.execute(
            "INSERT INTO " + table_name + "(user_id, title, val) VALUES (" + str(
                user_id) + ", '" + get_name + "', " + str(message_value) + ") ")
        mydb.commit()
        bot.send_message(message.chat.id, "Запись добавлена")
        total_result(message)

    def total_result(message):
        if table_name == 'incomes':
            bot.send_message(message.from_user.id, "Детализация Ваших доходов: \n")
        elif table_name == 'expenses':
            bot.send_message(message.from_user.id, "Детализация Ваших расходов: \n")
        cursor.execute("SELECT title, val FROM " + table_name + " WHERE user_id = " + str(user_id))
        show_detail = cursor.fetchall()
        for x in show_detail:
            bot.send_message(message.from_user.id, str(x[0]) + ": " + str(x[1]) + " тенге \n")
        if table_name == 'incomes':
            bot.send_message(message.from_user.id, "Для добавления пункта нажмите /add_incomes")
        elif table_name == 'expenses':
            bot.send_message(message.from_user.id, "Для добавления пункта нажмите /add_expenses")


bot.polling()
