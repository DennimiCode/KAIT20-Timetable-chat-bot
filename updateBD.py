from openpyxl import load_workbook
import sqlite3

bd=sqlite3.connect('data.db')
c=bd.cursor()

wb = load_workbook('Data/Junior.xlsx')
sheet = wb['Page 1']
mergeds=str(sheet.merged_cells.ranges)

def scheduler():
	# y - строка в таблице, с которой начинаются пары
	# x - столбец в таблицу
	global weekdayn
	if weekday=='Понедельник':
		y=12
		weekdayn=1
	elif weekday=='Вторник':
		y=23
		weekdayn=2
	elif weekday=='Среда':
		y=35
		weekdayn=3
	elif weekday=='Четверг':
		y=46
		weekdayn=4
	elif weekday=='Пятница':
		y=58
		weekdayn=5
	end=y+10
	if group=='ИСП111':x='D'
	elif group=='ИСП131':x='F'
	elif group=='ИСП111Д':x='H'
	elif group=='ИСП131Д':x='J'
	elif group=='ИСП121':x='L'
	elif group=='ИСП211':x='N'
	elif group=='ИСП251Д':x='P'
	elif group=='ИСП211Д':x='R'
	elif group=='ИСП231Д':x='T'
	elif group=='ИСП221':x='V'
	elif group=='ИСП241':x='X'
	elif group=='П311':x='Z'
	elif group=='П331':x='AB'
	elif group=='ПВ311':x='AD'
	elif group=='ПВ351':x='AF'
	elif group=='П321':x='AH'
	elif group=='П411':x='AJ'
	elif group=='ПИВ411':x='AL'
	schedule=[]
	while y!=end:
		try:
			text=sheet[f'{x}{y}'].value
			if weekdayn==1 or weekdayn==4 or weekdayn==5:
				if text is None:
					if y%2>=1:
						if mergeds.find(f'{x}{y-1}:{x}{y}')>=0:
							text=sheet[f'{x}{y-1}'].value
						else:
							text=''
					else:
						text=''
			else:
				if text is None:
					if y%2==0:
						if mergeds.find(f'{x}{y-1}:{x}{y}')>=0:
							text=sheet[f'{x}{y-1}'].value
						else:
							text=''
					else:
						text=''
			if text.find('None')>=0:
				text.replace('None','')
			schedule.append(text)
		except:pass
		y=y+1
	n=1
	ch=[]
	nch=[]
	chn=1
	nchn=1
	for text in schedule:
		text=text.replace('\n',' ')
		texts=['','']
		z=0
		if (text.find('1 п/г')>=0 or text.find('1п/г')>=0 or text.find('1 п\\г')>=0 or text.find('1п\\г')>=0) and (text.find('2 п/г')>=0 or text.find('2п/г')>=0 or text.find('2 п\\г')>=0 or text.find('2п\\г')>=0):
			try:
				texts=text.split('2 п/г')
				texts[1]=f'2 п/г {texts[1]}'
			except:
				try:
					texts=text.split('2п/г')
					texts[1]=f'2п/г {texts[1]}'
				except:
					try:
						texts=text.split('2 п\\г')
						texts[1]=f'2 п\\г {texts[1]}'
					except:
						texts=text.split('2п\\г')
						texts[1]=f'2п\\г {texts[1]}'
			double=True
		else:
			texts[1]=text
			z=1
			double=False
		while z!=2:
			pd=''
			if texts[z].find('1 п/г')>=0 or texts[z].find('1п/г')>=0 or texts[z].find('1 п\\г')>=0 or texts[z].find('1п\\г')>=0:pd='[1] '
			elif texts[z].find('2 п/г')>=0 or texts[z].find('2п/г')>=0 or texts[z].find('2 п\\г')>=0 or texts[z].find('2п\\г')>=0:pd='[2] '
			if texts[z].find('Русский язык')>=0:texts[z]=f'{pd}Русский язык'
			elif texts[z].find('ОУД.02')>=0:texts[z]=f'{pd}Литература'
			elif texts[z].find('Иностранный язык')>=0:texts[z]=f'{pd}Английский язык'
			elif texts[z].find('Математика')>=0:texts[z]=f'{pd}Математика'
			elif texts[z].find('История')>=0:texts[z]=f'{pd}История'
			elif texts[z].find('Физическая культура')>=0:texts[z]=f'{pd}Физическая культура'
			elif texts[z].find('Основы безопасности жизнедеятельности')>=0:texts[z]=f'{pd}ОБЖ'
			elif texts[z].find('Информатика')>=0:texts[z]=f'{pd}Информатика'
			elif texts[z].find('Физика')>=0:texts[z]=f'{pd}Физика'
			elif texts[z].find('Химия')>=0:texts[z]=f'{pd}Химия'
			elif texts[z].find('Обществознание')>=0:texts[z]=f'{pd}Обществознание'
			elif texts[z].find('Введение в специальность')>=0:texts[z]=f'{pd}Введение в специальность'
			elif texts[z].find('Индивидуальный проект')>=0:texts[z]=f'{pd}Индивидуальный проект'
			elif texts[z].find('Дискретная математика')>=0:texts[z]=f'{pd}Дискретная математика с ЭМЛ'			
			elif texts[z].find('Элементы')>=0:texts[z]=f'{pd}Элементы высшей математики'
			elif texts[z].find('баз данных')>=0:texts[z]=f'{pd}Основы проектирования БД'
			elif texts[z].find('Информационные')>=0:texts[z]=f'{pd}Информационные технологии'
			elif texts[z].find('алгоритмизации')>=0:texts[z]=f'{pd}ОА и программирования'
			elif texts[z].find('Психология')>=0:texts[z]=f'{pd}Психология и общение'
			elif texts[z].find('Операционные системы')>=0:texts[z]=f'{pd}ОС и среды'
			elif texts[z].find('Компьютерные сети')>=0:texts[z]=f'{pd}Компьютерные сети'
			elif texts[z].find('Поддержка и тестирование')>=0:texts[z]=f'{pd}ПиТПМ'
			elif texts[z].find('Обеспечение качества')>=0:texts[z]=f'{pd}ОКФКС'
			elif texts[z].find('Внедрение и поддержка')>=0:texts[z]=f'{pd}ВиПКС'
			elif texts[z].find('Основы философии')>=0:texts[z]=f'{pd}Основы философии'
			elif texts[z].find('Основы предпринимательской')>=0:texts[z]=f'{pd}Основы ПД'
			elif texts[z].find('Разработка мобильных')>=0:texts[z]=f'{pd}Разработка моб. приложений'
			elif texts[z].find('Технология разрабтки п')>=0:texts[z]=f'{pd}ТРПО'
			elif texts[z].find('Экология отрасли')>=0:texts[z]=f'{pd}Экология отрасли'
			elif texts[z].find('Сопровождение и продвижение')>=0:texts[z]=f'{pd}СиППООН'
			elif texts[z].find('Методы создания документов')>=0:texts[z]=f'{pd}МСДпоСиОПО'
			elif texts[z].find('Технология разрабтки и защиты')>=0:texts[z]=f'{pd}ТРиЗБД'
			elif texts[z].find('Документационное')>=0:texts[z]=f'{pd}ДОУ'
			elif texts[z].find('Менеджмент')>=0:texts[z]=f'{pd}Менеджмент'
			elif texts[z].find('Основы дизайн')>=0:texts[z]=f'{pd}Основы дизайн-проектирования'
			elif texts[z].find('Технология трехмерного')>=0:texts[z]=f'{pd}ТТМиА'
			elif texts[z].find('Обеспечение проектной')>=0:texts[z]=f'{pd}Обеспечение проектной деят.'
			z=z+1
		if double==True:
			texts[1]=f'{chn}. {texts[1]}'
			texts='\n'.join(texts)
		else:
			texts=texts[1]
		if n%2==0:
			ch.append(f'{chn}. {texts}')
			chn=chn+1
		else:
			nch.append(f'{nchn}. {texts}')
			nchn=nchn+1
		n=n+1
	return nch, ch

