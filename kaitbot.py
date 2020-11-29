# coding=UTF-8
from datetime import datetime, date, time
import vk_api, random
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import sqlite3
import requests
import json
import pyowm
from pyowm.commons.enums import SubscriptionTypeEnum
from pyowm.utils.measurables import kelvin_to_celsius

database = sqlite3.connect('data.db')
cursor = database.cursor()

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

my_token = '2fa2b46a0a27c25145b623649a2143fb8dff601d5f4150997ed9e0d9d9ee9f1bacb0d052cf9febc97e055'

vk_session = vk_api.VkApi(token = my_token)
session_api = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, '200587301')

def get_but(text, color):
	return {
		"action": {
			"type": "text",
			"payload": "{\"button\": \"" + "1" + "\"}",
			"label": f"{text}"
		},
		"color": f"{color}"
	}

grouplist=[]
for group in cursor.execute('SELECT groups FROM Schedule').fetchall():
	grouplist.append(group[0])
weekdays={1:'Понедельник',2:'Вторник',3:'Среда',4:'Четверг',5:'Пятница'}

keyboard = {
	"one_time": True,
	"buttons": [
		[get_but('🗓 Расписание', 'default'), get_but('🗒 Пары', 'default')],
		[get_but('🔔 Звонки', 'default'), get_but('🌡 Погода', 'default')]
	]
}
keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))

vkDict = {1:"xvanche", 2:"fraybyl", 3:"dennimi", 4:"id219093647", 5:"1nigm4"} 

def week():
	global nowDay
	nowDay = datetime.today().isoweekday() 
	nowWeek = requests.get("http://junior.ru/расписание/").text.split('Эта неделя ')[1].split('(')[0]
	if nowWeek=='четная':
		return 'ЧЁТНАЯ'
	return 'НЕЧЕТНАЯ'

def sender(id, text):
	try: 
		session_api.messages.send(
			key = (chat_key),
			server = (chat_server),
			ts=(chat_ts),
			random_id = get_random_id(),
			message=text,
			chat_id = event.chat_id,
			keyboard=keyboard
		)
	except:
		if peer_id=='':
			vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'random_id' : 0, 'keyboard': keyboard})
		else:
			session_api.messages.send(peer_id=peer_id,message=text,random_id=0, keyboard=keyboard)

def weather(city):
	city.lower()
	if nowDay>5:
		city = city
	elif nowDay<=5 and city !="москва":
		city='москва'
		sender(id, "В будние дни, погода доступна только в городе Москва")
	elif nowDay<=5:
		city == "москва"
	try:
		if city == "питер" or city == "спб" or city == "петербург":
			city = "санкт-петербург"
		PyOwm = pyowm.OWM('2a6565823dc741847bd762b19114d062', config=config)
		weatherManager = PyOwm.weather_manager()
		observation = weatherManager.weather_at_place(city)
		Weather = observation.weather

		if int(Weather.wind()['deg']) == 0:windLine = "Западный"
		elif int(Weather.wind()['deg']) == 45:windLine = "Северный"
		elif int(Weather.wind()['deg']) == 90:windLine = "Восточный"
		elif int(Weather.wind()['deg']) == 135:windLine = "Южный"
		elif int(Weather.wind()['deg']) > 0 and int(Weather.wind()['deg']) < 45:windLine = "Северо-западный"
		elif int(Weather.wind()['deg']) > 45 and int(Weather.wind()['deg']) < 90:windLine = "Северо-восточный"
		elif int(Weather.wind()['deg']) > 90 and int(Weather.wind()['deg']) < 135:windLine = "Юго-восточный"
		elif int(Weather.wind()['deg']) > 135 and int(Weather.wind()['deg']) != 0:windLine = "Юго-западный"

		if Weather.detailed_status == "небольшой дождь":weaterStatus = "небольшой дождь 🌧"
		elif Weather.detailed_status == "небольшая облачность":weaterStatus = "небольшая облачность ☁"
		elif Weather.detailed_status == "пасмурно":weaterStatus = "пасмурно ☁"
		elif Weather.detailed_status == "плотный туман":weaterStatus = "плотный туман 🌫"
		elif Weather.detailed_status == "ясно":weaterStatus = "ясно ☀"
		elif Weather.detailed_status == " облачно с прояснениями":weaterStatus = " облачно с прояснениями ⛅"
		else: weaterStatus = Weather.detailed_status

		sender(id, "Погода в указанном городе: " + observation.location.name + "\n" +
				"Погодные условия: " + weaterStatus + "\n" +
				"💨 Ветер: " + str(Weather.wind()['speed']) + " м/с" + ", " + windLine + "\n" +
				"💦 Влажность: " + str(Weather.humidity) + " %" + "\n" +
				"🌡 Температура: " + str(round(kelvin_to_celsius(Weather.temp['temp']))) + " ℃" + " Ощущается как: " + str(
				round(kelvin_to_celsius(Weather.temp['feels_like']))) + " ℃" + "\n" +
				"🌡↑ Температура днем: " + str(round(kelvin_to_celsius(Weather.temp['temp_max']))) + " ℃" + "\n" +
				"🌡↓ Температура ночью: " + str(round(kelvin_to_celsius(Weather.temp['temp_min']))) + " ℃")
	except: sender(id, "Что-то пошло не так, попробуйте еще раз.")

