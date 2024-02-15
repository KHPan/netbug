import netbug4
if __name__ == "__main__":
    site_list = netbug4.SiteList()
    while True:
        url = input("url:")
        site = site_list.find(url)
        if site is None:
            site = netbug4.Site()
        print(site.trans(url, is_test = True).prettify())