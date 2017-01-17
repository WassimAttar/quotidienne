# coding: utf-8

import sys

if sys.version_info < (3,0) :
	print("Fonctionne uniquement avec python 3")
	exit()

import os, re, time, subprocess, xml.dom.minidom, socket, urllib.request
from bs4 import BeautifulSoup

homedir = os.path.expanduser('~')

# Fichier de l'historique des vidéos déjà téléchargées
historique = homedir + "/Téléchargements/.quotidienne_historique"


class Source :

	# Dossier ou les vidéos sont sauvegardées
	outputdir = homedir + "/Téléchargements/"

	def _downloadXml(self,url):
		downloadTries = 0
		xmlFile = None
		while xmlFile is None :
			try:
				xmlFile = urllib.request.urlopen(url,timeout = 3).read()
			except (urllib.request.URLError, socket.timeout) as err:
				if downloadTries > 3:
					print("Problème de téléchargement, réessayez plus tard")
					return False
				else:
					downloadTries += 1
					print(type(self).__name__+" : Essai n°"+str(downloadTries))
					time.sleep(3)
		return xmlFile

	def _parseXml(self,xmlData) :
		try :
			tmp = xml.dom.minidom.parseString(xmlData)
		except xml.parsers.expat.ExpatError :
			tmp = False
		return tmp

	def _extractUrls(self,xml):
		pass

	def getUrls(self):
		urls = []
		for playlist in self._playLists :
			self._nomEmission = playlist[1]
			xmlData = self._downloadXml(self._urlXml.format(playlist[0]))
			if not xmlData == False :
				playlistXml = self._parseXml(xmlData)
				if not playlistXml == False :
					urls += self._extractUrls(playlistXml)
		return urls


class Canal(Source) :

	__playLists=[
	[201,"Zapping"],

	# [48,"Guignols"],
	# [121,"Bandes de filles"],
	# [14,"Le Cercle"],
	# [39,"Connasse"],
	# [130,	"Action discrete"],
	# [304,	"Action discrete"],
	# [371,	"Action discrete"],
	# [62,	"Le boucan du jour"],
	# [627,	"Bref"],
	# [104,	"Le grand journal"],
	# [254,	"Groland"],
	# [242,	"Du hard ou du cochon"],
	# [451,	"Jamel comedy club"],
	# [896,	"Le journal du hard"],
	# [39,	"La matinale"],
	# [215,	"Le meilleur du hier"],
	# [47,	"Les pépites du net"],
	# [249,	"Petit journal [le)"],
	# [843,	"La question de plus"])
	# [294,	"La revue de presse de Catherine et Eliane"],
	# [1082,"Salut les terriens"],
	# [41,	"Salut les terriens"],
	# [74,	"Salut les terriens"],
	# [105,	"Salut les terriens"],
	# [110,	"Salut les terriens"],
	# [316,	"Salut les terriens"],
	# [371,	"Salut les terriens"],
	# [680,	"Salut les terriens - edito de Blako"],
	# [1064,"Salut les terriens - Gaspard Proust"],
	# [1072,"Salut les terriens - les martiens de la semaine"],
	# [252,	"SAV des émissions"],
	# [936,	"Tweet en clair"],

	]

	# URL de toutes les vidéos d'une émission donnée.
	__urlXml = 'http://service.canal-plus.com/video/rest/getMEAs/cplus/{}'

	# Dossier ou les vidéos sont sauvegardées
	outputdir = homedir + "/Vidéos/en attente/"

	def __init__(self):
		self._urlXml = Canal.__urlXml
		self._playLists = Canal.__playLists

	# Les dates fournies par canal ne sont pas toujours bien formatées.
	# Parfois c'est 02/05/2015 ou 02/05/15 ou 02/05
	# Pour avoir l'historique et donc éviter de télécharger plusieurs fois la même émission
	# il est nécessaire de formater toujours de la même façon la date de diffusion de l'émission.
	# La forme choisie est la suivante 02/05/15
	def __getDate(self,i):
		L = ['TITRE','SOUS_TITRE']
		grep_date_annee_complete = '[0-9]{2}/[0-9]{2}/[0-9]{4}'
		grep_date_annee = '[0-9]{2}/[0-9]{2}/[0-9]{2}'
		grep_date_mois = '[0-9]{2}/[0-9]{2}'
		for balise in L:
			valeur = i.getElementsByTagName(balise)[0].childNodes[0].nodeValue
			if re.search(grep_date_annee_complete, valeur):
				temp = re.findall(grep_date_annee_complete, valeur)[0]
				return temp[0:6]+temp[8:10]
			elif re.search(grep_date_annee, valeur):
				return re.findall(grep_date_annee, valeur)[0]
			elif re.search(grep_date_mois, valeur):
				return re.findall(grep_date_mois, valeur)[0]+"/"+time.strftime("%y")
		return ""

	def _extractUrls(self,xmldoc):
		urls = []
		L = ['TITRE','SOUS_TITRE']
		meas = xmldoc.getElementsByTagName('MEA')
		for i in meas:
			if i.getElementsByTagName('ID')[0].childNodes != []:
				addUrl = True
				id = i.getElementsByTagName('ID')[0].childNodes[0].nodeValue
				for balise in L :
					if i.getElementsByTagName(balise)[0].childNodes != []:
						valeur = i.getElementsByTagName(balise)[0].childNodes[0].nodeValue
						if 'semaine' in valeur.lower() :
							addUrl = False
							break

				if i.getElementsByTagName('DURATION')[0].childNodes != []:
					duration = int(i.getElementsByTagName('DURATION')[0].childNodes[0].nodeValue)
					if duration > 480 and self._nomEmission == "Zapping" :
						addUrl = False

				if addUrl :
					url = i.getElementsByTagName('URL')[0].childNodes[0].nodeValue
					urls.append([self._nomEmission,self.__getDate(i),url])
		return urls


