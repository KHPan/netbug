#all
try:
  from google.colab import drive
  drive.mount('/content/gdrive')
  is_colab = True
except:
  is_colab = False
from bs4 import BeautifulSoup
import requests
from opencc import OpenCC
import traceback
import copy
import sys
import os
try:
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
	os.chdir(os.getcwd())
import wcwidth
import time
import random
random.seed(time.time())
import re

is_colab=False
is_show_steps=False
cc=OpenCC("s2tw")

def askYN(prt="滿意嗎？"):			#問是否問題
	while True:
		print(prt+"(y/n)", end="")
		inp=input()
		if inp=="y" or inp=="Y" or inp=="ｙ" or inp=="Ｙ":
			return True
		elif inp=="n" or inp=="N" or inp=="ｎ" or inp=="Ｎ":
			return False

def isSpace(ch):		#判別是否為空格
	return (ch==' ' or ch=='\u3000' or ch=='\t' or ch=='\n'
		or ch=='\u2003' or ch=='\xa0' or ch=='\r')

def isTitle(str):		#判別是否有標題
	if str[0] != '第':
		return False
	nplace=str.find('\n')
	if nplace==-1:
		nplace=len(str)
	pt = str[:nplace].find('章')
	if pt == -1:
		return False
	return (pt+1<nplace and isSpace(str[pt+1]))

def open_file(file_name, mode, is_novel):	#開啟檔案
	if is_novel:
		if is_colab:
			ret=open("/content/gdrive/MyDrive/小說/"
				+file_name, mode, encoding="utf-8")
		else:
			try:
				ret=open("C:/Users/HANK/Downloads/"
					+file_name, mode, encoding="utf-8")
			except:
				ret=open("C:/Users/hank9/OneDrive/文件/下載的小說/"
					+file_name, mode, encoding="utf-8")
	else:
		if is_colab:
			ret=open(file_name, mode, encoding="utf-8")
		else:
			ret=open(file_name, mode, encoding="utf-8")
	return ret

def printLine():		#畫一條線
	rows, _ = os.get_terminal_size()
	print('\u2588' * rows)

def print2(str1, str2):		#左右print
	str1 = str(str1).replace("\t", "    ").replace("\r", "")
	str2 = str(str2).replace("\t", "    ").replace("\r", "")
	def custom_wrap(text, width):
		result = []  # 用于存储每行的内容

		lines = text.split('\n')

		for line in lines:
			line_length = 0
			current_line = ""
			for char in line:
				char_width = wcwidth.wcswidth(char)
				if char_width < 0:
					char_width = 1
				if line_length + char_width <= width:
					line_length += char_width
				else:
					result.append(current_line +
						" " * (width - line_length))
					line_length = char_width
					current_line = ""
				current_line += char
			if line_length > 0:
				result.append(current_line +
					" " * (width - line_length))

		return result

	rows, _ = os.get_terminal_size()
	separator = " \u2588 "
	half_width = (rows - 4) // 2
	
	lines_str1 = custom_wrap(str1, half_width)
	lines_str2 = custom_wrap(str2, half_width)
	
	max_lines = max(len(lines_str1), len(lines_str2))
	
	for i in range(max_lines):
		line_str1 = (lines_str1[i] if i < len(lines_str1)
			else " " * half_width)
		line_str2 = (lines_str2[i] if i < len(lines_str2)
			else " " * half_width)
		
		print(line_str1 + separator + line_str2)


class CommandHandler:
	def __init__(self, txt):
		self.spt = str(txt).split(" ")
		self.index = 0
	
	def isWord(self, word):
		if self.index < len(self.spt)
			and self.spt[self.index] == word:
			self.index += 1
			return True
		else:
			return False
	
	def isEmpty(self):
		return self.index >= len(self.spt)
	
	def pop(self):
		try:
			return self.spt[self.index]
		except:
			return None
	
	def popInt(self):
		try:
			return int(self.spt[self.index])
		except:
			return None
	
	def remain(self):
		ret = " ".join(self.spt[self.index:])
		self.index = len(self.spt)
		return ret


