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
