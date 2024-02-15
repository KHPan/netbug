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