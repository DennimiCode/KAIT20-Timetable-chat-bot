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
import time
import asyncio

class Kait:

	def __init__(self):
		self.vk_session = vk_api.VkApi(token = Your_VKToken)
		self.session_api = self.vk_session.get_api()
		self.longpoll = VkBotLongPoll(self.vk_session, '200587301')

		keyboard = {
			"one_time": True,
			"buttons": [
				[self.get_but('🗓 Расписание', 'default'), self.get_but('🗒 Пары', 'default')],
				[self.get_but('🔔 Звонки', 'default'), self.get_but('🌡 Погода', 'default')]
			]
		}
		self.keyboard = str(json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode('utf-8'))
		asyncio.run(self.main())


	async def main(self):
		task1 = asyncio.create_task(self.check_events())
		task2 = asyncio.create_task(self.check_notifications())

		await asyncio.gather(task1,task2)

	async def check_notifications(self):
		timer=time.time()-100
		while True:
			now = time.time()
			if (now-timer>=60):
				Bot = KaitBot(None,None,None,None)
				result=Bot.notifications(self.vk_session)
				if result==True: timer=time.time()
				else: timer=time.time()-40
			await asyncio.sleep(0.1)

	async def check_events(self):
		chat = self.session_api.groups.getLongPollServer(group_id=200587301)
		ready_events=[]
		while True:
			for event in requests.get('{}?act=a_check&key={}&ts={}&mode=2&version=2'.format(chat['server'],chat['key'],chat['ts'])).json()['updates']:
				if not event in ready_events: 
					if event['type'] == 'message_new':
						self.new_message_event(event)
					ready_events.append(event)
				if len(ready_events)>25:
					chat = self.session_api.groups.getLongPollServer(group_id=200587301)
					ready_events=[]
			await asyncio.sleep(0.1)

	def follow_message(self,text):
		if not self.chat_id is None:
			self.session_api.messages.send(
				message = text,
				chat_id = self.chat_id,
				random_id = get_random_id(),
				keyboard = self.keyboard
			)
		elif self.peer_id == id: 
			self.session_api.messages.send(
				peer_id = self.peer_id,
				message = text,
				random_id = 0, 
				keyboard = self.keyboard
			)
		else: 
			self.vk_session.method(
				'messages.send', 
				{'user_id' : self.user_id, 
				'message' : text, 
				'random_id' : 0, 
				'keyboard': self.keyboard}
			)

	def new_message_event(self,event):
		self.user_id = event['object']['message']['from_id']
		self.peer_id = event['object']['message']['peer_id']
		msg = event['object']['message']['text'].lower()

		if str(self.peer_id)[0]=='2': self.chat_id = self.peer_id - 2000000000
		else: self.chat_id = None

		Bot = KaitBot(self.user_id,self.session_api,self.peer_id,self.chat_id)

		#Убираем лишние символы, приводя сообщение к доступному виду
		if msg.find("[club") >= 0:
			msg = msg.split()
			del(msg[0])
			msg=' '.join(msg)
		if msg.find('🔔')>=0 or msg.find('🗒')>=0 or msg.find('🗓')>=0 or msg.find('🌡')>=0:
			msg=msg.split()[1]

		answer=Bot.new_message(msg)
		if answer!=False:
			self.follow_message(answer)

	def get_but(self,text,color):
		return {
			"action": {
				"type": "text",
				"payload": "{\"button\": \"" + "1" + "\"}",
				"label": f"{text}"
			},
			"color": f"{color}"
		}

Kait()