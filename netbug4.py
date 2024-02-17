try:
  from google.colab import drive
  drive.mount('/content/gdrive')
  is_colab = True
except:
  is_colab = False
from bs4 import BeautifulSoup, Comment
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
import itertools
cc=OpenCC("s2tw")
from urllib.parse import urljoin
from urllib.parse import urlparse

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

def _custom_wrap(text, width):	#print2專用，照寬切字串
	lines = str(text).replace("\t", "  ").splitlines()
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
				yield (current_line +
					" " * (width - line_length))
				line_length = char_width
				current_line = ""
			current_line += char
		if line_length > 0:
			yield (current_line +
				" " * (width - line_length))

def print2(strs, insert_str = ""):		#並排寫多段字串並加分隔線
	rows, _ = os.get_terminal_size()
	if len(strs) == 1:
		print(strs[0])
	else:
		separator = " \u2588 "
		ele_width = (rows + len(separator) - 1) // len(strs) - len(separator)
		iters = (_custom_wrap(txt, ele_width) for txt in strs)
		for line in itertools.zip_longest(*iters, fillvalue = " " * ele_width):
			print(separator.join(line))
	if insert_str != "":
		print(insert_str)
	print('\u2588' * rows)

class CommandHandler:	#POP分析指令
	def __init__(self, txt):
		self.spt = [ele.replace("\\s", " ").replace("\\n", "\n")
				for ele in str(txt).split(" ")]
		self.index = 0
	
	def isWord(self, word):
		if isinstance(word, tuple):
			return any(self.isWord(w) for w in word)
		elif isinstance(word, list):
			if self.index + len(word) <= len(self.spt):
				for i in range(0, len(word)):
					if word[i] != self.spt[self.index + i]:
						return False
				self.index += len(word)
				return True
			else:
				return False
		else:
			if (self.index < len(self.spt)
				and self.spt[self.index] == word):
				self.index += 1
				return True
			else:
				return False
	
	def isEmpty(self):
		return self.index >= len(self.spt)
	
	def pop(self):
		try:
			ret = self.spt[self.index]
			self.index += 1
			return ret
		except:
			return None
	
	def popInt(self):
		try:
			ret = int(self.spt[self.index])
			self.index += 1
			return ret
		except:
			return None
	
	def remain(self):
		ret = " ".join(self.spt[self.index:])
		self.index = len(self.spt)
		return ret
	
	def __len__(self):
		return len(self.spt) - self.index
	
	def __getitem__(self, index):
		try:
			return self.spt[self.index + index]
		except:
			return None
	
	def __str__(self):
		return " ".join(self.spt)

class SiteList:			#存著那些sites
	def __init__(self):
		site_file = open_file("site-data.txt", 'r', False)
		self.data = [Site(f) for f in 
			site_file.read().split("\n--網站分隔線--\n")]
		site_file.close()
		
	def find(self, address):
		sub_address = urlparse(address).netloc
		for ele in self.data:
			if ele.address_name == sub_address:
				return ele
		return None
		
	def showSites(self):
		for site in self.data:
			print(site.client_name + "：" +
				site.address_name)
	
	def append(self, new_obj):
		self.data.append(new_obj)
	
	def write(self):
		site_file = open_file("site-data.txt", 'w', False)
		site_file.write("\n--網站分隔線--\n".join(
			map(str, self.data)))
		site_file.close()
		
	def __contains__(self, site_data):
		return site_data in self.data

