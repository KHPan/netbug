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
import itertools
cc=OpenCC("s2tw")
import collections

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

def print2(strs):		#並排寫多段字串並加分隔線
	rows, _ = os.get_terminal_size()
	if len(strs) == 1:
		print(str[0])
	else:
		separator = " \u2588 "
		ele_width = (rows + len(separator)) // len(strs) - len(separator)
		iters = (_custom_wrap(txt, ele_width) for txt in strs)
		for line in itertools.zip_longest(*iters, fillvalue = " " * ele_width):
			print(separator.join(line))
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
		site_file = open_file("site-data3.txt", 'r', False)
		self.data = [Site(f) for f in 
			site_file.read().split("\n--網站分隔線--\n")]
		site_file.close()
		
	def find(self, sub_address):
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
		site_file = open_file("netbug-data3.txt", 'w', False)
		site_file.write("\n--網站分隔線--\n".join(
			map(str, self.data)))
		site_file.close()
		
	def __contains__(self, site_data):
		return site_data in self.data

class Site:
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

RunData = collections.namedtuple("RunData", "cnt, bs, address")

