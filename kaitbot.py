import sqlite3
from random import randrange as random
import requests
import datetime
import pyowm
from pyowm.commons.enums import SubscriptionTypeEnum
from pyowm.utils.measurables import kelvin_to_celsius
from tokens import Your_WeatherToken
import time

database = sqlite3.connect('data.db')
cursor = database.cursor()

Supports = {1:"xvanche", 2:"fraybyl", 3:"dennimi", 4:"id219093647", 5:"1nigm4"}
weekdays={1:'Понедельник',2:'Вторник',3:'Среда',4:'Четверг',5:'Пятница'}

config = {
	'subscription_type': SubscriptionTypeEnum.FREE,
	'language': 'ru',
	'connection': {
		'use_ssl': True,
		'verify_ssl_certs': True,
		'use_proxy': False,
		'timeout_secs': 5
	},
	'proxies': {
		'http': 'http://user:pass@host:port',
		'https': 'socks5://user:pass@host:port'
	}
}

class KaitBot:

	def __init__(self,user_id,session_api,peer_id):
		self.user_id = user_id
		self.session_api = session_api
		self.peer_id = peer_id
		self.commands = ['начать', 'статус', 'инфо', 'неделя', 'погода', 'звонки', 'пары', 
						'расписание', 'группа', 'пг', 'кик', 'куратор', 'староста', 'студент',
						'уведомления','каит']

	def new_message(self, message):
		self.check_user_exist(self.user_id)
		self.get_fullname(self.user_id)
		with open('logs.data', 'a') as logs:
			logs.write(f'[{time.strftime("%H:%M")}] [{self.peer_id}]{self.selected_username}: {message}\n')
		try:
			if (message in self.commands) or (message.split()[0] in self.commands):
				# Если в беседе, иначе в ЛС			
				if self.peer_id!=self.user_id: 
					peer = True
					message = message.split()
					if message[0]=='каит':
						del(message[0])
						message=' '.join(message)
				else: peer = False

				if message == 'начать': return 'Чтобы начать укажите:\n1. Группу - Группа №группы\n2. Подгруппу - пг №подгруппы\n\nИнфо - вывод список доступных команд'
				elif message.split()[0] == "статус":
					try: selected_user_id = int(message.split()[1].replace('[id',"").split('|')[0])
					except: selected_user_id = self.user_id
					return self.get_user(selected_user_id)
				elif message == 'инфо':
					Support = Supports[random(1,6)]
					if peer == True:
						if self.check_permisson(self.user_id) == True: return f'Группа - вывод доступных групп Юниор\nГруппа №группы - стать студентом группы\nСтатус - вывод информации о себе\nПогода - узнать погоду в г. Москве\nПогода город - узнать погоду в городе(доступно только в выходные дни)\nРасписание - вывод расписания на всю неделю\nПары - вывод расписания на сегодня\nЗвонки - вывод расписания звонков\nНеделя - вывод чётности недели(НЕЧЕТНАЯ, ЧЁТНАЯ)\nСтудент @id - вывод информации о студенте\nКик @id - исключить пользователя из беседы\nСтуденты - вывод всех студентов в группе\nКуратор @id - назначить пользователя куратором\nСтароста @id - назначить пользователя старостой\n\nОстались вопросы? Пишите: vk.com/{Support}'
						elif self.check_state(self.user_id) == True: return f'Группа - вывод доступных групп Юниор\nГруппа №группы - стать студентом группы\nСтатус - вывод информации о себе\nПогода - узнать погоду в г. Москве\nПогода город - узнать погоду в городе(доступно только в выходные дни)\nРасписание - вывод расписания на всю неделю\nПары - вывод расписания на сегодня\nЗвонки - вывод расписания звонков\nНеделя - вывод чётности недели(НЕЧЕТНАЯ, ЧЁТНАЯ)\nСтудент @id - вывод информации о студенте\nКик @id - исключить пользователя из беседы\nСтуденты - вывод всех студентов в группе\n\nОстались вопросы? Пишите: vk.com/{Support}'
						else: return f'Группа - вывод доступных групп Юниор\nГруппа №группы - стать студентом группы\nСтатус - вывод информации о себе\nПогода - узнать погоду в г. Москве\nПогода город - узнать погоду в городе(доступно только в выходные дни)\nРасписание - вывод расписания на всю неделю\nПары - вывод расписания на сегодня\nЗвонки - вывод расписания звонков\nНеделя - вывод чётности недели(НЕЧЕТНАЯ, ЧЁТНАЯ)\n\nОстались вопросы? Пишите: vk.com/{Support}'
					else: return f'Группа - вывод доступных групп Юниор\nГруппа №группы - стать студентом группы\nСтатус - вывод информации о себе\nПогода - узнать погоду в г. Москве\nПогода город - узнать погоду в городе(доступно только в выходные дни)\nРасписание - вывод расписания на всю неделю\nПары - вывод расписания на сегодня\nЗвонки - вывод расписания звонков\nНеделя - вывод чётности недели(НЕЧЕТНАЯ, ЧЁТНАЯ)\n\nОстались вопросы? Пишите: vk.com/{Support}'
				elif message == 'неделя': return self.check_week_and_weekday()
				elif message.split()[0] == 'погода':
					try:city = message.split()[1]
					except:city = 'москва' 
					return self.get_weather(city)
				elif message == 'звонки': return self.get_bells()
				elif message == 'пары': return self.get_lecture(self.user_id)
				elif message == 'расписание': return self.get_schedule()
				elif message.split()[0] == 'группа':
					try: group=message.split()[1].upper()
					except:group=''
					return self.add_group(group)
				elif message.split()[0] == 'пг':
					try: subGroup = message.split()[1]
					except: return 'Доступные подгруппы - 1, 2'
					return self.add_subgroup(subGroup)
				elif message.split()[0] == 'кик':
					if peer == True:
						if self.check_permisson(self.user_id)==True or self.check_state(self.user_id)=='Куратор' or self.check_state(self.user_id)=='Староста':
							try: selected_user_id = int(message.split()[1].replace('[id',"").split('|')[0])
							except: return 'Неверно указан ID пользователя.\nПример: кик @kait20official'
							return self.kick_user(selected_user_id)
						return 'Ты не можешь исключать пользователей!'
					else: return 'Данная возможность не поддерживается здесь'
				elif message.split()[0] in {'куратор','староста','студент'}:
					if peer == True:
						if self.check_permisson(self.user_id)==True:
							state = message.split()[0].title()
							try: selected_user_id = int(message.split()[1].replace('[id',"").split('|')[0])
							except: return f'Неверно указан ID пользователя.\nПример: {state} @kait20official'
							return self.add_state(selected_user_id,state)
				elif message.split()[0] == 'уведомления':
					try: turn = message.split()[1]
					except : turn = ''
					if turn in {'вкл','выкл','включить','выключить',''}:
						return self.set_notify_politics(turn)
				else: return f'{self.seleceted_username}, неизвестная команда\nНапиши инфо, чтобы узнать список доступных команд'
		except:pass
		return False

	def check_user_exist(self,selected_user_id):
		if cursor.execute('SELECT id FROM Users WHERE id=%s'%selected_user_id).fetchone() is None:
			cursor.execute('INSERT INTO Users(id,state,notify) VALUES(%s,"Студент","False")'%selected_user_id)
			database.commit()

	def check_week_and_weekday(self):
		now = datetime.datetime.now()
		self.weekDay = now.isoweekday()
		weekNum = int(datetime.date(now.year, now.month, now.day).isocalendar()[1])
		if weekNum % 2 == 0: self.weekNum = 'ЧЁТНАЯ'
		else: self.weekNum = 'НЕЧЕТНАЯ'
		return f"Неделя {weekNum}: {self.weekNum}"

	def get_weather(self,city):
		self.check_week_and_weekday()
		infoMsg=''
		if self.weekDay <= 5 and city != "москва":
			city='москва'
			infoMsg="В будние дни, погода доступна только в городе Москва"
		elif self.weekDay <= 5: city == "москва"
		try:
			if city in {"питер","спб","петербург"}:
				city = "санкт-петербург"
			PyOwm = pyowm.OWM(Your_WeatherToken, config=config)
			weatherManager = PyOwm.weather_manager()
			observation = weatherManager.weather_at_place(city)
			Weather = observation.weather

			windDeg = int(Weather.wind()['deg'])
			if windDeg == 0:windLine = "Западный"
			elif windDeg == 45:windLine = "Северный"
			elif windDeg == 90:windLine = "Восточный"
			elif windDeg == 135:windLine = "Южный"
			elif windDeg > 0 and int(Weather.wind()['deg']) < 45:windLine = "Северо-западный"
			elif windDeg > 45 and int(Weather.wind()['deg']) < 90:windLine = "Северо-восточный"
			elif windDeg > 90 and int(Weather.wind()['deg']) < 135:windLine = "Юго-восточный"
			elif windDeg > 135 and int(Weather.wind()['deg']) != 0:windLine = "Юго-западный"

			weatherStatus = Weather.detailed_status
			if weatherStatus == "небольшой дождь":weatherStatus = "небольшой дождь 🌧"
			elif weatherStatus == "небольшая облачность":weatherStatus = "небольшая облачность ☁"
			elif weatherStatus == "пасмурно":weatherStatus = "пасмурно ☁"
			elif weatherStatus == "плотный туман":weatherStatus = "плотный туман 🌫"
			elif weatherStatus == "ясно":weatherStatus = "ясно ☀"
			elif weatherStatus == " облачно с прояснениями":weatherStatus = " облачно с прояснениями ⛅"

			return ("Погода в указанном городе: " + observation.location.name + "\n" +
					"Погодные условия: " + weatherStatus + "\n" +
					"💨 Ветер: " + str(Weather.wind()['speed']) + " м/с" + ", " + windLine + "\n" +
					"💦 Влажность: " + str(Weather.humidity) + " %" + "\n" +
					"🌡 Температура: " + str(round(kelvin_to_celsius(Weather.temp['temp']))) + " ℃" + " Ощущается как: " + str(
					round(kelvin_to_celsius(Weather.temp['feels_like']))) + " ℃" + "\n" +
					"🌡↑ Температура днем: " + str(round(kelvin_to_celsius(Weather.temp['temp_max']))) + " ℃" + "\n" +
					"🌡↓ Температура ночью: " + str(round(kelvin_to_celsius(Weather.temp['temp_min']))) + " ℃" + f"\n\n{infoMsg}")
		except: return "Что-то пошло не так, попробуйте еще раз."

	def check_permisson(self,selected_user_id):
		for id in self.session_api.messages.getConversationMembers(peer_id=self.peer_id)["items"]:
			if id["member_id"] == selected_user_id:
				if id.get('is_admin', False)==True:
					return True
				return False
	
	def check_group(self,selected_user_id):
		if cursor.execute('SELECT groups FROM Users WHERE id=%s'%selected_user_id).fetchone()[0] is None:
			return 'не указана'
		return cursor.execute('SELECT groups FROM Users WHERE id=%s'%selected_user_id).fetchone()[0]

	def check_subgroup(self,selected_user_id):
		if cursor.execute('SELECT pg FROM Users WHERE id=%s'%selected_user_id).fetchone()[0] is None:
			return "не указана"
		return cursor.execute('SELECT pg FROM Users WHERE id=%s'%selected_user_id).fetchone()[0]
	
	def check_thread(self,selected_user_id):
		if cursor.execute('SELECT thread FROM Users WHERE id=%s'%selected_user_id).fetchone()[0] is None:
			return '-'
		return cursor.execute('SELECT thread FROM Users WHERE id=%s'%selected_user_id).fetchone()[0]
	
	def check_state(self,selected_user_id):
		return cursor.execute('SELECT state FROM Users WHERE id=%s'%selected_user_id).fetchone()[0]

	def check_all_groups(self):
		groupslist=[]
		for group in cursor.execute('SELECT groups FROM Schedule').fetchall():
			groupslist.append(group[0])
		return groupslist
	
	def get_user(self,selected_user_id):
		self.check_user_exist(selected_user_id)
		self.get_fullname(selected_user_id)
		return f"[{self.check_state(selected_user_id)}] {self.selected_username}:\nГруппа: {self.check_group(selected_user_id)}\nПодгруппа: {self.check_subgroup(selected_user_id)}\nПоток: {self.check_thread(selected_user_id)}"

	def get_fullname(self,selected_user_id):
		first_name = self.session_api.users.get(user_ids = selected_user_id)[0]['first_name']
		last_name = self.session_api.users.get(user_ids = selected_user_id)[0]['last_name']
		self.selected_username = f'{str(first_name)} {str(last_name)}'

	def get_schedule(self):
		self.check_week_and_weekday()
		group=self.check_group(self.user_id)
		if group != 'не указана':
			subGroup = self.check_subgroup(self.user_id)
			if subGroup != '-':
				Schedule=cursor.execute('SELECT "All" FROM Schedule WHERE groups="%s"'%group).fetchone()[0]
				schedule = []
				n = 1
				while n != 6:
					smile='✏'
					if n == 1:schedule.append(f'[{group}-{subGroup}] Расписание на неделю:\n{smile}{weekdays[n]}\n{Schedule.split(weekdays[n])[1].split(f"{self.weekNum}{subGroup}")[1]}')
					else:schedule.append(f'\n{smile}{weekdays[n]}\n{Schedule.split(weekdays[n])[1].split(f"{self.weekNum}{subGroup}")[1]}')
					n += 1
				n = 0
				schedule="".join(schedule)
				return schedule
		return 'Обязательно к заполнению:\n1. Группа - Группа №группы\n2. Подгруппа - пг №подгруппы\n\nИнфо - вывод список доступных команд'

	def get_bells(self):
		group = self.check_group(self.user_id)
		if group != 'не указана':
			thread = self.check_thread(self.user_id)
			if thread != '-':
				return cursor.execute('SELECT bells FROM Threads WHERE thread="%s"'%thread).fetchone()[0]
		return 'Обязательно к заполнению:\n1. Группа - Группа №группы\n2. Подгруппа - пг №подгруппы\n\nИнфо - вывод список доступных команд'

	def get_lecture(self,user_id):
		group = self.check_group(user_id)
		if group != 'не указана':
			self.check_week_and_weekday()
			if self.weekDay>5:
				return 'Отдыхай :D Сегодня нет пар'
			else:
				subGroup = self.check_subgroup(user_id)
				if subGroup != '-':
					schedule=cursor.execute('SELECT "All" FROM Schedule WHERE groups="%s"'%group).fetchone()[0]
					return f'[{group}-{subGroup}] Расписание на сегодня:\n{schedule.split(weekdays[self.weekDay])[1].split(f"{self.weekNum}{subGroup}")[1]}'
		return 'Обязательно к заполнению:\n1. Группа - Группа №группы\n2. Подгруппа - пг №подгруппы\n\nИнфо - вывод список доступных команд'

	def set_notify_politics(self,turn):
		self.get_fullname(self.user_id)
		if (cursor.execute('SELECT notify FROM Users WHERE id=%s'%self.user_id).fetchone()[0] == 'True' and turn in {'вкл','включить'}) or (cursor.execute('SELECT notify FROM Users WHERE id=%s'%self.user_id).fetchone()[0] == 'False' and turn in {'выкл','выключить'}):
			if turn in {'вкл','включить'}: text = 'включены'
			else: text = 'выключены'
			return f'{self.selected_username}, уведомления уже {text}'
		if turn in {'вкл','включить'}:
			cursor.execute('UPDATE Users SET notify="True" WHERE id=%s'%self.user_id)
			text = 'включены'
		elif turn in {'выкл','выключить'}:
			cursor.execute('UPDATE Users SET notify="False" WHERE id=%s'%self.user_id)
			text = 'выключены'
		else:
			if cursor.execute('SELECT notify FROM Users WHERE id=%s'%self.user_id).fetchone()[0] == 'True':
				cursor.execute('UPDATE Users SET notify="False" WHERE id=%s'%self.user_id)
				text = 'выключены'
			else:
				cursor.execute('UPDATE Users SET notify="True" WHERE id=%s'%self.user_id)
				text = 'включены'
		database.commit()
		return f'{self.selected_username}, уведомления {text}'

	def add_group(self,group):
		if group == self.check_group(self.user_id):
			return 'Ты уже состоишь в этой группе!'
		groupslist = self.check_all_groups()
		if group in groupslist:
			cursor.execute('UPDATE Users SET groups="%s" WHERE id=%s'%(group,self.user_id))
			if group.find('ИСП') >= False: thread = 1
			else: thread = 2
			cursor.execute('UPDATE Users SET thread=%s WHERE id=%s'%(thread,self.user_id))
			database.commit()
			return f'Теперь Вы участник группы {group}'
		return f'Доступные группы: {", ".join(groupslist)}'

	def add_subgroup(self,subGroup):
		if int(subGroup) == self.check_subgroup(self.user_id):
			return f'Ты уже состоишь в подгруппе {subGroup}'
		if subGroup in {"1","2"}:
			cursor.execute('UPDATE Users SET pg=%s WHERE id=%s'%(subGroup,self.user_id))
			database.commit()
			return 'Вы успешно записаны в подгруппу %s'%subGroup
		return 'Доступные подгруппы - 1, 2'

	def add_state(self,selected_user_id,state):
		self.check_user_exist(selected_user_id)
		self.get_fullname(selected_user_id)
		cursor.execute('UPDATE Users SET state="%s" WHERE id=%d'%(state,selected_user_id))
		database.commit()
		return f'Пользователю @id{selected_user_id}({self.selected_username}) присвоена должность {state}!'

	def kick_user(self,selected_user_id):
		try:
			if self.check_permisson(selected_user_id)!=True:
				self.session_api.messages.removeChatUser(chat_id = self.peer_id,user_id = selected_user_id,random_id = 0)
				self.get_fullname(selected_user_id)
				return f'@id{selected_user_id}({self.selected_username}) был исключен из беседы'
			else: return 'Невозможно исключить данного пользователя'
		except: return 'Неверно указан ID пользователя.\nПример: кик @kait20official'

	def notifications(self):
		result=False
		currentTime=time.strftime('%H:%M')
		thread=1
		for bells in cursor.execute('SELECT bells FROM Threads').fetchall():
			n=1
			while n!=6:
				try:
					bell=bells[0].split('\n')[n].split(f'пара -> ')[1].split("-")[0].split(':')
				except:pass
				bell[1]=int(bell[1])-5
				if bell[1]<0:
					bell[1]=60+bell[1]
					bell[0]=str(int(bell[0])-1)
				bell[1]=str(bell[1])
				if len(bell[1])==1:
					bell[1]=f'0{bell[1]}'
				if len(bell[0])==1:
					bell[0]=f'0{bell[0]}'	
				bell=':'.join(bell)
				if bell == currentTime:
					result=True
					for user_id in cursor.execute('SELECT id FROM Users WHERE notify="True"').fetchall():
						if self.check_thread(user_id[0]) == thread:
							text = self.get_lecture(user_id).split('\n')[n]
							if text.replace(f'{n}. ','') != '':
								text = f'[Напоминание] Через 5 минут начнется пара!\n{text}'
								self.send_notification(user_id,text)
				n+=1
			thread+=1
		return result

	def send_notification(self,user_id,text):
		self.session_api.messages.send(
			peer_id = user_id,
			message = text,
			random_id = 0, 
		)