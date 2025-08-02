import requests
import re
import json
import sys
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

def fetch_posts(channel_id):
    url = f"https://www.youtube.com/channel/{channel_id}/community"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao buscar a página do canal {channel_id}: {e}")
        return []

    match = re.search(r"var ytInitialData = ({.*?});</script>", html, re.DOTALL)
    if not match:
        print(f"[ERRO] ytInitialData não encontrado para o canal {channel_id}.")
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"[ERRO] Falha ao decodificar JSON do canal {channel_id}: {e}")
        return []

    posts = []
    try:
        tabs = data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
        for tab in tabs:
            title = tab.get("tabRenderer", {}).get("title", "").lower()
            tab_id = tab.get("tabRenderer", {}).get("tabIdentifier", "")
            if title in ["posts", "comunidade"] or tab_id == "community":
                section_contents = tab["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
                items = section_contents[0]["itemSectionRenderer"]["contents"]
                for item in items:
                    if "backstagePostThreadRenderer" not in item:
                        continue

                    post_data = item["backstagePostThreadRenderer"]["post"]["backstagePostRenderer"]
                    post_id = post_data.get("postId")
                    post_url = f"https://www.youtube.com/post/{post_id}"
                    post_date = datetime.now(timezone.utc)

                    post_title = "Novo Post da Comunidade"
                    post_text = ""

                    # Texto do post
                    runs = post_data.get("contentText", {}).get("runs", [])
                    if runs:
                        post_text = "".join([r.get("text", "") for r in runs])

                    # Anexos
                    attachment = post_data.get("backstageAttachment", {})

                    if attachment.get("pollRenderer"):
                        poll = attachment["pollRenderer"]
                        question = poll.get("question", {}).get("runs", [])
                        if question and not post_text:
                            post_text = "".join([r.get("text", "") for r in question])
                    
                    elif attachment.get("backstageImageRenderer") and not post_text:
                        post_text = "Post com imagem."

                    elif attachment.get("videoRenderer") and not post_text:
                        post_text = "Post com vídeo."

                    if not post_text:
                        post_text = "Conteúdo não disponível."

                    posts.append({
                        "title": post_title,
                        "text": post_text,
                        "link": post_url,
                        "date": post_date,
                    })
                    print(f"[OK] Post encontrado: {post_id}")

    except Exception as e:
        print(f"[ERRO] Estrutura inesperada ao processar canal {channel_id}: {e}")
        return []

    return posts

def build_rss(posts, channel_id, filename):
    rss = Element('rss', version='2.0', **{'xmlns:atom': 'http://www.w3.org/2005/Atom'})
    channel = SubElement(rss, 'channel')

    SubElement(channel, 'title').text = f"YouTube Community Posts - {channel_id}"
    SubElement(channel, 'link').text = f"https://www.youtube.com/channel/{channel_id}/community"
    SubElement(channel, 'description').text = f"Feed RSS da aba Comunidade do YouTube para o canal {channel_id}"
    SubElement(channel, 'atom:link', {
        'href': f"https://raw.githubusercontent.com/celozaga/youtube-posts-rss/main/{filename}",
        'rel': 'self',
        'type': 'application/rss+xml'
    })

    for post in posts:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = post.get('title', 'Novo post da comunidade')
        SubElement(item, 'description').text = post.get('text', 'Conteúdo não disponível.')
        SubElement(item, 'pubDate').text = post['date'].strftime('%a, %d %b %Y %H:%M:%S GMT')
        SubElement(item, 'link').text = post['link']
        SubElement(item, 'guid', {'isPermaLink': 'false'}).text = post['link']

    xml_str = tostring(rss, 'utf-8')
    pretty = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(pretty)

def main():
    if len(sys.argv) != 3:
        print("Uso: python generate_rss.py <channel_id> <output_filename>")
        sys.exit(1)

    channel_id = sys.argv[1]
    output_filename = sys.argv[2]
    print(f"[INFO] Processando canal: {channel_id} → {output_filename}")

    posts = fetch_posts(channel_id)
    build_rss(posts, channel_id, output_filename)
    print(f"[SUCESSO] Feed RSS com {len(posts)} posts gerado em: {output_filename}")

if __name__ == "__main__":
    main()