class Site:				#網站
	def __init__(self, txt = None):
		(self.address_name, self.client_name,
			self.encoding, self.fnovelname, self.fpreread,
			self.fstart, self.fcontent, self.ftitle, self.fnext
			) = (itertools.repeat("", 9) if txt is None
			else txt.split("\n/\n"))
	
	def __str__(self):
		return "\n/\n".join([self.address_name, self.client_name,
			self.encoding, self.fnovelname, self.fpreread,
			self.fstart, self.fcontent, self.ftitle, self.fnext])
	
	headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
						#跳轉網址順便搞encoding
	def trans(self, address, old_addr = None, is_test = False):
		if old_addr is not None:
			address = urljoin(old_addr, address)
		response = requests.get(address, headers = Site.headers)
		if self.encoding != "":
			response.encoding = self.encoding
		bs = BeautifulSoup(response.text, "lxml")
		if not is_test:
			return bs, address
		elif self.encoding != "":
			print(bs.getText().strip())
			if askYN():
				return bs, address
		else:
			assert bs.find("head") is not None, "head is None"
			for metas in bs.find("head").find_all("meta"):
				if not metas.get("charset") is None:
					self.encoding = metas.get("charset")
					break
			if self.encoding == "":
				self.encoding = response.encoding
				print(bs.getText().strip())
				print(f"默認encoding：{self.encoding}")
				if askYN():
					return bs, address
			else:
				try:
					response.encoding = self.encoding
					bs = BeautifulSoup(response.text, "lxml")
					print(bs.getText().strip())
				except:
					print(f"網站提供encoding({self.encoding})有誤")
				else:
					print(f"網站提供encoding：{self.encoding}")
					if askYN():
						return bs, address
		
		while True:
			self.encoding = input("輸入測試encoding：")
			try:
				response.encoding = self.encoding
				bs = BeautifulSoup(response.text, "lxml")
				print(bs.getText().strip())
			except:
				print("請輸入合法encoding")
			else:
				if askYN():
					return bs, address

class Out:
	def __str__(self):
		return "爬蟲結束"

class Error:
	def __str__(self):
		return "出現錯誤"

class Page:				#動態改動的頁面
	def __init__(self, site, address, is_test = False):
		self.site = site
		self.address = address
		self.trans(address, is_test)
	
	def trans(self, address, is_test = False):
		self.bs, self.address = self.site.trans(
			address, self.address, is_test)
				
	def runCode(self, code, is_show = False):	#直接跑純程式碼
		run = Run(self)
		for line in code.splitlines():
			if is_show:
				print2(run.div)
				print(f"CODE:{line}")
			run.run(line)
			if isinstance(run.div, (Error, Out)):
				break
		if is_show:
			print2(run.div)
			print("網址：" + run.page.address)
		return run.div

	def runFunc(self, code_name):		#跑site裡面的程式
		code = getattr(self.site, code_name, None)
		for i in range(3):
			result = self.runCode(code, is_show = (i == 2))
			if not isinstance(result, Error):
				return result
			else:
				assert i < 2, "三次錯誤!!"
				print("出錯!!十秒後重新載入!!")
				time.sleep(10)
				print("十秒結束")
				self.trans(self.address)

