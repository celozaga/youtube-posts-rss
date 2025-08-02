import requests
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

CHANNEL_ID = "UCO6axYvGFekWJjmSdbHo-8Q"
URL = f"https://www.youtube.com/channel/{CHANNEL_ID}/posts"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def extract_yt_initial_data(html):
    match = re.search(r"var ytInitialData = ({.*?});</script>", html, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    else:
        return None

def parse_community_posts(data):
    posts = []
    try:
        contents = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        for tab in contents:
            tab_renderer = tab.get("tabRenderer", {})
            if "title" in tab_renderer and tab_renderer["title"].lower() == "posts":
                section = tab_renderer["content"]["sectionListRenderer"]["contents"][0]
                items = section["itemSectionRenderer"]["contents"]
                for item in items:
                    if "backstagePostThreadRenderer" in item:
                        post_data = item["backstagePostThreadRenderer"]["post"]["backstagePostRenderer"]

                        text_runs = post_data.get("contentText", {}).get("runs", [])
                        post_text = ''.join([run.get("text", "") for run in text_runs])

                        post_id = post_data.get("postId")
                        post_url = f"https://www.youtube.com/post/{post_id}"

                        timestamp_usec = int(post_data.get("publishedTimeText", {}).get("runs", [{}])[0].get("text", "0").replace("•", "").strip())

                        posts.append({
                            "title": (post_text[:50] + "...") if len(post_text) > 50 else post_text,
                            "text": post_text,
                            "link": post_url,
                            "date": datetime.now(timezone.utc)  # Data real é mais difícil de extrair, YouTube usa texto tipo "2 days ago"
                        })
    except Exception as e:
        print("Erro ao extrair posts:", e)
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

def main():
    response = requests.get(URL, headers=HEADERS)
    html = response.text

    data = extract_yt_initial_data(html)
    if not data:
        print("ytInitialData não encontrado.")
        return

    posts = parse_community_posts(data)
    if not posts:
        print("Nenhum post encontrado.")
    else:
        build_rss(posts)

if __name__ == "__main__":
    main()