def check(group):
	if c.execute('SELECT groups FROM Schedule WHERE groups="%s"'%group).fetchone() is None:
		c.execute('INSERT INTO Schedule(groups) VALUES("%s")'%group)
		bd.commit()

def sort(weeks,pg):
	n=0
	week=weeks[:]
	for text in week:
		if pg==1:
			if text.find('[2]')>=0:
				if text.find('\n')>=0:
					week[n]=text.split('\n')[0]
				else:
					week[n]=text.split('[2]')[0]
			if text.find('[1]')>=0:
				week[n]=week[n].replace('[1] ','')
		else:
			if text.find('[1]')>=0:
				if text.find('\n')>=0:
					week[n]=text.split('\n')[1]
				else:
					week[n]=text.split('[1]')[0]
			if text.find('[2]')>=0:
				week[n]=week[n].replace('[2] ','')	
		n=n+1		
	week='\n'.join(week)
	return week

grouplist=['ИСП111','ИСП131','ИСП111Д','ИСП131Д','ИСП121','ИСП211','ИСП251Д','ИСП211Д','ИСП231Д','ИСП231Д','ИСП221','ИСП241','П311','П331','ПВ311','ПВ351','П321','П411','ПИВ411']
weekdays=['Понедельник','Вторник','Среда','Четверг','Пятница']
for group in grouplist:
	alls=[]
	for weekday in weekdays:
		nch, ch = scheduler()
		alls.append(f'{weekday}НЕЧЕТНАЯ1{sort(nch,1)}НЕЧЕТНАЯ1НЕЧЕТНАЯ2{sort(nch,2)}НЕЧЕТНАЯ2ЧЁТНАЯ1{sort(ch,1)}ЧЁТНАЯ1ЧЁТНАЯ2{sort(ch,2)}ЧЁТНАЯ2{weekday}')
	alls=''.join(alls)
	check(group)
	c.execute('UPDATE Schedule SET "All"="%s" WHERE groups="%s"'%(alls,group))
	bd.commit()