class Run:				#跑時用
	def __init__(self, page):
		self.page = page
		self.div = self.page.bs
		self.tag = None
	
	special_cmd = ("exist", "start")
	def find(self, cmd, *, is_list):
		tag_name = cmd.pop()
		if len(cmd) < 2 or cmd[0] in Run.special_cmd:
			attrs = {}
		else:
			attr_name = cmd.pop()
			if attr_name == "class":
				attr_name = "class_"
			target = cmd.pop()
			if cmd.isWord("exist"):
				target = re.compile(target)
			elif cmd.isWord("start"):
				target = re.compile("^" + target)
			attrs = {attr_name : target}
		
		if cmd.isEmpty():
			if is_list:
				ret = self.div.find_all(tag_name, **attrs)
				return ret if ret else []
			else:
				return self.div.find(tag_name, **attrs)
		else:
			lst = self.div.find_all(tag_name, **attrs)
			index = cmd.popInt()
			if lst is None or index >= len(lst):
				return [] if is_list else None
			else:
				return [lst[index]] if is_list else lst[index]
	
	text_tag = ("p", "h1", "h2", "h3", "b", "em", "span")
	def run(self, code):
		if isinstance(self.div, (Out, Error)):
			return
		if isinstance(code, CommandHandler):
			cmd = code
			code = str(code)
		else:
			cmd = CommandHandler(code)
		try:
			if cmd.isWord("text"):
				self.div = copy.copy(self.div)
				for ele in self.div.find_all(string=lambda text: isinstance(text, Comment)):
					ele.extract()
				while True:
					flst = self.div.find_all(recursive=False)
					if len(flst) == 0:
						break
					for ele in flst:
						if ele.name == "br":
							ele.replace_with("\n")
						elif ele.name in Run.text_tag:
							ele.append("\n")
							ele.unwrap()
						else:
							ele.extract()
				self.div = cc.convert(self.div.getText().strip())
			
			elif cmd.isWord("unwrap"):
				self.div = copy.copy(self.div)
				word = "" if cmd.isEmpty() else cmd.pop()
				for ele in self.find(cmd, is_list = True):
					ele.insert_before(word)
					ele.unwrap()
			
			elif cmd.isWord("select"):
				self.div = self.div.select_one(cmd.remain())
				
			elif cmd.isWord("trans"):
				i1 = cmd.popInt()
				i2 = cmd.popInt()
				if i1 is not None:
					if i2 is not None:
						time.sleep(random.uniform(i1, i2))
					else:
						time.sleep(i1)
				self.page.trans(self.div)
				self.div = self.page.bs
			
			elif cmd.isWord("get"):
				self.div = self.div.get(cmd.pop())
			
			elif cmd.isWord("extract"):
				self.div = copy.copy(self.div)
				for ele in self.find(cmd, is_list = True):
					ele.extract()
			
			elif cmd.isWord("find"):
				if isinstance(self.div, str):
					self.div = self.div.find(cmd.pop())
				else:
					self.div = self.find(cmd, is_list = False)
			
			elif cmd.isWord("out"):
				if cmd.isWord("exist"):
					if cmd.isEmpty():
						if self.div != -1 and not self.div is None:
							self.div = Out()
					else:
						if str(self.div).find(cmd.pop()) != -1:
							self.div = Out()
				elif cmd.isWord(["not", "exist"]):
					if cmd.isEmpty():
						if self.div == -1 or self.div is None:
							self.div = Out()
					else:
						if str(self.div).find(cmd.pop()) == -1:
							self.div = Out()
			
			elif cmd.isWord("back"):
				if cmd.isEmpty():
					self.div = self.page.bs
				elif cmd.isWord("tag"):
					self.div = self.tag
			
			elif cmd.isWord("nothing"):
				self.div = ""
			
			elif cmd.isWord("split"):
				self.div = self.div.split(cmd.pop())[cmd.popInt()]
			
			elif cmd.isWord("tag"):
				self.tag = self.div
			
			if not cmd.isEmpty():
				print(f"CODE_ERROR:{code}")
				print("指令不存在或有多餘字符")
				print(f"remain:{cmd.remain()}")
				self.div = Error()
		except:
			print(f"CODE_ERROR:{code}")
			traceback.print_exc()
			self.div = Error()

	def __str__(self):
		if hasattr(self.div, "prettify"):
			return str(self.div.prettify())
		else:
			return str(self.div)

	def __copy__(self):
		ret = Run(copy.copy(self.page))
		ret.div = self.div
		ret.tag = self.tag
		return ret

class ListStack:
	def __init__(self, datas = None):
		self.data = []
		if datas is not None:
			self.push(datas)
	
	def push(self, datas):
		self.data.append(datas)
	
	def pop(self):
		return self.data.pop()
	
	def toBegin(self):
		ret = self.data[0]
		self.data = []
		return ret
	
	def remove(self, index):
		for data in self.data:
			data.pop(index)
	
	def append(self, it):
		for base, add in zip(self.data, it):
			base.append(add)
	
	def width(self):
		return len(self.data[0])

