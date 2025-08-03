import requests
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

# Altere pelo ID do seu canal (se o link for youtube.com/c/nomedocanal,
# você precisa encontrar o ID que começa com "UC...")
CHANNEL_ID = "UCO6axYvGFekWJjmSdbHo-8Q"

# URL da aba Comunidade do seu canal
URL = f"https://www.youtube.com/channel/{CHANNEL_ID}/community"

# Headers para simular uma requisição de navegador
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}

def fetch_posts():
    """Busca a página e extrai os posts do ytInitialData."""
    try:
        response = requests.get(URL, headers=HEADERS)
        response.raise_for_status()
        html = response.text
    except requests.RequestException as e:
        print(f"Erro ao buscar a URL: {e}")
        return []

    match = re.search(r"var ytInitialData = ({.*?});</script>", html, re.DOTALL)
    if not match:
        print("ytInitialData não encontrado. A estrutura da página pode ter mudado.")
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return []

    posts = []
    try:
        contents = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        for tab in contents:
            if "tabRenderer" in tab and tab["tabRenderer"]["title"].lower() == "posts":
                section = tab["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]
                if "itemSectionRenderer" in section:
                    items = section["itemSectionRenderer"]["contents"]
                    for item in items:
                        if "backstagePostThreadRenderer" in item:
                            post_data = item["backstagePostThreadRenderer"]["post"]["backstagePostRenderer"]
                            
                            content_text_runs = post_data.get("contentText", {}).get("runs", [])
                            post_text = "".join([run.get("text", "") for run in content_text_runs])

                            post_id = post_data.get("postId")
                            post_url = f"https://www.youtube.com/post/{post_id}"
                            post_date = datetime.now(timezone.utc)

                            posts.append({
                                "title": (post_text[:100] + "...") if len(post_text) > 100 else post_text,
                                "text": post_text,
                                "link": post_url,
                                "date": post_date,
                            })
                            print(f"Post encontrado: {post_id}")
    except KeyError as e:
        print(f"Estrutura do JSON inesperada. Chave ausente: {e}. A estrutura da página pode ter mudado.")
        return []
    
    return posts

def build_rss(posts):
    """Cria e salva o arquivo RSS com os posts extraídos."""
    rss = Element('rss')
    rss.set('version', '2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')

    channel = SubElement(rss, 'channel')
    SubElement(channel, 'title').text = "YouTube Community Posts"
    SubElement(channel, 'link').text = URL
    SubElement(channel, 'description').text = "Feed RSS da aba Comunidade do YouTube"
    SubElement(channel, 'atom:link', {
        'href': f"https://raw.githubusercontent.com/celozaga/youtube-posts-rss/main/feed.xml",
        'rel': 'self',
        'type': 'application/rss+xml'
    })

    for post in posts:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = post['title']
        
        # Correção: a descrição agora contém apenas o texto puro, sem tags
        description_content = post['text']
        SubElement(item, 'description').text = description_content
        
        SubElement(item, 'pubDate').text = post['date'].strftime('%a, %d %b %Y %H:%M:%S GMT')
        SubElement(item, 'link').text = post['link']
        SubElement(item, 'guid', {'isPermaLink': 'false'}).text = post['link']

    xml_str = tostring(rss, 'utf-8')
    pretty = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(pretty)

if __name__ == "__main__":
    posts = fetch_posts()
    if posts:
        build_rss(posts)
        print(f"Feed RSS com {len(posts)} posts gerado com sucesso.")
    else:
        print("Nenhum post encontrado para gerar o feed.")
