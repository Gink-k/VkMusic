import os, threading
from tkinter import Frame, Canvas, Button, Entry, RIDGE, mainloop
from PIL.ImageTk import PhotoImage # <== required for JPEG display
from config import resFileName

class AuthGUI(Frame):
	def __init__(self, parent=None, act=print, result=[], maxSize=(300, 350), **options):
		Frame.__init__(self, parent, **options)
		self.master.title('Авторизация')
		self.master.geometry('%dx%d' % maxSize)
		self.master.maxsize(*maxSize)
		self.pack(fill='both', expand='yes')
		
		self.btnAct = act
		self.result = result
		self.makeWidgets(maxSize)
		
	def makeWidgets(self, maxSize, 
					labeltext=('Логин', 'Пароль'),  
					font=("Times New Roman", 12, "bold"), 
					fname=os.path.join(resFileName, 'bg2.jpg')):	
		
		self.bg_image = PhotoImage(file=fname)
		canvas = Canvas(self, width=maxSize[0], height=maxSize[1], highlightthickness=0)
		canvas.pack(side='top', fill='both', expand='yes')
		canvas.create_image(0, 0, image=self.bg_image, anchor='nw')
		
		logFr = Frame(canvas)
		logFr.pack(pady=80)
		canvas.create_window(150, 100, window=logFr)
		
		self.login = Entry(logFr, font=font, bg='#5181B8', fg='white')
		self.login.pack(side='bottom')
		canvas.create_text(95, 70, font=("Arial", 14), text=labeltext[0], fill='white')
		
		
		pasFr = Frame(canvas)
		pasFr.pack()
		canvas.create_window(150, 200, window=pasFr)
		
		self.password = Entry(pasFr, font=font, bg='#5181B8', fg='white', show='*')
		self.password.pack(side='bottom')
		canvas.create_text(105, 170, font=("Arial", 14), text=labeltext[1], fill='white')
		
		self.canvas = canvas
		
		btn = Button(canvas,
					 text='Войти',
					 width=6,
					 height=2 ,
					 bg='#5181B8',
					 fg='white',
					 command=self.performThreadAct)
												
		btn.pack(side='bottom', pady=45)
		canvas.create_window(150, 300, window=btn)
		
		self.master.bind('<Return>', lambda event: self.performThreadAct())
		
	def performThreadAct(self):
		thread = threading.Thread(target=self.btnAct, args=(self.login.get(), self.password.get(), self.result))
		thread.daemon = True
		thread.start()

if __name__ == '__main__':
	app = AuthGUI(relief=RIDGE)
	mainloop()