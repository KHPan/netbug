import netbug4
if __name__ == "__main__":
	str1 = "end"*100
	str2 = "start"*80
	str3 = "value"*90
	netbug4.print2((str1, str2, str3))
	site_list = netbug4.SiteList()
	print(" \u2588 ")
	print("len:", len(" \u2588 "))
	url = input("url:")
	site = site_list.find(url)
	test = netbug4.Test(site, url)
	test.test(site_list)