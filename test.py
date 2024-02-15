import netbug4
if __name__ == "__main__":
    site_list = netbug4.SiteList()
    url = input("url:")
    site = site_list.find(url)
    test = netbug4.Test(site, url)
    code = test.makeCode()
    print(f"CODE:\n{code}")