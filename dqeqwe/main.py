import telebot, shelve, sqlite3
import config, dop, payments, adminka, files

bot = telebot.TeleBot(config.token)
in_admin = [820110898]



@bot.message_handler(content_types=["text"])
def message_send(message):
	if '/start' == message.text:
		if message.chat.username:
			if dop.get_sost(message.chat.id) is True: 
				with shelve.open(files.sost_bd) as bd: del bd[str(message.chat.id)]
			if message.chat.id in in_admin: in_admin.remove(message.chat.id)
			if message.chat.id == config.admin_id and dop.it_first(message.chat.id) is True: in_admin.append(message.chat.id)
			elif dop.it_first(message.chat.id) is True and message.chat.id not in dop.get_adminlist():
				bot.send_message(message.chat.id, 'Бот ещё не готов к работе!\n Sorry!')
			elif dop.check_message('start') is True:
				key = telebot.types.InlineKeyboardMarkup()
				key.add(telebot.types.InlineKeyboardButton(text='Перейти к каталогу товаров', callback_data='Перейти к каталогу товаров'))
				with shelve.open(files.bot_message_bd) as bd: start_message = bd['start']
				start_message = start_message.replace('username', message.chat.username)
				start_message = start_message.replace('name', message.from_user.first_name)
				bot.send_message(message.chat.id, start_message, reply_markup=key)	
			elif dop.check_message('start') is False and message.chat.id in dop.get_adminlist():
				bot.send_message(message.chat.id, 'Приветствие ещё не добавлено!\nЧтобы его добавить, перейдите в админку по команде /adm и *настройте ответы бота*', parse_mode='Markdown')

			dop.user_loger(chat_id=message.chat.id) #логгирование юзеровs
		elif not message.chat.username:
			with shelve.open(files.bot_message_bd) as bd: start_message = bd['userfalse']
			start_message = start_message.replace('uname', message.from_user.first_name)
			bot.send_message(message.chat.id, start_message, parse_mode='Markdown')
			
	elif '/adm' == message.text:
		if not message.chat.id in in_admin:  in_admin.append(message.chat.id)
		adminka.in_adminka(message.chat.id, message.text, message.chat.username, message.from_user.first_name)

	elif  message.chat.id in in_admin: adminka.in_adminka(message.chat.id, message.text, message.chat.username, message.from_user.first_name)

	elif '/help' == message.text:
		if dop.check_message('help') is True:
			with shelve.open(files.bot_message_bd) as bd: help_message = bd['help']
			bot.send_message(message.chat.id, help_message)
		elif dop.check_message('help') is False and message.chat.id in dop.get_adminlist():
			bot.send_message(message.chat.id, 'Сообщение с помощью ещё не добавлено!\nЧтобы его добавить, перейдите в админку по команде /adm и *настройте ответы бота*', parse_mode='Markdown')







	elif dop.get_sost(message.chat.id) is True:
		with shelve.open(files.sost_bd) as bd: sost_num = bd[str(message.chat.id)]
		if sost_num == 22:
			key = telebot.types.InlineKeyboardMarkup()
			try:
				amount = int(message.text) #проверяется, числительно ли это
				with open('data/Temp/' + str(message.chat.id) + 'good_name.txt', encoding='utf-8') as f: name_good = f.read()
				if dop.get_minimum(name_good) <= amount <= dop.amount_of_goods(name_good):
					sum = dop.order_sum(name_good, amount)
					if dop.check_vklpayments('qiwi') == '✅' and dop.check_vklpayments('btc') == '✅':
						b1 = telebot.types.InlineKeyboardButton(text='🥝Qiwi🥝', callback_data='Qiwi')
						b2 = telebot.types.InlineKeyboardButton(text='💰btc', callback_data='btc')
						key.add(b1, b2)
					elif dop.check_vklpayments('qiwi') == '✅': key.add(telebot.types.InlineKeyboardButton(text='🥝Qiwi🥝', callback_data='Qiwi'))
					elif dop.check_vklpayments('btc') ==  '✅': key.add(telebot.types.InlineKeyboardButton(text='💰btc', callback_data='btc'))
					key.add(telebot.types.InlineKeyboardButton(text='Вернуться в начало', callback_data = 'Вернуться в начало'))
					bot.send_message(message.chat.id,'Вы *выбрали*: ' + name_good + '\n*Количеством*: ' + str(amount) + '\n*Сумма* заказа: ' + str(sum) + ' р\nВыбирите, куда желаете оплатить', parse_mode='Markdown', reply_markup=key)
					with open('data/Temp/' + str(message.chat.id) + '.txt', 'w', encoding='utf-8') as f:
						f.write(str(amount) + '\n') #записывается количество выбраных товаров
						f.write(str(sum) + '\n') #записывается стоимость выбранных товаров
				elif dop.get_minimum(name_good) >= amount: 
					key.add(telebot.types.InlineKeyboardButton(text = 'Вернуться в начало', callback_data = 'Вернуться в начало'))
					bot.send_message(message.chat.id, 'Выберите и отправьте большее количество!\nМинимальное количество к покупке *' + str(dop.get_minimum(name_good)) + '*', parse_mode='Markdown', reply_markup=key)
				elif amount >= dop.amount_of_goods(name_good): 
					bot.send_message(message.chat.id, 'Выберите и отправьте меньшее количество!\nМаксимальное количество к покупке *' + str(dop.amount_of_goods(name_good)) + '*', parse_mode='Markdown', reply_markup=key)
			except: 
				key.add(telebot.types.InlineKeyboardButton(text='Вернуться в начало', callback_data='Вернуться в начало'))
				bot.send_message(message.chat.id, 'Нужное количество выбирать строго в цифрах!', reply_markup=key)








