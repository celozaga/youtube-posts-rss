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
    return None

def parse_community_posts(data):
    posts = []
    try:
        tabs = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        for tab in tabs:
            tab_renderer = tab.get("tabRenderer", {})
            if tab_renderer.get("title", "").lower() == "posts":
                contents = tab_renderer["content"]["sectionListRenderer"]["contents"][0]
                items = contents["itemSectionRenderer"]["contents"]
                for item in items:
                    thread = item.get("backstagePostThreadRenderer", {}).get("post", {}).get("backstagePostRenderer", {})
                    if thread:
                        runs = thread.get("contentText", {}).get("runs", [])
                        text = ''.join([r.get("text", "") for r in runs])
                        post_id = thread.get("postId")
                        link = f"https://www.youtube.com/post/{post_id}"
                        posts.append({
                            "text": text,
                            "link": link,
                            "date": datetime.now(timezone.utc)
                        })
    except Exception as e:
        print("Erro ao extrair posts:", e)
    return posts

def build_rss(posts):
    rss = Element('rss', version="2.0")
    channel = SubElement(rss, 'channel')
    SubElement(channel, 'title').text = "YouTube Community Feed"
    SubElement(channel, 'link').text = URL
    SubElement(channel, 'description').text = "Public community posts feed"

    for post in posts:
        item = SubElement(channel, 'item')
        SubElement(item, 'description').text = post["text"]
        SubElement(item, 'link').text = post["link"]
        SubElement(item, 'pubDate').text = post["date"].strftime('%a, %d %b %Y %H:%M:%S GMT')

    xml_str = tostring(rss, encoding='utf-8')
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
