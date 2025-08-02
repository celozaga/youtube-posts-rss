import requests
from bs4 import BeautifulSoup
import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

# Altere pelo ID do canal desejado (ex: UC... etc)
CHANNEL_ID = "UCO6axYvGFekWJjmSdbHo-8Q"

URL = f"https://www.youtube.com/channel/{CHANNEL_ID}/posts"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_posts():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Ainda não há HTML "estático" completo da aba Posts
    # Precisaremos adaptar quando o YouTube atualizar a estrutura
    # Exemplo alternativo: usar RSSHub e replicar a lógica
    posts = []

    for script in soup.find_all("script"):
        if "ytInitialData" in script.text:
            data = script.string
            # Aqui seria o parsing com json.loads e regex para extrair texto
            # Exige mais detalhamento técnico (posso ajudar se quiser essa versão)

    return posts

def build_rss(posts):
    rss = Element('rss')
    rss.set('version', '2.0')
    channel = SubElement(rss, 'channel')

    SubElement(channel, 'title').text = "YouTube Community Posts"
    SubElement(channel, 'link').text = URL
    SubElement(channel, 'description').text = "Feed RSS da aba Comunidade do YouTube"

    for post in posts:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = post['title']
        SubElement(item, 'description').text = post['text']
        SubElement(item, 'pubDate').text = post['date'].strftime('%a, %d %b %Y %H:%M:%S GMT')
        SubElement(item, 'link').text = post['link']

    xml_str = tostring(rss, 'utf-8')
    pretty = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(pretty)

if __name__ == "__main__":
    posts = fetch_posts()
    build_rss(posts)
