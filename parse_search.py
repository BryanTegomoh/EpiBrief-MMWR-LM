from bs4 import BeautifulSoup
html=open('tmp_search73.html','r',encoding='utf-8').read()
s=BeautifulSoup(html,'html.parser')
links=[a['href'] for a in s.select('a[href]') if '/mmwr/volumes/73/wr/mm73' in a['href'] and a['href'].endswith('.htm')]
print(len(links))
print(links[:10])