class SiteData:
	def __init__(self, txt = None):
		if txt == "" or txt is None:
			self.address_name = ""
			self.client_name = ""
			self.encoding = ""
			self.fnovelname = ""
			self.fpreread = ""
			self.fstart = ""
			self.fcontent = ""
			self.ftitle = ""
			self.fnext = ""
		else:
			lst = txt.split("\n/\n")
			self.address_name = lst[0]
			self.client_name = lst[1]
			self.encoding = lst[2]
			self.fnovelname = lst[3]
			self.fpreread = lst[4]
			self.fstart = lst[5]
			self.fcontent = lst[6]
			self.ftitle = lst[7]
			self.fnext = lst[8]
	def __str__(self):
		return "\n/\n".join([self.address_name, self.client_name,
			self.encoding, self.fnovelname, self.fpreread,
			self.fstart, self.fcontent, self.ftitle, self.fnext])


fname = {"fnovelname" : "小說名",
		"fpreread" : "前言",
		"fstart" : "開始",
		"fcontent" : "內文",
		"ftitle" : "章節標題(若無則nothing)",
		"fnext" : "下一章或out"}


class SiteList:
	def __init__(self):
		site_file = open_file("netbug-data3.txt", 'r', False)
		self.data = [SiteData(f) for f in 
			site_file.read().split("\n--網站分隔線--\n")]
		site_file.close()
		
	def find(self, sub_address):
		for ele in self.data:
			if ele.address_name == sub_address:
				return ele
		return None
		
	def showSites(self):
		for site_data in self.data:
			print(site_data.client_name + "：" +
				site_data.address_name)
	
	def append(self, new_obj):
		self.data.append(new_obj)
	
	def write(self):
		site_file = open_file("netbug-data3.txt", 'w', False)
		site_file.write("\n--網站分隔線--\n".join(
			map(str, self.data)))
		site_file.close()
		
	def __contains__(self, site_data):
		return site_data in self.data


class Out:
	def __str__(self):
		return "爬蟲結束"

class Error:
	def __str__(self):
		return "出現錯誤"

