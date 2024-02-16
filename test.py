import netbug4
if __name__ == "__main__":
	site_list = netbug4.SiteList()
	url = "https://big5.quanben5.com/n/shouchangmishu/"#input("url:")
	site = site_list.find(url)
	netbug4.Test(site, url, site_list)
	'''novel = netbug4.Novel(site, url)
	print(f"novel name:{novel.novelName()}")
	file_name = "test.txt"
	novel.setFile(file_name)
	for index, page in enumerate(novel.iterAll()):
		page.text(index)'''