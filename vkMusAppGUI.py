import os, requests, time, threading
import tkinter.ttk as ttk
from tkinter import (Frame, Toplevel, Canvas, Button, 
						Entry, RIDGE, mainloop, TclError, 
							END, Scrollbar, Listbox, Radiobutton, 
								RIGHT, LEFT, Y, YES, BOTH, ACTIVE, StringVar)
from authGUI import AuthGUI
from vkMusApp import VkMusic
from PIL import Image
from io import BytesIO
from PIL.ImageTk import PhotoImage # <== required for JPEG display
from tkinter.messagebox import showerror, askyesno, showinfo
from extraOptionsGUI import ExtraOptionsGUI
from config import resFileName, cacheFileName

class VkMusAppGUI(Frame):
	def __init__(self, parent=None, **options):
		Frame.__init__(self, parent, **options)
		self.vk = VkMusic()
		self.authResult = []
		self.makeAuthWidgets()
		self.myAfter()

		self.userMusic = [[]]
		self.findedMusic = [[]]
		self.threadInWork = 0
		self.inSearchPlayList = False
		self.lastEntryName = None
		self.extraParams = {'dir': os.path.curdir, 
							'mkDir': False, 
							'reverse': False}

	def myAfter(self, time=1000):
		self.win.after(time, self.makeWidgets)
		
	def makeWidgets(self):
		try:
			if self.authResult[0]:
				maxSize = (820, 500)
				fname = os.path.join(resFileName, 'bg3.jpg')
				self.master.title('Music')
				self.master.geometry('%dx%d' % maxSize)
				self.master.maxsize(*maxSize)
				self.master.iconbitmap(os.path.join(resFileName, 'icon2.ico'))
				self.master.protocol("WM_DELETE_WINDOW", self.delCache)
				
				canvas = self.win.canvas
				canvas.delete("all")
				self.bg_image = PhotoImage(file=fname)
				canvas.create_image(0, 0, image=self.bg_image, anchor='nw')
				
				userInfo = self.vk.getUserInfo()
				userName = userInfo['first_name'] + ' ' + userInfo['last_name']
				userPhotoURL = self.vk.getUserPhoto()
				userImage = requests.get(userPhotoURL).content
				userImage = Image.open(BytesIO(userImage))
				self.userImage = PhotoImage(userImage)
				imageX = (200 - self.userImage.width()) / 2
				imageY = 70
				userNameY = self.userImage.height() + imageY + 10
				canvas.create_image(imageX, imageY, image=self.userImage, anchor='nw')
				canvas.create_text(imageX, userNameY, fill='white', text=userName, anchor='nw')
			
				playBtnFile = os.path.join(resFileName, 'play.png')
				self.playButtonImage = PhotoImage(file=playBtnFile)
				playButton = Button(canvas, image=self.playButtonImage, 
												bg='#3c3c3c', command=self.playMusic)
				playButton.pack()
				canvas.create_window(50, 300, width=30, height=30, window=playButton)
				self.currentSongText = canvas.create_text(70, 300, fill='white', anchor='w', text='Текущая композиция')

				lFrame = Frame(canvas)
				lFrame.pack()
				canvas.create_window(400, 200, width=400, height=300, window=lFrame)
				
				sbar = Scrollbar(lFrame)
				listbox = Listbox(lFrame, selectmode='EXTENDED', exportselection=False)
				sbar.config(command=listbox.yview)      # связать sbar и list        
				listbox.config(yscrollcommand=sbar.set) # сдвиг одного = сдвиг другого 
				listbox.bind('<<ListboxSelect>>', self.showLastSelectSong)
				sbar.pack(side=RIGHT, fill=Y)        # первым добавлен – посл. обрезан        
				listbox.pack(side=LEFT, expand=YES, fill=BOTH) # список обрезается первым
				self.list = listbox
								
				self.var = StringVar()
				self.radioVal = ('playlist', 'search')
				
				playlist = Radiobutton(canvas, 
										#command=self.getPlaylist, 
											bg='#3c3c3c', 
												variable=self.var, 
													value=self.radioVal[0])
				search = Radiobutton(canvas, 
										#command=self.getMusic,
											bg='#3c3c3c', 
												variable=self.var, 
													value=self.radioVal[1])
				playlist.pack(), search.pack()
				canvas.create_window(660, 65, window=playlist)
				canvas.create_window(660, 105, window=search)
				canvas.create_text(720, 65, fill='white', text='Мой плейлист')
				canvas.create_text(700, 105, fill='white', text='Искать')
				
				canvas.create_text(692, 145, fill='white', text='Название песни')
				songNameEntry = Entry(canvas)
				songNameEntry.pack()
				canvas.create_window(710, 165, window=songNameEntry)
				self.songNameEntry = songNameEntry
				self.master.bind('<Return>', lambda event: self.showMuscicList())
				
				canvas.create_text(705, 200, fill='white', text='Номера композиций')
				numEntry = Entry(canvas)
				numEntry.pack()
				canvas.create_window(710, 220, window=numEntry)
				numEntry.bind('<KeyPress>', self.selectMultipleItems)
				self.numEntry = numEntry
				
				resBtn = Button(canvas, text='Найти', 
									command=self.showMuscicList)
									
				dwlBtn = Button(canvas, text='Скачать', 
									command=self.downloadMusic)
									
				extraOptBtn = Button(canvas, text='Доп. параметры', 
									command=self.showExtraOpts)
				
				resBtn.pack(), dwlBtn.pack(), extraOptBtn.pack()
				canvas.create_window(675, 260, width=60, window=resBtn)
				canvas.create_window(745, 260, width=60, window=dwlBtn)
				canvas.create_window(710, 300, height=35, width=130, window=extraOptBtn)
				
				progressbar = ttk.Progressbar (canvas, mode="determinate")
				progressbar.pack()
				canvas.create_window(400, 400, width=400, window=progressbar)
				self.progressbar = progressbar
				
				generalProgressbar = ttk.Progressbar (canvas, mode="determinate")
				generalProgressbar.pack()
				canvas.create_window(400, 450, width=400, window=generalProgressbar)
				self.generalProgressbar = generalProgressbar
				
				self.songNumInfo = canvas.create_text(200, 35, fill='white', anchor='w', text='')
		
				self.canvas = canvas
			
			##### Show playlist at start #####
				self.showPlayList()
			##################################

			else:
				showerror('Ошибка', 'Авторизация не удалась!')
				del self.authResult[0]
				self.myAfter()
		except IndexError: 
			self.myAfter()
	
	def makeAuthWidgets(self):
		self.win = AuthGUI(act=self.vk.authVk, result=self.authResult)
	
	def showExtraOpts(self):
		ExtraOptionsGUI(self, extraParams=self.extraParams)
		if self.extraParams['reverse']:
			self.list.select_set(0, END)
		if self.extraParams['mkDir']:
			self.makeDir()

	def delCache(self):
		for fileName in os.listdir(cacheFileName):
			path = os.path.join(cacheFileName, fileName)
			os.remove(path)
		self.quit()

	def makeThread(self, func, args):
		th = threading.Thread(target=func, args=args)
		th.daemon = True
		th.start()
			
	def getPlaylist(self):
		self.makeThread(self.vk.getUserMusic, (self.userMusic,))
	
	def getMusic(self):
		if self.songNameEntry.get(): 
			name = self.songNameEntry.get()
			self.makeThread(self.vk.getMusic, (name, self.findedMusic))
			self.lastEntryName = name
		else:
			showinfo('Ошибка!', 'Введите название песни!')

	def selectMultipleItems(self, event):
		def listIteration(somelist, func):
			for pos in somelist:
				try:
					if '-' in pos:
						first = pos[ : pos.find('-')]
						last = pos[pos.find('-')+1:]
						func(first, last)
					else:
						func(pos)
				except (TclError): pass

		def clearExtraSelections(selection, func):
			if hasattr(self, 'lastSelection'):
				extra = set(self.lastSelection) - set(selection)
				listIteration(extra, func) #self.list.select_clear
			self.lastSelection = selection
		
		if event.char.isprintable():
			selection = self.numEntry.get() + event.char
			selection = selection.replace(' ', '').split(',')
		elif event.char == '\x08':
			selection = self.numEntry.get()[:-1].replace(' ', '').split(',')
		else:
			selection = self.numEntry.get().replace(' ', '').split(',')
		
		func = (self.list.select_set, self.list.select_clear) if self.extraParams['reverse'] else (self.list.select_clear, self.list.select_set)
			
		clearExtraSelections(selection, func[0])
		
		listIteration(selection, func[1])

	def	showMuscicList(self):
		self.list.delete(0, 'end')
		self.threadInWork += 1
		
		def prText(song, i):
			text = '{:>03}. {} - {}    {}'
			duration = str(song['duration'] // 60) + ':' + str(song['duration'] % 60) 		
			return text.format(i, song['artist'], song['title'], duration)
		
		def startWork(musicL):
			self.songInfo = []
			with threading.Lock():
				i = 0
				for song in musicL:
					if self.threadInWork > 1:
						self.threadInWork -= 1
						return
					text = prText(song, i)
					try:
						self.list.insert(i, text)
						fname = song['artist'] + ' - ' + song['title'] + '.mp3'
						for pos in r'\/:><*?"|':
							fname = fname.replace(pos, '_')
						self.songInfo.append({'name': fname, 'url': song['url']})
					except TclError: pass
					else:
						i+=1
				self.canvas.itemconfig(self.songNumInfo, text=('Найдено %d композиций'%i))
				self.threadInWork -= 1
				if self.extraParams['reverse']:
					self.list.select_set(0, END) 

		def threadShowMusic(musicL):
			if musicL[0]:
				self.makeThread(startWork, (musicL[0], ))
			else:
				self.after(500, threadShowMusic, musicL)

		if self.var.get() == self.radioVal[0]:
			if not self.userMusic[0] and not self.inSearchPlayList:
				self.inSearchPlayList = True
				self.getPlaylist()
			threadShowMusic(self.userMusic)
			self.canvas.itemconfig(self.songNumInfo, text='Загружаем плейлист...')
		elif self.var.get() == self.radioVal[1]:
			if self.lastEntryName != self.songNameEntry.get():
				self.findedMusic[0] = []
				self.getMusic()
			threadShowMusic(self.findedMusic)
			self.canvas.itemconfig(self.songNumInfo, text='Идет поиск...')
		else:
			showinfo('Ошибка', 'Выберите категорию!')

		self.threadInWork -= 1
	
	def showPlayList(self):
		self.var.set('playlist')
		self.showMuscicList()

	def showLastSelectSong(self, event):
		try:
			num = self.list.curselection()[-1]
			song = self.songInfo[num]['name'] 
			song = song if len(song) < 22 else (song[:18] + '...')  
			self.canvas.itemconfig(self.currentSongText, text=song)
		except AttributeError: 
			pass

	def playMusic(self):
		try:
			num = self.list.curselection()[-1]
			song = self.songInfo[num]['name']
			file = os.path.join(cacheFileName, song)

			if not os.path.exists(cacheFileName):
				os.mkdir(cacheFileName)

			if not song in os.listdir(cacheFileName):
				with requests.get(self.songInfo[num]['url'], stream=True) as response:
					content = b''
					for chunk in response.iter_content(1024*50):
						content +=chunk
				with open(file, "wb") as f:
					f.write(content)
			
			cmdline = '"%s"'%file
			os.system(cmdline)
		except Exception: showerror('Ошибка', 'Не удалось воспроизвести композицию!')

	def makeDir(self):
		newdir = os.path.join(self.extraParams['dir'], 'Music')
		if not os.path.exists(newdir):
			os.mkdir(newdir)
			self.extraParams['dir'] = newdir
		elif askyesno('Внимание!', 'Папка "Music" уже была создана ранее.\nИспользовать ее?'):
			self.extraParams['dir'] = newdir
		
	def downloadMusic(self):
		def threadDwnl():
			curSelect = self.list.curselection()
			curSelectLen = len(curSelect)
			self.generalProgressbar['maximum'] = curSelectLen
			count = 0
			totalText = 'Закачено: %03d из %03d'
			totalDownload = self.canvas.create_text(200, 430, fill='white', tag='total', anchor='w', text=totalText%(count, curSelectLen))
			for num in curSelect:
				num = int(num)
				if not self.songInfo[num]['name'] in os.listdir(self.extraParams['dir']):
					file = os.path.join(self.extraParams['dir'], self.songInfo[num]['name'])
					text = self.songInfo[num]['name']+'...' 
					self.canvas.create_text(200, 375, fill='white', tag='fileLabel', anchor='w', text=text)
					with requests.get(self.songInfo[num]['url'], stream=True) as response:
						content = b''
						maxValue = response.headers['content-length']
						self.progressbar['maximum'] = maxValue
						for chunk in response.iter_content(1024*50):
							self.progressbar['value']+=len(chunk)
							content +=chunk
						self.progressbar['value'] = 0
						self.canvas.delete('fileLabel')
					with open(file, "wb") as file:
						file.write(content)
				count +=1
				self.canvas.itemconfig(totalDownload, text=totalText%(count, curSelectLen))
				self.generalProgressbar['value'] = count
			self.generalProgressbar['value'] = 0
			self.canvas.delete('total')
			
			showinfo('Успех!', 'Загрузка завершена.')
		
		self.makeThread(threadDwnl, ())
		
if __name__ == '__main__':
	app = VkMusAppGUI(relief=RIDGE)
	mainloop()