class Novel:
	def __init__(self, site_data, is_test):
		self.site_data = site_data
		self.is_test = is_test
		#self.address
		#self.bs
		#self.div
		self.first_encoding = True
	
	def addressBeautify(self, address):
		if address.find("https://")==0:
			return address
		elif address.find("//")==0:
			return "https:"+address
		elif address.find("/")==0:
			return "/".join(self.address.split("/")[:3]) + address
		else:
			return ("/".join(self.address.split("/")[:-1])
				+"/"+address)
	
	#設定BS順便搞Encoding
	headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
	def setAddressAndEncoding(self, address):
		try:
			req = requests.get(address, headers = Novel.headers)
		except:
			print("讀取網址失敗")
			return False
		self.address = address
		
		#非測試模式
		if not self.is_test or not self.first_encoding:
			req.encoding = self.site_data.encoding
			self.bs = BeautifulSoup(req.text, "lxml")
			return True
		self.first_encoding = False
		
		#預設
		if self.site_data.encoding != "":
			req.encoding = self.site_data.encoding
			self.bs = BeautifulSoup(req.text, "lxml")
			print("原encoding："+self.site_data.encoding)
			print("檢測網頁內容：")
			print(self.bs.getText())
			if askYN():
				return True
		else:
			self.bs = BeautifulSoup(req.text, "lxml")
			if self.bs.find("head") is None:
				print("BS:「"+str(self.bs)+"」")
				print("find(head)是None，網站似乎不提供爬蟲")
				return False
			
			for metas in self.bs.find("head").find_all("meta"):
				if not metas.get("charset") is None:
					self.site_data.encoding=metas.get("charset")
					break
			
			try:
				if self.site_data.encoding=="":
					self.site_data.encoding=req.encoding
					print("默認encoding："+self.site_data.encoding)
				else:
					req.encoding=self.site_data.encoding
					self.bs=BeautifulSoup(req.text, "lxml")
					print("網站encoding："+self.site_data.encoding)
				print("檢測網頁內容：")
				print(self.bs.getText())
			except:
				print("網站提供encoding有誤")
			else:
				if askYN():
					return True
		
		#手動輸入encoding
		while True:
			self.site_data.encoding=input("輸入測試encoding：")
			try:
				req.encoding=self.site_data.encoding
				self.bs=BeautifulSoup(req.text, "lxml")
				print(self.bs.getText())
			except:
				print("請輸入合法encoding")
			else:
				if askYN():
					return True
	
	special_cmd = ("exist", "start")
	def find(self, cmd, *, is_list):
		tag_name = cmd[0]
		cmd = cmd[1:]
		if len(cmd) < 2 or cmd[0] in Novel.special_cmd:
			attrs = {}
		else:
			attr_name = "class_" if cmd[0] == "class" else cmd[0]
			if len(cmd) > 2 and cmd[2] == "exist":
				target = re.compile(cmd[1])
				cmd = cmd[3:]
			elif len(cmd) > 2 and cmd[2] == "start":
				target = re.compile("^" + cmd[1])
				cmd = cmd[3:]
			else:
				target = cmd[1]
				cmd = cmd[2:]
			attrs = {attr_name : target}
		
		if len(cmd) == 0:
			if is_list:
				ret = self.div.find_all(tag_name, **attrs)
				return ret if ret else []
			else:
				return self.div.find(tag_name, **attrs)
		else:
			lst = self.div.find_all(tag_name, **attrs)
			index = int(cmd[0])
			if lst is None or index >= len(lst):
				return [] if is_list else None
			else:
				return [lst[index]] if is_list else lst[index]
	

	text_tag = ("p", "h1", "h2", "h3", "b", "em", "span")
	def runLine(self, code_line):	#跑單行程式
		if is_show_steps:
			print(self.div)
			print(code_line)
			printLine()
		try:
			spt = [ele.replace("\\s", " ").replace("\\n", "\n")
				for ele in code_line.split(" ")]
			if spt[0] == "text":
				self.div = copy.copy(self.div)
				for ele in self.div.find_all(recursive=False):
					if ele.name == "br":
						ele.replace_with("\n")
					elif ele.name in Novel.text_tag:
						ele.replace_with(ele.getText()+"\n")
					else:
						ele.extract()
				self.div = cc.convert(self.div.getText())
				start = 0
				while start<len(self.div):
					if not isSpace(self.div[start]):
						break
					start = start + 1
				end = len(self.div) - 1
				while end>start:
					if not isSpace(self.div[end]):
						break
					end = end - 1
				if start >= end:
					self.div = ""
				else:
					self.div = self.div[start:(end+1)]
			
			elif spt[0] == "unwrap":
				self.div = copy.copy(self.div)
				for ele in self.find(spt[1:], is_list = True):
					ele.unwrap()
			
			elif spt[0] == "select":
				self.div = self.div.select_one(
					code_line[code_line.index(" ")+1:])
				
			elif spt[0] == "trans":
				if len(spt) > 1:
					time.sleep(random.uniform(int(spt[1]), int(spt[2])))
				assert self.setAddressAndEncoding(
					self.addressBeautify(self.div)), f"網址{self.div}跳轉失敗"
				self.div = self.bs
			
			elif spt[0] == "get":
				self.div = self.div.get(spt[1])
			
			elif spt[0] == "extract":
				self.div = copy.copy(self.div)
				[ele.extract() for ele in
					self.find(spt[1:], is_list = True)]
			
			elif spt[0] == "find":
				if isinstance(self.div, str):
					self.div = self.div.find(spt[1])
				else:
					self.div = self.find(spt[1:], is_list = False)
			
			elif spt[0] == "out":
				if spt[1] == "exist":
					if len(spt) == 2:
						if self.div != -1 and not self.div is None:
							self.div = Out()
					else:
						if str(self.div).find(spt[-1]) != -1:
							self.div = Out()
				elif spt[1] == "not" and spt[2] == "exist":
					if len(spt) == 3:
						if self.div == -1 or self.div is None:
							self.div = Out()
					else:
						if str(self.div).find(spt[-1]) == -1:
							self.div = Out()
			
			elif spt[0] == "back":
				if len(spt) == 1:
					self.div = self.bs
				elif spt[1] == "tag":
					self.div = self.tag
			
			elif spt[0] == "nothing":
				self.div = ""
			
			elif spt[0] == "split":
				self.div = self.div.split(spt[1])[int(spt[2])]
			
			elif spt[0] == "tag":
				self.tag = self.div
			
			else:
				print("CODE_ERROR:"+code_line)
				print("指令不存在")
				self.div = Error()
				return False
		except:
			print("CODE_ERROR:"+code_line)
			traceback.print_exc()
			self.div = Error()
			return False
			
		return True
	
	def setCopy(self):
		self.cdiv = [self.div]
		self.cbs = [self.bs]
		self.ctag = [self.tag]
	
	def fromCopy(self):
		self.div = self.cdiv[-1]
		self.bs = self.cbs[-1]
		self.tag = self.ctag[-1]
	
	def popCopy(self):
		self.cdiv.pop()
		self.cbs.pop()
		self.ctag.pop()
		self.fromCopy()
	
	def resetCopy(self):
		self.cdiv = [self.cdiv[0]]
		self.ctag = [self.ctag[0]]
		self.cbs = [self.cbs[0]]
		self.fromCopy()
	
	def appendCopy(self):
		self.cdiv.append(self.div)
		self.cbs.append(self.bs)
		self.ctag.append(self.tag)
	
	def codeStart(self):
		self.div = self.bs
		self.tag = None
	
	def runCode(self, code_name, err_cnt=0):	#跑或製造程式
		self.codeStart()
		code_all = getattr(self.site_data, code_name, None)
		if code_all != "":
			old_addr = self.address
			if self.is_test:
				self.setCopy()
			for code_line in code_all.split("\n"):
				if err_cnt == 2:
					print(self.div)
					print("CODE：" + code_line)
				self.runLine(code_line)
				if isinstance(self.div, Out):
					break
				elif isinstance(self.div, Error):
					while not self.setAddressAndEncoding(old_addr):
						print(f"網址{old_addr}跳轉失敗，之前明明成功了，真奇怪，10-100秒後重試")
						time.sleep(random.uniform(10, 100))
						print("10-100秒結束")
					if err_cnt<2:
						print("出錯!!五秒後重新載入")
						time.sleep(5)
						print("五秒結束")
						self.runCode(code_name, err_cnt+1)
					else:
						print("網址：" + self.address)
						print("CODE_NAME：" + code_name)
						print("已三次重新載入仍舊錯誤!!!!!")
					break
			if self.is_test:
				print(self.div)
				if askYN(fname[code_name]+"滿意嗎？"):
					return self.div
				else:
					self.fromCopy()
			else:
				return self.div
		
		#寫code
		codes = []
		self.setCopy()
		if code_name == "fnext":
			last_page = Novel(self.site_data, False)
			while not last_page.setAddressAndEncoding(
				input("輸入最後一頁網址：")):
				pass
			last_page.codeStart()
			last_page.setCopy()
			print2(self.div, last_page.div)
		else:
			print(self.div)
		printLine()
		while True:
			inp = input(f"輸入{fname[code_name]}程式碼:")
			if inp == "undo":
				if len(codes) > 0:
					codes.pop()
					self.popCopy()
					if code_name == "fnext":
						last_page.popCopy()
						print2(self.div, last_page.div)
					else:
						print(self.div)
					printLine()
				else:
					print("無程式碼")
					
			elif inp == "reset":
				codes = []
				self.resetCopy()
				if code_name == "fnext":
					last_page.resetCopy()
					print2(self.div, last_page.div)
				else:
					print(self.div)
				printLine()
				
			elif inp == "ok" or inp == "done" or inp == "":
				setattr(self.site_data, code_name,
					"\n".join(codes))
				return self.div
			
			elif inp == "jump":
				new_addr = input("輸入跳轉網址：")
				old_addr = self.address
				if not self.setAddressAndEncoding(new_addr):
					print("網址跳轉失敗")
					self.address = old_addr
				else:
					codes = []
					self.codeStart()
					self.setCopy()
					if code_name == "fnext":
						last_page.setCopy()
						print2(self.div, last_page.div)
					else:
						print(self.div)
					printLine()
			
			elif inp == "show":
				if code_name == "fnext":
					print2(self.div, last_page.div)
				else:
					print(self.div)
				printLine()
			
			elif inp.find("show ") == 0:
				try:
					spt = inp.split(" ")
					fa = self.find(spt[1:], is_list = True)
					for index, content in sorted(enumerate(fa),
						key = lambda obj: len(str(obj[1]))):
						print(f"index:{index}")
						print(content)
						print(f"index:{index}")
						printLine()
				except:
					traceback.print_exc()
			
			else:
				if self.runLine(inp) and (code_name != "fnext"
					or isinstance(last_page.div, Out)
					or last_page.runLine(inp)):
					codes.append(inp)
					self.appendCopy()
					if code_name == "fnext":
						last_page.appendCopy()
						print2(self.div, last_page.div)
					else:
						print(self.div)
					printLine()
				else:
					self.fromCopy()
					if code_name == "fnext":
						last_page.fromCopy()


