import netbug4
import requests
from bs4 import BeautifulSoup
if __name__ == "__main__":
    response = requests.get("https://ixdzs8.tw/read/339561/p1707.html")
    bs = BeautifulSoup(response.text, "lxml")
    run = netbug4.Run(bs)
    while True:
        inp = input()
        run.run(inp)
        netbug4.print2((run.div.prettify(),))