class Novel:
	def __init__(self, site, address = None):
		self.site = site
		if address is None:
			return
		self.page = Page(site, address)
		self.file = None
		self.file_name = None
	
	def setFile(self, add_file_name = None):
		novel_name = self.novelName()
		if add_file_name is None:
			add_file_name = input(f"小說名：{novel_name}")
		self.file_name = (novel_name + add_file_name
			+ f"(爬蟲-{self.site.client_name}).txt")
		self.file = open_file(self.file_name, 'w', True)
	
	def closeFile(self):
		if self.file is not None:
			self.file.close()
	
	def text(self, cnt):
		if cnt == 0:
			preread = self.page.runFunc("fpreread")
			print(f"{self.file_name}：前言")
			self.file.write(preread)
			self.file.write("\n")
		else:
			content = self.page.runFunc("fcontent")
			title = self.page.runFunc("ftitle")
			if title == "":
				print(f"{self.file_name}：第{cnt}頁")
			else:
				if not isTitle(content):
					content = title + "\n" + content
					if not isTitle(content):
						content = f"第{cnt}章 " + content
				print(self.file_name + "：" + 
					content[:content.find("\n")])
			self.file.write(content + "\n")

	def novelName(self):
		return self.page.runFunc("fnovelname")

	def __copy__(self):
		ret = Novel(self.site)
		ret.page = copy.copy(self.page)
		ret.file = self.file
		ret.file_name = self.file_name
		return ret

	def __iter__(self):
		yd = copy.copy(self)
		self.page.runFunc("fstart")
		yield yd
		while True:
			yd = copy.copy(self)
			if isinstance(self.page.runFunc("fnext"), Out):
				yield yd
				self.closeFile()
				return
			yield yd

class Test:
	fname = {"fnovelname" : "小說名",
			"fpreread" : "前言",
			"fstart" : "開始",
			"fcontent" : "內文",
			"ftitle" : "章節標題(若無則nothing)",
			"fnext" : "下一章或out"}
	
	def __init__(self, address, site_list = None):
		self.address = address
		if site_list is not None:
			self.test(site_list)

	def test(self, site_list):		#主程式
		self.site = site_list.find(self.address)
		if self.site is None:
			self.site = Site()
			self.site.address_name = urlparse(self.address).netloc
		try:
			if (self.site.client_name == ""
				or not askYN(f"網站名：{self.site.client_name}，滿意嗎？")):
				self.site.client_name = input("輸入網站名：")
			self.runs = [Run(Page(self.site, self.address, is_test = True))]
			self.testCode()
			if self.site not in site_list:
				site_list.append(self.site)
			site_list.write()
			print("成功寫入檔案")
		except KeyboardInterrupt:
			file = open_file("test-data.txt", 'w', False)
			file.write(str(self.site))
			file.close()
			print("目前進度寫入備用檔案")
		
	def makeCode(self, code_name = ""):		#從頭創造code
		for run in self.runs:
			run.run("back")
		codes = []
		stack = ListStack()
		print2(self.runs)
		while True:
			inp = input(f"輸入{code_name}程式碼：")
			if inp in ("ok", "done", ""):
				return "\n".join(codes)
			elif inp == "reset":
				self.runs = stack.toBegin()
				codes = []
				print2(self.runs)
			elif inp == "undo":
				if len(codes) == 0:
					print("退無可退")
				else:
					self.runs = stack.pop()
					codes.pop()
					print2(self.runs)
			elif inp == "show":
				print2(self.runs)
			elif inp.startswith("show "):
				try:
					cmd = CommandHandler(inp)
					cmd.pop()
					if cmd.isWord("text"):
						cpyruns = [copy.copy(run) for run in self.runs]
						for run in cpyruns:
							run.run("text")
						print2(cpyruns)
					else:
						fas = [run.find(copy.copy(cmd), is_list = True)
							for run in self.runs]
						blocks = itertools.zip_longest(*fas)
						for index, content in enumerate(blocks):
							print(f"index:{index}")
							print2(content, insert_str = f"index:{index}")
				except:
					traceback.print_exc()
			elif inp.startswith("remove "):
				index = int(inp.split(" ")[1])
				if index >= stack.width():
					print("超出範圍")
				elif stack.width() == 1:
					print("單一頁面無法刪除")
				else:
					stack.remove(index)
					self.runs.pop(index)
					print2(self.runs)
			elif inp == "add":
				address = input("輸入網址：")
				try:
					new_page = copy.copy(self.runs[0].page)
					new_page.trans(address)
					new_run = Run(new_page)
					new_stack = []
					for c in codes:
						new_stack.append(copy.copy(new_run))
						new_run.run(c)
						assert not isinstance(new_run.div, Error), "CODE_ERROR"
				except:
					traceback.print_exc()
					print("跳轉並跑出現問題")
				else:
					self.runs.append(new_run)
					stack.append(new_stack)
					print2(self.runs)
			else:
				old_runs = [copy.copy(run) for run in self.runs]
				for index, run in enumerate(self.runs):
					run.run(inp)
					if isinstance(run.div, Error):
						print(f"第{index}個發生問題，這條不算")
						self.runs = old_runs
						break
				else:
					codes.append(inp)
					stack.push(old_runs)
					print2(self.runs)

	def checkFunc(self, code_name):		#從site創或改code
		if getattr(self.site, code_name, None) != "":
			runs_copy = [copy.copy(run) for run in self.runs]
			try:
				results = [run.page.runFunc(code_name) for run in self.runs]
			except:
				traceback.print_exc()
				print("出問題了，重寫code")
			else:
				print2(results)
				if askYN(f"{Test.fname[code_name]}滿意嗎？"):
					return		
			self.runs = runs_copy
			print2(f"OLD CODE:\n{getattr(self.site, code_name)}")
		setattr(self.site, code_name, self.makeCode(Test.fname[code_name]))

	def testCode(self):			#test程式碼之後
		for key in Test.fname:
			if key == "fnext":
				while True:
					address = input("輸入最後一頁網址：")
					try:
						self.runs.append(Run(Page(self.site, address)))
					except requests.exceptions.RequestException:
						print("請輸入合法網址")
					else:
						break
			self.checkFunc(key)

