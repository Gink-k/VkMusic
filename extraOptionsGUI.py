import os
from tkinter import (Toplevel, Canvas, Button, Checkbutton, IntVar)
from tkinter.messagebox import showerror
from tkinter.filedialog import askdirectory
from PIL.ImageTk import PhotoImage
from config import resFileName

class ExtraOptionsGUI(Toplevel):
	def __init__(self, parent=None, myBtn=Button, extraParams={}, maxSize=(300, 200), **options):
		Toplevel.__init__(self, parent, **options)
		fname = os.path.join(resFileName, 'extra_bg2.jpg')
	
		self.extraParams = extraParams
		self.bg_image = PhotoImage(file=fname)
		
		canvas = Canvas(self, width=maxSize[0], height=maxSize[1], highlightthickness=0)
		canvas.pack(side='top', fill='both', expand='yes')
		canvas.create_image(0, 0, image=self.bg_image, anchor='nw')
		
		self.mkDirVar = IntVar()
		mkDirChBtn = Checkbutton(canvas, 
								text='', 
								variable=self.mkDirVar, command=self.setMkDirParams)
		mkDirChBtn.pack()
		canvas.create_window(40, 50, window=mkDirChBtn)
		canvas.create_text(125, 50, font=("Times", 11), text='Создать папку "Music"')
		
		self.reverseVar = IntVar()
		reverseChBtn = Checkbutton(canvas, 
								text='', 
								variable=self.reverseVar, command=self.setReverseParams)
		reverseChBtn.pack()
		canvas.create_window(40, 90, window=reverseChBtn)
		canvas.create_text(175, 90, font=("Times", 11), text='Реверсировать выделение композиций')
	
		dirBtn = myBtn(canvas, text='Папка для закачки', command=self.setDirectory)
		dirBtn.pack()
		canvas.create_window(100, 170, height=30, window=dirBtn)
		
		qBtn = myBtn(canvas, text='ок', command=self.destroy)
		qBtn.pack()
		canvas.create_window(250, 170, height=30, width=40, window=qBtn)
		
		self.setInitSetting()
		
		self.grab_set()
		self.focus_set()
		self.wait_window()
		
	def setInitSetting(self):
		if self.extraParams['mkDir']:
			self.mkDirVar.set(1)
		if self.extraParams['reverse']:
			self.reverseVar.set(1)
	
	def setMkDirParams(self):
		self.extraParams['mkDir'] = self.mkDirVar.get()

	def setReverseParams(self):
		self.extraParams['reverse'] = self.reverseVar.get()
		
	def setDirectory(self):
		dir = askdirectory()
		if dir:
			self.extraParams['dir'] = dir