class FranceInfo(Source) :

	__playLists=[
		[11581,"C'est mon argent"],
		[11617,"C'est mon boulot"],
		[14473,"C'est mon époque"],
		[14100,"En direct de la Silicon Valley"],
		[13241,"France Info numérique"],
		[14072,"L'interview éco"],
		[14070,"Le décryptage éco"],
		[14099,"Le mot de l'éco"],
		[18998,"Nouveau monde"],
		[10586,"Le sens de l'info"],
		[15192,"Le vrai du faux numérique"],
		[14475,"On s'y emploie"],
		[12092,"Question de choix"],
		[14152,"Tout et son contraire, l'intégrale"],
		[11063,"Tout Info tout éco"],
		[11531,"Le billet de François Morel"],
		[14103,"Ca nous marque"],
		[11453,"Les pourquoi"],
		[11549,"Sur les épaules de Darwin"],
	]

	# URL des podcasts.
	__urlXml = 'http://radiofrance-podcast.net/podcast09/rss_{}.xml'

	# Dossier ou les vidéos sont sauvegardées
	outputdir = homedir + "/Vidéos/en attente/franceinfo/"


	def __init__(self):
		self._urlXml = FranceInfo.__urlXml
		self._playLists = FranceInfo.__playLists

	def __getDate(self,url) :
		grep_date_annee_complete = '[0-9]{2}.[0-9]{2}.[0-9]{4}'
		if re.search("-"+grep_date_annee_complete+"-", url):
			tmp = re.findall(grep_date_annee_complete, url)[0]
			return tmp.replace(".", "/")
		return ""

	def _extractUrls(self,xmldoc):
		urls = []
		meas = xmldoc.getElementsByTagName('item')
		for i in meas:
			if i.getElementsByTagName('guid')[0].childNodes != []:
				url = i.getElementsByTagName('guid')[0].childNodes[0].nodeValue
				urls.append([self._nomEmission,self.__getDate(url),url])
		return urls