class Require:
	def __init__(self, novel, file_name = ""):
		self.novel = novel
		self.file_name = file_name
		if file_name == "":
			self.file = sys.stdout
		else:
			self.file = open_file(file_name, 'w', True)
	def __del__(self):
		if self.file_name != "":
			self.file.close()


site_list = SiteList()
is_test = False
while True:
	try:
		require_list = []
		while True:
			#輸入網址
			print("輸入測試網址：" if is_test
				else "輸入爬蟲網址：")
			try:
				address = input()
			except KeyboardInterrupt:
				print("程式結束，KeyboardInterrupt")
				sys.exit()
			#檢查指令
			if address == "t" or address == "T":
				is_test = not is_test
				require_list = []
				continue
			elif address == "ok" or address == "":
				if is_test:
					print("ok是爬蟲模式使用的")
					continue
				elif len(require_list) == 0:
					print("還沒有要爬的東西")
					continue
				else:
					break
			elif address == "show":
				site_list.showSites()
				continue
					
			#novel類別初始化
			try:
				address_name = address.split("/")[2]
			except:
				print("請使用合法網址")
				continue
			site_data = site_list.find(address_name)
			if site_data is None:
				if is_test:
					site_data = SiteData()
					site_data.address_name = address_name
					site_data.client_name = input("輸入網站名：")
				else:
					print("未登錄網站，請使用以下網站：")
					site_list.showSites()
					continue
			this_novel = Novel(site_data, is_test)
			#bs初始化和encoding
			if not this_novel.setAddressAndEncoding(address):
				continue
			#開啟寫檔案
			novel_name = this_novel.runCode("fnovelname")
			if is_test:
				require_list.append(Require(this_novel))
			else:
				inp = input("小說名：" + novel_name)
				file_name = (novel_name + inp + "(爬蟲-" +
					site_data.client_name + ").txt")
				require_list.append(Require(this_novel, file_name))
			
			#test模式只有一個網址
			if is_test:
				break
		
		all_err_msg=[]
		cnt=0
		while len(require_list) > 0:
			for require in require_list[:]:
				if cnt == 0:
					preread = require.novel.runCode("fpreread")
					print(require.file_name + "：前言")
					require.file.write(preread + "\n")
					require.novel.runCode("fstart")
				else:
					content = require.novel.runCode("fcontent")
					title = require.novel.runCode("ftitle")
					if title == "":
						print(f"{require.file_name}：第{cnt}頁")
					else:
						if not isTitle(content):
							content = title + "\n" + content
							if not isTitle(content):
								content = f"第{cnt}章 " + content
						print(require.file_name + "：" + 
							content[:content.find("\n")])
					require.file.write(content + "\n")
					if isinstance(require.novel.runCode("fnext"),
						Out):
						require_list.remove(require)
						del require
			cnt = cnt + 1
			if is_test and cnt == 2:
				if not require_list[0].novel.site_data in site_list:
					site_list.append(require_list[0].novel.site_data)
				site_list.write()
				print("成功寫入檔案")
				break
	except KeyboardInterrupt:
		if is_test and len(require_list) > 0:
			file = open_file("netbug-data-test3.txt", 'w', False)
			file.write(str(require_list[0].novel.site_data))
			file.close()
		print("重來，KeyboardInterrupt")