def check_user(id):
	if cursor.execute("SELECT id FROM Users WHERE id=%s"%id).fetchone() is None:
		cursor.execute('INSERT INTO Users(id,state) VALUES(%d,"Студент")'%id)
		database.commit()

def check_group(id):
	if cursor.execute('SELECT groups FROM Users WHERE id=%s'%id).fetchone()[0] is None:
		sender(id, 'Необходимо указать №группы - Группа №группы.')
		return False
	return cursor.execute('SELECT groups FROM Users WHERE id=%s'%id).fetchone()[0]

def check_thread(id):
	if cursor.execute('SELECT thread FROM Users WHERE id=%s'%id).fetchone()[0] is None:
		return False
	return cursor.execute('SELECT thread FROM Users WHERE id=%s'%id).fetchone()[0]

def check_pg(id):
	if cursor.execute('SELECT pg FROM Users WHERE id=%s'%id).fetchone()[0] is None:
		return "?"
	return cursor.execute('SELECT pg FROM Users WHERE id=%s'%id).fetchone()[0]

def check_state(id):
	if cursor.execute('SELECT state FROM Users WHERE id=%s'%id).fetchone()[0]=='Куратор' or cursor.execute('SELECT state FROM Users WHERE id=%s'%id).fetchone()[0]=='Староста':
		return True
	return False

def check_admin(selected_id):
	for ids in session_api.messages.getConversationMembers(peer_id = peer_id)["items"]:
		if ids["member_id"] == selected_id:
			admin = ids.get('is_admin', False)
			if admin == True:return True
			return False

def kick(id,selected_id):
	session_api.messages.removeChatUser(chat_id=event.chat_id,user_id=selected_id,random_id=0)
	FIO(selected_id)
	sender(id, f'@id{selected_id}({fullname}) был кикнут с беседы')

def check_student(id,selected_id):
	FIO(selected_id)
	if id==selected_id:
		sender(id, f"{name}, твои данные:\nДолжность: {cursor.execute('SELECT state FROM Users WHERE id=%s'%id).fetchone()[0]}\nГруппа: {check_group(id)}\nПодгруппа: {check_pg(id)}\nПоток: {cursor.execute('SELECT thread FROM Users WHERE id=%s'%id).fetchone()[0]}")
	else:
		sender(id, f"Данные пользователя {fullname}:\nДолжность: {cursor.execute('SELECT state FROM Users WHERE id=%s'%selected_id).fetchone()[0]}\nГруппа: {check_group(selected_id)}\nПодгруппа: {check_pg(selected_id)}\nПоток: {cursor.execute('SELECT thread FROM Users WHERE id=%s'%selected_id).fetchone()[0]}")

def group(id):
	group=cursor.execute('SELECT groups FROM Users WHERE id=%s'%id).fetchone()[0]
	ids=[]
	for id in cursor.execute('SELECT id FROM Users WHERE groups="%s"'%group).fetchall():
		ids.append(id[0])
	text=''
	n=1
	for id in ids:
		FIO(id)
		pd=check_pg(id)
		text=text+f'{n}. {fullname} [{pd}]\n'
		n=n+1
	sender(id, text)

def FIO(id):
	global name,lastname,fullname
	name=session_api.users.get(user_ids = id)[0]['first_name']
	lastname=session_api.users.get(user_ids = id)[0]['last_name']
	fullname=f'{str(name)} {str(lastname)}'
	city=session_api.users.get(user_ids = id, fields= "city")[0]['city']['title']

