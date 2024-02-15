import netbug4
if __name__ == "__main__":
    site_list = netbug4.SiteList()
    while True:
        url = input("url:")
        site = site_list.find(url)
        bs, _ = site.trans(url)
        ans = netbug4.runCode(bs, site.fpreread)
        print(ans)