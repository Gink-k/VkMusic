import vk_api
from vk_api.audio import VkAudio

class VkMusic:
	def authVk(self, login, password, flag):
		try:
			self.session = vk_api.VkApi(login, password)
			self.session.auth()
			self.setVkAudio()
		except Exception:
			flag.append(0)
		else:
			self.api = self.session.get_api()
			flag.append(1)
		
	
	def setVkAudio(self):
		self.vkAudio = VkAudio(self.session)
		
	def getUserPhoto(self):
		return self.api.photos.get(album_id='profile')["items"][-1]["sizes"][0]["url"]
		
	def getUserInfo(self):
		return self.api.users.get()[0]
		
	def getUserMusic(self, userList):
		music = []
		music.extend(self.vkAudio.get())
		userList[0] = music

	def getMusic(self, name, findedMusic):		
		music = []
		music.extend(self.vkAudio.search(name, count=500))
		findedMusic[0] = music