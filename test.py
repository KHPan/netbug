from netbug4 import *
import sys
from PyQt5 import QtWidgets, QtCore
if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	widget = QtWidgets.QWidget()
	widget.resize(360, 360)
	widget.setWindowTitle("hello, pyqt5")
	widget.show()
	sys.exit(app.exec_())
	'''site_list = netbug4.SiteList()
	url = "https://big5.quanben5.com/n/shouchangmishu/"#input("url:")
	site = site_list.find(url)
	netbug4.Test(site, url, site_list)'''