class Bfm(Source) :

	__template = """
	    <object class="BrightcoveExperience">
        <param name="playerID" value="1225340300001" />
        <param name="playerKey" value="AQ~~,AAAAzBCHAyE~,4dQGL3-Dcc52cNRXVBpbhFHpDeu15lHx" />
        <param name="@videoPlayer" value="{}" />
    </object>
  """

	__patternVideoID = 'data-video-id="[0-9]{13}"'

	# L'URL des vidéos.
	__playLists=[
		['http://bfmbusiness.bfmtv.com/mediaplayer/video/marc-fiorentino-',"Fiorantino"]
	]

	# URL de toutes les vidéos d'une émission donnée.
	__urlXml = 'http://bfmbusiness.bfmtv.com/mediaplayer/chroniques/marc-fiorentino/'

	# Dossier ou les vidéos sont sauvegardées
	outputdir = homedir + "/Vidéos/en attente/"

	def __init__(self):
		self._urlXml = Bfm.__urlXml
		self._playLists = Bfm.__playLists
		self.__webServerProcess = ""
		self.__launchTmpWebServer()

	def __del__(self):
		self.__webServerProcess.terminate()

	def __getDate(self,url) :
		grep_date_mois_liste = ['-[0-9]{2}-[0-9]{2}-[0-9]{6}','-[0-9]{4}-[0-9]{6}']
		for grep_date_mois in grep_date_mois_liste :
			if re.search(grep_date_mois, url):
				tmp = (re.findall(grep_date_mois, url)[0]).replace("-","")
				date = tmp[:2] + '/' + tmp[2:4]
				year = time.strftime("%y")
				if int(time.strftime("%m")) < 3 :
					year = str(int(year)-1)
				return date+"/"+year
		return ""

	def _parseXml(self,xmlData) :
		return BeautifulSoup(xmlData, "lxml")

	def _extractUrls(self,xmldoc):
		urls = []
		for link in xmldoc.find_all('a', href=True):
			if Bfm.__playLists[0][0] in link['href']:
				url = link['href']
				tmpUrl = self.__createTmpUrl(url)
				if tmpUrl == False :
					tmpUrl = url
				urls.append([self._nomEmission,self.__getDate(url),tmpUrl])
		return urls

	def __createTmpUrl(self,url) :
		xmlData = str(super(Bfm,self)._downloadXml(url))
		if re.search(Bfm.__patternVideoID, xmlData):
			videoID = (re.findall(Bfm.__patternVideoID, xmlData)[0])[15:28]
			self.__createTmpHtml(videoID)
			return "http://localhost:8888/{}".format(videoID)
		return False

	def __createTmpHtml(self,videoID) :
		file = open("/tmp/"+videoID, 'a')
		file.write(Bfm.__template.format(videoID))
		file.close()

	def __launchTmpWebServer(self) :
		cmd_args = ['python','-m','SimpleHTTPServer',"8888"]
		self.__webServerProcess = subprocess.Popen(cmd_args,cwd="/tmp/")

class Download :

	def __init__(self,Source):
		self.__checkYoutubeDlInstallation()
		self.__checkHistoryFile()
		self.__outputdir = Source.outputdir
		self.__urls(Source.getUrls())


	def __checkYoutubeDlInstallation(self):
		try:
			subprocess.call(["youtube-dl","--version"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		except OSError :
			print("youtube-dl non installé. Pour installer la dernière version, tapez cette commande :\nsudo wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/bin/youtube-dl && sudo chmod 755 /usr/bin/youtube-dl")
			exit()

	def __checkHistoryFile(self):
		if not os.path.isfile(historique) :
			file = open(historique, 'w+')
			file.close()


	def __getQuality(self,url):
		cmd_args = ['youtube-dl','-F', url]
		p = subprocess.check_output(cmd_args)
		p.rstrip()
		return re.findall('http-\d*',p)[-1]

	def __checkHistory(self,logPlaylist):
		file = open(historique, 'r')
		for line in file:
			if logPlaylist+'\n' == line:
				# print("Déjà DL : "+logPlaylist)
				file.close()
				return True
		file.close()
		return False

	def __addHistory(self,logPlaylist):
		file = open(historique, 'a')
		file.write(logPlaylist + '\n')
		file.close()

	def __wget(self,url):
		cmd_args = ['wget',"-P", self.__outputdir, url]
		p = subprocess.Popen(cmd_args)
		return p.wait()

	def __youtubeDl(self,url) :
		cmd_args = ['youtube-dl','-f','best', "-o", self.__outputdir+"%(title)s.%(ext)s", url]
		p = subprocess.Popen(cmd_args)
		return p.wait()


	def __download(self,url) :
		extensions = ['mp3','mp4']
		for extension in extensions :
			if extension in url :
				return self.__wget(url)
		return self.__youtubeDl(url)

	def __urls(self,urls) :
		for url in urls :
			logPlaylist = url[0]+"|"+url[1]
			if not self.__checkHistory(logPlaylist) :
				if self.__download(url[2]) == 0 :
					self.__addHistory(logPlaylist)

def real_main() :
	Sources = [Canal,Bfm,FranceInfo]

	for Source in Sources :
		Download(Source())

if __name__ == "__main__":

	try:
		real_main()
	except KeyboardInterrupt:
		exit('\nERROR: Interrompu par l\'utilisateur')