class InputCollector:
	def __init__(self, is_test = False):
		self.is_test = is_test
	
	def input(self, site_list):
		novels = []
		while True:
			print("輸入測試網址：" if self.is_test
				else "輸入爬蟲網址：")
			try:
				address = input()
			except KeyboardInterrupt:
				print("程式結束，KeyboardInterrupt")
				sys.exit()
			#檢查指令
			if address in ("t", "T"):
				if not self.is_test and len(novels) > 0:
					if not askYN("變為測試模式將會刪除之前輸入的爬蟲請求，確定？"):
						continue
					novels = []
				self.is_test = not self.is_test
				continue
			elif address in ("ok", "", "done", "start"):
				if self.is_test:
					print(f"{address}指令是爬蟲模式專用")
					continue
				elif len(novels) == 0:
					print("未輸入爬蟲請求")
					continue
				else:
					return NovelList(novels)
			elif address == "show":
				site_list.showSites()
				continue

			#test模式只需Test即可
			if self.is_test:
				return Test(address)

			site = site_list.find(address)
			if site is None:
				print("未登錄網站，請使用以下網站：")
				site_list.showSites()
				continue
			try:
				novel = Novel(site, address)
				novel.setFile()
			except:
				traceback.print_exc()
				print("出問題!!爬蟲請求未載入!!")
			else:
				novels.append(novel)

class NovelList:
	def __init__(self, lst):
		self.data = lst

	def __iter__(self):
		lst = [enumerate(i) for i in self.data]
		while len(lst) > 0:
			for i in lst[:]:
				try:
					yield next(i)
				except StopIteration:
					lst.remove(i)
		self.data = []

if __name__ == "__main__":
	site_list = SiteList()
	input_collector = InputCollector()
	while True:
		novels = input_collector.input(site_list)

		#跑的部分
		try:
			if input_collector.is_test:
				novels.test(site_list)
			else:
				for cnt, page in novels:
					page.text(cnt)
		except:
			traceback.print_exc()
			print("出問題!!重來!!")
			for novel in novels:
				novel.closeFile()