#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~инлайн режим~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
@bot.callback_query_handler(func=lambda c:True)
def inline(callback):
	the_goods = dop.get_goods()
	if callback.message.chat.id in in_admin:
		adminka.ad_inline(callback.data, callback.message.chat.id, callback.message.message_id)

	elif callback.data == 'Перейти к каталогу товаров':
		con = sqlite3.connect(files.main_db)
		cursor = con.cursor()
		cursor.execute("SELECT name, price FROM goods;")
		key = telebot.types.InlineKeyboardMarkup()
		for name, price in cursor.fetchall():
			key.add(telebot.types.InlineKeyboardButton(text = name, callback_data = name))
		key.add(telebot.types.InlineKeyboardButton(text = 'Вернуться в начало', callback_data = 'Вернуться в начало'))
		con.close()

		if dop.get_productcatalog() == None: bot.answer_callback_query(callback_query_id=callback.id, show_alert=True, text='На данный момент в боте не было создано ни одной позиции')
		else:
			try: bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=dop.get_productcatalog(), reply_markup=key, parse_mode='Markdown')
			except: pass

	elif callback.data in the_goods:
		with open('data/Temp/' + str(callback.message.chat.id) + 'good_name.txt', 'w', encoding='utf-8') as f: f.write(callback.data)
		key = telebot.types.InlineKeyboardMarkup()
		key.add(telebot.types.InlineKeyboardButton(text = 'Купить', callback_data = 'Купить'))
		key.add(telebot.types.InlineKeyboardButton(text = 'Вернуться в начало', callback_data = 'Вернуться в начало'))
		try: bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=dop.get_description(callback.data), reply_markup=key)
		except: pass

	elif callback.data == 'Вернуться в начало':
		if callback.message.chat.username:
			if dop.get_sost(callback.message.chat.id) is True: 
				with shelve.open(files.sost_bd) as bd: del bd[str(callback.message.chat.id)]
			key = telebot.types.InlineKeyboardMarkup()
			key.add(telebot.types.InlineKeyboardButton(text = 'Перейти к каталогу товаров', callback_data = 'Перейти к каталогу товаров'))
			with shelve.open(files.bot_message_bd) as bd: start_message = bd['start']
			start_message = start_message.replace('username', callback.message.chat.username)
			start_message = start_message.replace('name', callback.message.from_user.first_name)
			try: bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=start_message, reply_markup=key)
			except: pass
		elif not callback.message.chat.username:
			with shelve.open(files.bot_message_bd) as bd: start_message = bd['userfalse']
			start_message = start_message.replace('uname', callback.message.from_user.first_name)
			bot.send_message(callback.message.chat.id, start_message, parse_mode='Markdown')

	elif callback.data == 'Купить':
		with open('data/Temp/' + str(callback.message.chat.id) + 'good_name.txt', encoding='utf-8') as f: name_good = f.read()
		if dop.amount_of_goods(name_good) == 0: bot.answer_callback_query(callback_query_id=callback.id, show_alert=True, text='В данный момент недоступно к покупке')
		elif dop.payments_checkvkl() == None: bot.answer_callback_query(callback_query_id=callback.id, show_alert=True, text='Оплата на данный момент отключена')
		else:
			key = telebot.types.InlineKeyboardMarkup()
			key.add(telebot.types.InlineKeyboardButton(text = 'Вернуться в начало', callback_data = 'Вернуться в начало'))
			try: bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Введите *количество* товаров к покупке\n*Минимальное* количество к покупке: ' + str(dop.get_minimum(name_good)) + '\n*Максимальное* доступное: ' + str(dop.amount_of_goods(name_good)), reply_markup=key, parse_mode='Markdown')
			except: pass
			with shelve.open(files.sost_bd) as bd: bd[str(callback.message.chat.id)] = 22

	elif callback.data == 'btc' or callback.data == 'Qiwi':
		if callback.data == 'Qiwi':
			with open('data/Temp/' + str(callback.message.chat.id) + 'good_name.txt', encoding='utf-8') as f: name_good = f.read()
			amount = dop.normal_read_line('data/Temp/' + str(callback.message.chat.id) + '.txt', 0)
			sum = dop.normal_read_line('data/Temp/' + str(callback.message.chat.id) + '.txt', 1)

			payments.creat_bill_qiwi(callback.message.chat.id, callback.id, callback.message.message_id, sum, name_good, amount)
		elif callback.data == 'btc':
			sum = dop.normal_read_line('data/Temp/' + str(callback.message.chat.id) + '.txt', 1)
			with open('data/Temp/' + str(callback.message.chat.id) + 'good_name.txt', encoding='utf-8') as f: name_good = f.read()
			amount = dop.normal_read_line('data/Temp/' + str(callback.message.chat.id) + '.txt', 0)
			if int(sum) < 40: bot.answer_callback_query(callback_query_id=callback.id, show_alert=True, text='Сумму менее 100 рублей оплатить в btc невозможно!')

			else: payments.creat_bill_btc(callback.message.chat.id, callback.id, callback.message.message_id, sum, name_good, amount)
	elif callback.data == 'Проверить оплату': payments.check_oplata_qiwi(callback.message.chat.id, callback.from_user.username, callback.id, callback.message.from_user.first_name)
	
	elif callback.data == 'Проверить оплату btc': payments.check_oplata_btc(callback.message.chat.id, callback.from_user.username, callback.id, callback.message.from_user.first_name)

	elif dop.get_sost(callback.message.chat.id) is True:
		with shelve.open(files.sost_bd) as bd: sost_num = bd[str(callback.message.chat.id)]
		if sost_num == 12: pass 






	









#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~работа с файлами~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
@bot.message_handler(content_types=['document'])
def handle_docs_log(message):
		if message.chat.id in in_admin:
			if shelve.open(files.sost_bd)[str(message.chat.id)] == 12:
				adminka.new_files(message.document.file_id, message.chat.id)
		







if __name__ == '__main__':
	bot.infinity_polling()


