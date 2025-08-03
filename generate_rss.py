import requests
import re
import json
import sys
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

def find_backstage_posts(obj):
    """Busca recursivamente todos os backstagePostThreadRenderer no JSON."""
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "backstagePostThreadRenderer":
                found.append(v)
            else:
                found.extend(find_backstage_posts(v))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(find_backstage_posts(item))
    return found

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
        print(f"Erro ao buscar a URL para o canal {channel_id}: {e}")
        return []

    # Regex tolerante para o ytInitialData
    match = re.search(r"ytInitialData[\"']?\s*=\s*({.*?});", html, re.DOTALL)
    if not match:
        print(f"ytInitialData não encontrado para o canal {channel_id}. A estrutura da página pode ter mudado.")
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON para o canal {channel_id}: {e}")
        return []

    posts = []
    raw_posts = find_backstage_posts(data)
    print(f"{channel_id}: Encontrados {len(raw_posts)} posts brutos no JSON.")

    for post_data in raw_posts:
        post = post_data.get("post", {}).get("backstagePostRenderer", {})
        # Ignorar posts de vídeo se desejado
        if post.get("backstageAttachment", {}).get("videoRenderer"):
            continue

        post_id = post.get("postId")
        post_url = f"https://www.youtube.com/post/{post_id}" if post_id else ""
        post_date = datetime.now(timezone.utc) # Não há data real, mas pode adaptar se achar timestamp

        post_text = ""
        post_title = ""
        content_text_runs = post.get("contentText", {}).get("runs", [])
        if content_text_runs:
            post_text = "".join([run.get("text", "") for run in content_text_runs])
            post_title = (post_text[:60] + "...") if len(post_text) > 60 else post_text
        else:
            # Enquete
            poll_renderer = post.get("backstageAttachment", {}).get("pollRenderer")
            if poll_renderer:
                poll_question_runs = poll_renderer.get("question", {}).get("runs", [])
                poll_question = "".join([run.get("text", "") for run in poll_question_runs]) if poll_question_runs else "Enquete"
                post_text = poll_question
                post_title = poll_question
                choices = poll_renderer.get("choices", [])
                if choices:
                    post_text += "\nOpções:\n" + "\n".join([c.get("text", "") for c in choices])
            else:
                # Post apenas com imagem ou sem texto
                post_text = "Post sem texto."
                post_title = "Post sem texto."

        post_title = post_title.replace('\n', ' ').strip()
        post_text = post_text.strip()
        if not post_title:
            post_title = "Post da comunidade"
        if not post_text:
            post_text = "Conteúdo não disponível."

        posts.append({
            "title": post_title,
            "text": post_text,
            "link": post_url,
            "date": post_date,
        })

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
        SubElement(item, 'title').text = post['title']
        SubElement(item, 'description').text = post['text']
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
    print(f"Processando canal: {channel_id} para o arquivo: {output_filename}")

    posts = fetch_posts(channel_id)
    build_rss(posts, channel_id, output_filename)
    print(f"Feed RSS com {len(posts)} posts gerado com sucesso em {output_filename}.")

if __name__ == "__main__":
    main()
