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

bd = sqlite3.connect('data.db')
c = bd.cursor()

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
for group in c.execute('SELECT groups FROM Schedule').fetchall():
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
	if nowDay == 6 or 7:
		city = city
	elif nowDay != 6 or 7 and city == "москва":
		city == "москва"
	elif nowDay != 6 or 7 and city != "москва":
		sender(id, "В будние дни, погода доступна только в городе Москва")
	try:
		if city == "питер" or city == "спб" or city == "петербург":
			city = "санкт-петербург"
		owm = pyowm.OWM('2a6565823dc741847bd762b19114d062', config=config)
		mgr = owm.weather_manager()
		observation = mgr.weather_at_place(city)
		w = observation.weather

		if int(w.wind()['deg']) == 0:windLine = "Западный"
		elif int(w.wind()['deg']) == 45:windLine = "Северный"
		elif int(w.wind()['deg']) == 90:windLine = "Восточный"
		elif int(w.wind()['deg']) == 135:windLine = "Южный"
		elif int(w.wind()['deg']) > 0 and int(w.wind()['deg']) < 45:windLine = "Северо-западный"
		elif int(w.wind()['deg']) > 45 and int(w.wind()['deg']) < 90:windLine = "Северо-восточный"
		elif int(w.wind()['deg']) > 90 and int(w.wind()['deg']) < 135:windLine = "Юго-восточный"
		elif int(w.wind()['deg']) > 135 and int(w.wind()['deg']) != 0:windLine = "Юго-западный"

		if w.detailed_status == "небольшой дождь":weaterStatus = "небольшой дождь 🌧"
		elif w.detailed_status == "небольшая облачность":weaterStatus = "небольшая облачность ☁"
		elif w.detailed_status == "пасмурно":weaterStatus = "пасмурно ☁"
		elif w.detailed_status == "плотный туман":weaterStatus = "плотный туман 🌫"
		elif w.detailed_status == "ясно":weaterStatus = "ясно ☀"
		elif w.detailed_status == " облачно с прояснениями":weaterStatus = " облачно с прояснениями ⛅"
		else: weaterStatus = w.detailed_status

		sender(id, "Погода в указанном городе: " + observation.location.name + "\n" +
				"Погодные условия: " + weaterStatus + "\n" +
				"💨 Ветер: " + str(w.wind()['speed']) + " м/с" + ", " + windLine + "\n" +
				"💦 Влажность: " + str(w.humidity) + " %" + "\n" +
				"🌡 Температура: " + str(round(kelvin_to_celsius(w.temp['temp']))) + " ℃" + " Ощущается как: " + str(
				round(kelvin_to_celsius(w.temp['feels_like']))) + " ℃" + "\n" +
				"🌡↑ Температура днем: " + str(round(kelvin_to_celsius(w.temp['temp_max']))) + " ℃" + "\n" +
				"🌡↓ Температура ночью: " + str(round(kelvin_to_celsius(w.temp['temp_min']))) + " ℃")
	except: sender(id, "Что-то пошло не так, попробуйте еще раз.")

def check_user(id):
	if c.execute("SELECT id FROM Users WHERE id=%s"%id).fetchone() is None:
		c.execute('INSERT INTO Users(id,state) VALUES(%d,"Студент")'%id)
		bd.commit()

def check_group(id):
	if c.execute('SELECT groups FROM Users WHERE id=%s'%id).fetchone()[0] is None:
		sender(id, 'Необходимо указать №группы - Группа №группы.')
		return False
	return c.execute('SELECT groups FROM Users WHERE id=%s'%id).fetchone()[0]

def check_thread(id):
	if c.execute('SELECT thread FROM Users WHERE id=%s'%id).fetchone()[0] is None:
		return False
	return c.execute('SELECT thread FROM Users WHERE id=%s'%id).fetchone()[0]

def check_pg(id):
	if c.execute('SELECT pg FROM Users WHERE id=%s'%id).fetchone()[0] is None:
		return "?"
	return c.execute('SELECT pg FROM Users WHERE id=%s'%id).fetchone()[0]

def check_state(id):
	if c.execute('SELECT state FROM Users WHERE id=%s'%id).fetchone()[0]=='Куратор' or c.execute('SELECT state FROM Users WHERE id=%s'%id).fetchone()[0]=='Староста':
		return True
	return False

def check_admin(iid):
	for ids in session_api.messages.getConversationMembers(peer_id = peer_id)["items"]:
		if ids["member_id"] == iid:
			admin = ids.get('is_admin', False)
			if admin == True:return True
			return False

def kick(id,iid):
	session_api.messages.removeChatUser(chat_id=event.chat_id,user_id=iid,random_id=0)
	FIO(iid)
	sender(id, f'@id{iid}({fullname}) был кикнут с беседы')

