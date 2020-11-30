# coding=UTF-8
import datetime
import vk_api, random
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import sqlite3
import requests
import json
from tokens import Your_VKToken
from kaitbot import KaitBot

database = sqlite3.connect('data.db')
cursor = database.cursor()

my_token = Your_VKToken

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
	"one_time": True,
	"buttons": [
		[get_but('🗓 Расписание', 'default'), get_but('🗒 Пары', 'default')],
		[get_but('🔔 Звонки', 'default'), get_but('🌡 Погода', 'default')]
	]
}
keyboard = str(json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode('utf-8'))

def follow_message(id, text):
	try:
		session_api.messages.send(
			key = chatSettings['chat_key'],
			server = chatSettings['chat_server'],
			ts = chatSettings['chat_ts'],
			message = text,
			chat_id = event.chat_id,
			random_id = get_random_id(),
			keyboard = keyboard
		)
	except:
		if peer_id == id: session_api.messages.send(peer_id = peer_id,message = text,random_id = 0, keyboard = keyboard)
		else: vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'random_id' : 0, 'keyboard': keyboard})

chatSettings={}

for event in longpoll.listen():
	try:
		if event.type == VkBotEventType.MESSAGE_NEW:
			msg = event.object.message['text'].lower()
			if msg != '':
				chat = session_api.groups.getLongPollServer(group_id=200587301)
				chatSettings['chat_key'] = chat['key']
				chatSettings['chat_server'] = chat['server']
				chatSettings['chat_ts'] = chat['ts']
				chatSettings['chat_id'] = event.chat_id
				peer_id = event.object.message['peer_id']
				id = event.object.message['from_id']

				bot = KaitBot(id,session_api,peer_id,chatSettings['chat_id'])

				if msg.find("[club") >= 0:
					msg = msg.split()
					del(msg[0])
					msg=' '.join(msg)
				if msg.find('🔔')>=0 or msg.find('🗒')>=0 or msg.find('🗓')>=0 or msg.find('🌡')>=0:
					msg=msg.split()[1]

				answer=bot.new_message(msg)
				if answer!=False:
					follow_message(id, answer)

	except Exception as e:print(e)