try:
	for event in longpoll.listen():
		if event.type == VkBotEventType.MESSAGE_NEW:
			msg=event.object.message['text'].lower()
			print(event)
			if msg!='':
				peer_id=''
				chat=session_api.groups.getLongPollServer(group_id=200587301)
				chat_key=chat['key']
				chat_server=chat['server']
				chat_ts=chat['ts']
				peer_id=event.object.message['peer_id']
				id = event.object.message['from_id']
				check_user(id)
				for ids in session_api.messages.getConversationMembers(peer_id = peer_id)["items"]:
					if ids["member_id"] == id:
						admin = ids.get('is_admin', False)
						if admin == True:access=True
						else:access=False
						break
				FIO(id)
				print(f'[{name} {lastname}] {msg}')
				if msg.find("[club")>=0:
					msg=msg.split()
					del(msg[0])
					msg=' '.join(msg)
				if msg == 'статус':
					check_student(id,id)
				elif msg.find("погода")>=0:
					week()
					if msg=='🌡 погода':weather("москва")
					elif msg.split()[0]=='погода':
						try:weather(msg.split()[1])
						except:weather('москва')
				elif msg == 'начать':
					sender(id, 'Чтобы начать укажите:\nСвою группу - Группа №группы\nПодгруппу - пг №подгруппы\n\nИнфо - вывод список доступных команд')
				elif msg == 'инфо':
					randVK=vkDict[random.randrange(1,6)]
					FIO(randVK)
					#для админов беседы
					if access==True:sender(id, 'Группа - вывод доступных групп Юниор\nГруппа №группы - стать студентом группы\nСтатус - вывод информации о себе\nПогода - узнать погоду в г. Москве\nПогода город - узнать погоду в городе(доступно только в выходные дни)\nРасписание - вывод расписания на всю неделю\nПары - вывод расписания на сегодня\nЗвонки - вывод расписания звонков\nНеделя - вывод чётности недели(НЕЧЕТНАЯ, ЧЁТНАЯ)\nСтудент @id - вывод информации о студенте\nКик @id - исключить пользователя из беседы\nСтуденты - вывод всех студентов в группе\nКуратор @id - назначить пользователя куратором\nСтароста @id - назначить пользователя старостой\n\nОстались вопросы? Пишите: vk.com/%s'%randVK)
					#для кураторов и старост
					elif check_state(id)==True:sender(id, 'Группа - вывод доступных групп Юниор\nГруппа №группы - стать студентом группы\nСтатус - вывод информации о себе\nПогода - узнать погоду в г. Москве\nПогода город - узнать погоду в городе(доступно только в выходные дни)\nРасписание - вывод расписания на всю неделю\nПары - вывод расписания на сегодня\nЗвонки - вывод расписания звонков\nНеделя - вывод чётности недели(НЕЧЕТНАЯ, ЧЁТНАЯ)\nСтудент @id - вывод информации о студенте\nКик @id - исключить пользователя из беседы\nСтуденты - вывод всех студентов в группе\n\nОстались вопросы? Пишите: vk.com/%s'%randVK)
					#для студентов
					else:sender(id, 'Группа - вывод доступных групп Юниор\nГруппа №группы - стать студентом группы\nСтатус - вывод информации о себе\nПогода - узнать погоду в г. Москве\nПогода город - узнать погоду в городе(доступно только в выходные дни)\nРасписание - вывод расписания на всю неделю\nПары - вывод расписания на сегодня\nЗвонки - вывод расписания звонков\nНеделя - вывод чётности недели(НЕЧЕТНАЯ, ЧЁТНАЯ)\n\nОстались вопросы? Пишите: vk.com/%s'%randVK)
				elif msg=="неделя":
					sender(id, week())
				elif msg == "звонки"or msg=='🔔 звонки':
					group=check_group(id)
					if group!=False:
						thread=check_thread(id)
						if thread!=False:
							sender(id, cursor.execute('SELECT bells FROM Threads WHERE thread="%s"'%thread).fetchone()[0])
						else:sender(id, 'Напишите: Группа №группы, для начала работы с ботом')
				elif msg == "пары" or msg=='🗒 пары':
					group=check_group(id)
					if group!=False:
						week()
						nowDay=1
						if nowDay>5:
							sender(id, 'Отдыхай :D Сегодня нет пар')
						else:
							pg=check_pg(id)
							if pg!='?':
								text=cursor.execute('SELECT "All" FROM Schedule WHERE groups="%s"'%group).fetchone()[0]
								sender(id, f'[{group}-{pg}] Расписание на сегодня:\n{text.split(weekdays[nowDay])[1].split(f"{week()}{pg}")[1]}')
							else:
								sender(id, 'Необходимо указать свою подгруппу\nПг №подгруппы')
				elif msg == "расписание" or msg=='🗓 расписание':
					group=check_group(id)
					if group!=False:
						pg=check_pg(id)
						if pg!='?':
							text=cursor.execute('SELECT "All" FROM Schedule WHERE groups="%s"'%group).fetchone()[0]
							n=1
							schedule=[]
							while n!=6:
								if n==1:schedule.append(f'[{group}-{pg}] Расписание на неделю:\n{weekdays[n]}\n{text.split(weekdays[n])[1].split(f"{week()}{pg}")[1]}')
								else:schedule.append(f'\n{weekdays[n]}\n{text.split(weekdays[n])[1].split(f"{week()}{pg}")[1]}')
								n=n+1
							n=0
							schedule="".join(schedule)
							sender(id, schedule)
						else:sender(id, 'Необходимо указать свою подгруппу\nПг №подгруппы')
				elif msg.split()[0] == "группа":
					try:
						for gp in grouplist:
							if msg.split()[1]==gp.lower():
								cursor.execute('UPDATE Users SET groups="%s" WHERE id=%s'%(msg.split()[1].upper(),id))
								if msg.split()[1].find('исп1')>=0 or msg.split()[1].find('исп2')>=0:
									thread=1
								else:
									thread=2
								cursor.execute('UPDATE Users SET thread=%s WHERE id=%s'%(thread,id))
								database.commit()
								sender(id, f'Теперь Вы участник группы {msg.split()[1].upper()}')
								break
							elif gp==grouplist[-1]:sender(id, f'Доступные группы: {", ".join(grouplist)}')
					except:sender(id, f'Доступные группы: {", ".join(grouplist)}')
				elif msg.split()[0]=='кик' and (access==True or check_state(id)==True):
					try:
						if check_admin(int(msg.split()[1].replace('[id',"").split('|')[0]))!=True:
							kick(id,int(msg.split()[1].replace('[id',"").split('|')[0]))
						else:sender(id,'Невозможно исключить данного пользователя')
					except:sender(id, 'Не найден ID пользователя')
				elif msg.split()[0]=='куратор' and access==True:
					try:
						cursor.execute('UPDATE Users SET state="Куратор" WHERE id=%d'%int(msg.split()[1].replace('[id',"").split('|')[0]))
						database.commit()
						FIO(int(msg.split()[1].replace('[id',"").split('|')[0]))
						sender(id, 'Пользователю @id%s(%s) присвоена должность "Куратор"'%(msg.split()[1].replace('[id',"").split('|')[0],fullname))
					except:sender(id, 'Не найден ID пользователя')
				elif msg.split()[0]=='староста' and access==True:
					try:
						cursor.execute('UPDATE Users SET state="Староста" WHERE id=%d'%int(msg.split()[1].replace('[id',"").split('|')[0]))
						database.commit()
						FIO(int(msg.split()[1].replace('[id',"").split('|')[0]))
						sender(id, 'Пользователю @id%s(%s) присвоена должность "Староста"'%(msg.split()[1].replace('[id',"").split('|')[0],fullname))
					except:sender(id, 'Не найден ID пользователя')
				elif msg.split()[0]=='пг':
					try:
						if msg.split()[1]=="1" or msg.split()[1]=="2":
							cursor.execute('UPDATE Users SET pg=%s WHERE id=%s'%(msg.split()[1],id))
							database.commit()
							sender(id, 'Вы успешно записаны в подгруппу %s'%msg.split()[1])
						else:sender(id, 'Доступные подгруппы - 1, 2')
					except:sender(id, 'Доступные подгруппы - 1, 2')
				elif msg.split()[0]=='студент' and (access==True or check_state(id))==True:
					try:check_student(id,int(msg.split()[1].replace('[id',"").split('|')[0]))
					except:sender(id, 'Не найден ID пользователя')
				elif msg.split()[0]=='студенты' and (access==True or check_state(id)==True):group(id)
except Exception as e:print(e)				