def check_student(id,iid):
	FIO(iid)
	if id==iid:
		sender(id, f"{name}, твои данные:\nДолжность: {c.execute('SELECT state FROM Users WHERE id=%s'%id).fetchone()[0]}\nГруппа: {check_group(id)}\nПодгруппа: {check_pg(id)}\nПоток: {c.execute('SELECT thread FROM Users WHERE id=%s'%id).fetchone()[0]}")
	else:
		sender(id, f"Данные пользователя {fullname}:\nДолжность: {c.execute('SELECT state FROM Users WHERE id=%s'%iid).fetchone()[0]}\nГруппа: {check_group(iid)}\nПодгруппа: {check_pg(iid)}\nПоток: {c.execute('SELECT thread FROM Users WHERE id=%s'%iid).fetchone()[0]}")

def group(id):
	group=c.execute('SELECT groups FROM Users WHERE id=%s'%id).fetchone()[0]
	ids=[]
	for id in c.execute('SELECT id FROM Users WHERE groups="%s"'%group).fetchall():
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
					sender(id, 'Напишите: Группа №группы, для начала работы с ботом')
				elif msg == 'инфо':
					randVK=vkDict[random.randrange(1,6)]
					FIO(randVK)
					#для админов беседы, куратора и старосты
					if access==True:sender(id, 'Расписание - выводит полное расписание на неделю\nПары - выводит пары на текущий день\nЗвонки - выводит расписание звонков\nГруппа №группы - изменить № группы\nНеделя - выводит текущую неделю(ЧЕТНАЯ, НЕЧЕТНАЯ)\nСтатус - выведет информацию о Вас\nКик @id? - исключить пользователя из беседы\nСтуденты - вывести список группы\nСтудент @id? - вывести информацию о пользователе\nПогода - погода в городе\nОстались вопросы? Пишите: vk.com/%s'%randVK)
					#для студентов
					else:sender(id, 'Расписание - выводит полное расписание на неделю\nПары - выводит пары на текущий день\nЗвонки - выводит расписание звонков\nГруппа №группы - изменить № группы\nНеделя - выводит текущую неделю(ЧЕТНАЯ, НЕЧЕТНАЯ)\nСтатус - выведет информацию о Вас\nПогода - погода в городе\nОстались вопросы? Пишите: vk.com/%s'%randVK)
				elif msg=="неделя":
					sender(id, week())
				elif msg == "звонки"or msg=='🔔 звонки':
					group=check_group(id)
					if group!=False:
						thread=check_thread(id)
						if thread!=False:
							sender(id, c.execute('SELECT bells FROM Threads WHERE thread="%s"'%thread).fetchone()[0])
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
								text=c.execute('SELECT "All" FROM Schedule WHERE groups="%s"'%group).fetchone()[0]
								sender(id, f'[{group}-{pg}] Расписание на сегодня:\n{text.split(weekdays[nowDay])[1].split(f"{week()}{pg}")[1]}')
							else:
								sender(id, 'Необходимо указать свою подгруппу\nПг №подгруппы')
				elif msg == "расписание" or msg=='🗓 расписание':
					group=check_group(id)
					if group!=False:
						pg=check_pg(id)
						if pg!='?':
							text=c.execute('SELECT "All" FROM Schedule WHERE groups="%s"'%group).fetchone()[0]
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
								c.execute('UPDATE Users SET groups="%s" WHERE id=%s'%(msg.split()[1].upper(),id))
								if msg.split()[1].find('исп1')>=0 or msg.split()[1].find('исп2')>=0:
									thread=1
								else:
									thread=2
								c.execute('UPDATE Users SET thread=%s WHERE id=%s'%(thread,id))
								bd.commit()
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
						c.execute('UPDATE Users SET state="Куратор" WHERE id=%d'%int(msg.split()[1].replace('[id',"").split('|')[0]))
						bd.commit()
						FIO(int(msg.split()[1].replace('[id',"").split('|')[0]))
						sender(id, 'Пользователю @id%s(%s) присвоена должность "Куратор"'%(msg.split()[1].replace('[id',"").split('|')[0],fullname))
					except:sender(id, 'Не найден ID пользователя')
				elif msg.split()[0]=='староста' and access==True:
					try:
						c.execute('UPDATE Users SET state="Староста" WHERE id=%d'%int(msg.split()[1].replace('[id',"").split('|')[0]))
						bd.commit()
						FIO(int(msg.split()[1].replace('[id',"").split('|')[0]))
						sender(id, 'Пользователю @id%s(%s) присвоена должность "Староста"'%(msg.split()[1].replace('[id',"").split('|')[0],fullname))
					except:sender(id, 'Не найден ID пользователя')
				elif msg.split()[0]=='пг':
					try:
						if msg.split()[1]=="1" or msg.split()[1]=="2":
							c.execute('UPDATE Users SET pg=%s WHERE id=%s'%(msg.split()[1],id))
							bd.commit()
							sender(id, 'Вы успешно записаны в подгруппу %s'%msg.split()[1])
						else:sender(id, 'Доступные подгруппы - 1, 2')
					except:sender(id, 'Доступные подгруппы - 1, 2')
				elif msg.split()[0]=='студент' and (access==True or check_state(id))==True:
					try:check_student(id,int(msg.split()[1].replace('[id',"").split('|')[0]))
					except:sender(id, 'Не найден ID пользователя')
				elif msg.split()[0]=='студенты' and (access==True or check_state(id)==True):group(id)
except Exception as e:print(e)				