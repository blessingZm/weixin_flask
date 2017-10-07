import requests
from bs4 import BeautifulSoup


url = 'http://m.weather.com.cn/mweather/101200901.shtml'
# header = {
#     "User-Agent":	"Mozilla/5.0 (Windows NT 10.0; …) Gecko/20100101 Firefox/56.0"
# }
res = requests.get(url)
soup = BeautifulSoup(res.content, 'lxml')
print(soup)
updateTime = soup.find('span', class_='flfx iconli')
print(updateTime)
