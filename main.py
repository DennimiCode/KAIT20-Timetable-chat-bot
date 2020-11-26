#Импорты всез библиотек
from datetime import datetime, date, time
import vk_api, random
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import sqlite3
import requests
import json
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


keyboard = {
	"one_time": False,
	"buttons": [
		[get_but('Расписание', 'positive'), get_but('Пары', 'positive')],
		[get_but('Звонки', 'positive'), get_but('Группа', 'positive')]
	]
}
keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))

bd = sqlite3.connect('data.db')
c = bd.cursor()

vkDict = {"xvanche":1, "fraybyl":2, "dennimi":3, "id219093647":4, "1nigm4":5} 

def admin():
	global randVK
	randomNum =  random.randrange(1,6)
	for key in vkDict:
		if vkDict[key] == randomNum:
			randVK = key

nowDay = datetime.today().isoweekday() 
nowWeek = requests.get("https://my-calend.ru/week-number").text.split(' неделя года')[0].split("<h2>")[1]
if int(nowWeek)%2==0:
	nowWeek='ЧЕТНАЯ'
else:
	nowWeek='НЕЧЕТНАЯ'

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

def check_user(id):
	if c.execute("SELECT id FROM Users WHERE id=%s"%id).fetchone() is None:
		c.execute('INSERT INTO Users(id) VALUES(%d)'%id)
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
		return ""
	return c.execute('SELECT pg FROM Users WHERE id=%s'%id).fetchone()[0]

def kick(id):
	session_api.messages.removeChatUser(chat_id=event.chat_id,user_id=id,random_id=0)
	FIO(id)
	sender(id, f'@id{id}({fullname}) был кикнут с беседы')

def check_student(id):
	FIO(id)
	sender(id, f"@id{id}({name}), твои данные:\nГруппа: {check_group(id)}\nПодгруппа: {check_pg(id)}\nПоток: {c.execute('SELECT thread FROM Users WHERE id=%s'%id).fetchone()[0]}")

def group(group):
	ids=[]
	for id in c.execute('SELECT id FROM Users WHERE groups="%s"'%group).fetchall():
		ids.append(id[0])
	text=''
	n=1
	for id in ids:
		FIO(id)
		pd=check_pg(id)
		if pd!='':text=text+f'{n}. @id{id}({fullname}) [{pd}]\n'
		else:text=text+f'{n}. @id{id}({fullname})\n'
		n=n+1
	sender(id, text)

def FIO(id):
	global name,lastname,fullname
	name=session_api.users.get(user_ids = id)[0]['first_name']
	lastname=session_api.users.get(user_ids = id)[0]['last_name']
	fullname=f'{str(name)} {str(lastname)}'

for event in longpoll.listen():
	if event.type == VkBotEventType.MESSAGE_NEW:
		msg=str(event).split(', ')[6].split("'")[3].lower()
		if msg!='':
			peer_id=''
			chat_key=session_api.groups.getLongPollServer(group_id=200587301)['key']
			chat_server=session_api.groups.getLongPollServer(group_id=200587301)['server']
			chat_ts=session_api.groups.getLongPollServer(group_id=200587301)['ts']
			peer_id=int(str(event).split(', ')[5].split(': ')[1])
			id = int(str(event).split(", ")[2].split(": ")[1])
			check_user(id)
			if id==249827478 or id==551011530 or id==168670483 or id==167498582 or id==219093647:access=True
			else: access=False
			FIO(id)
			print(f'[{name} {lastname}] {msg}')
			if msg.find("[club")>=0:
				msg=msg.split()[1]
			if msg == 'я':
				check_student(id)
			elif msg == 'начать':
				sender(id, 'Напишите: Группа №группы, для начала работы с ботом')
			elif msg == 'инфо':
				admin()
				FIO(randVK)
				sender(id, 'Расписание - выводит полное расписание на неделю\nПары - выводит пары на текущий день\nЗвонки - выводит расписание звонков\nГруппа №группы - изменить № группы\nИнфо - выводит помощь по доступным командам\nНеделя - выводит текущую неделю(ЧЕТНАЯ, НЕЧЕТНАЯ)\nЯ - выведет информацию о Вас\nОстались вопросы? Пишите: @%s(%s)'%(randVK,fullname))
			elif msg=="неделя":
				sender(id, nowWeek)
			elif msg == "звонки":
				group=check_group(id)
				if group!=False:
					sender(id, str(c.execute('SELECT thread FROM Threads WHERE groups="%s"'%group).fetchone()).split("'")[1].replace('/n','\n'))
			elif msg == "пары":
				group=check_group(id)
				if group!=False:
					spliter=f'-{nowWeek}{c.execute("SELECT pg FROM Users WHERE id=%s"%id).fetchone()[0]}'
					sender(id, str(c.execute('SELECT "%s" FROM Schedule WHERE groups="%s"'%(nowDay,group)).fetchone()).split(spliter)[1].replace("/n","\n"))
			elif msg == "расписание":
				group=check_group(id)
				if group!=False:
					spliter=f'-{nowWeek}{c.execute("SELECT pg FROM Users WHERE id=%s"%id).fetchone()[0]}'
					sender(id, str(c.execute('SELECT "all" FROM Schedule WHERE groups="%s"'%group).fetchone()).split(spliter)[1].replace("/n","\n"))
			elif msg.split()[0] == "группа":
				try:
					if msg.split()[1]!='исп211' and msg.split()[1]!='исп251д':
						sender(id, 'Доступные группы: ИСП211, ИСП251Д')
					else:
						c.execute('UPDATE Users SET groups="%s" WHERE id=%s'%(msg.split()[1].upper(),id))
						c.execute('UPDATE Users SET thread=1 WHERE id=%s'%id)
						bd.commit()
						sender(id, f'Теперь Вы участник группы {msg.split()[1].upper()}')
				except:sender(id, 'Доступные группы: ИСП211, ИСП251Д')
			elif msg.split()[0]=='кик' and access==True:
				try:
					kick(int(msg.split()[1].replace('[id',"").split('|')[0]))
				except:sender(id, 'Ошибка, id не найден')
			elif msg.split()[0]=='пг':
				try:
					if msg.split()[1]=="1" or msg.split()[1]=="2":
						c.execute('UPDATE Users SET pg=%s WHERE id=%s'%(msg.split()[1],id))
						bd.commit()
						sender(id, 'Вы успешно записаны в подгруппу %s'%msg.split()[1])
					else:sender(id, 'Доступные подгруппы - 1, 2')
				except:sender(id, 'Доступные подгруппы - 1, 2')
			elif msg.split()[0]=='студент' and access==True:
				try:
					check_student(int(msg.split()[1].replace('[id',"").split('|')[0]))
				except:sender(id, 'Ошибка, id не найден')
			elif msg.split()[0]=='студенты' and access==True:
				try:
					group(msg.split()[1].upper())
				except:pass