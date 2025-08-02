import requests
import re
import json
import sys
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

def fetch_posts(channel_id):
    """Busca a página e extrai os posts do ytInitialData."""
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

    match = re.search(r"var ytInitialData = ({.*?});</script>", html, re.DOTALL)
    if not match:
        print(f"ytInitialData não encontrado para o canal {channel_id}. A estrutura da página pode ter mudado.")
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON para o canal {channel_id}: {e}")
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
                            
                            post_id = post_data.get("postId")
                            post_url = f"https://www.youtube.com/post/{post_id}"
                            post_date = datetime.now(timezone.utc)
                            
                            post_title = ""
                            post_text = ""
                            
                            # Extrai o texto principal, se existir
                            content_text_runs = post_data.get("contentText", {}).get("runs", [])
                            if content_text_runs:
                                post_text = "".join([run.get("text", "") for run in content_text_runs])

                            # Verifica se o post tem anexo de vídeo e extrai os dados
                            if "backstageAttachment" in post_data:
                                attachment = post_data["backstageAttachment"]
                                if "videoRenderer" in attachment:
                                    video_data = attachment["videoRenderer"]
                                    # Usa o título do vídeo como título do feed
                                    if "title" in video_data and "runs" in video_data["title"]:
                                        post_title = "".join([run.get("text", "") for run in video_data["title"]["runs"]])
                                    
                                    video_id = video_data.get("videoId")
                                    if video_id:
                                        # Cria o link direto para o vídeo
                                        post_url = f"https://www.youtube.com/post/UgkxVnahkiK{video_id}"
                                    
                                    if "descriptionSnippet" in video_data and "runs" in video_data["descriptionSnippet"]:
                                        post_text = "".join([run.get("text", "") for run in video_data["descriptionSnippet"]["runs"]])
                                        
                            # Se o post é uma enquete
                            elif "backstageAttachment" in post_data and "pollRenderer" in post_data["backstageAttachment"]:
                                poll_question_runs = post_data["backstageAttachment"]["pollRenderer"]["question"].get("runs", [])
                                if poll_question_runs:
                                    post_title = "".join([run.get("text", "") for run in poll_question_runs])
                                    if not post_text:
                                        post_text = post_title
                                    
                            # Se o post tem texto principal (sem anexo de video/enquete), usa-o para o título
                            if not post_title and post_text:
                                post_title = (post_text[:100] + "...") if len(post_text) > 100 else post_text
                            elif not post_title:
                                post_title = "Novo Post da Comunidade"

                            posts.append({
                                "title": post_title,
                                "text": post_text,
                                "link": post_url,
                                "date": post_date,
                            })
                            print(f"Post encontrado: {post_id}")
    except KeyError as e:
        print(f"Estrutura do JSON inesperada para o canal {channel_id}. Chave ausente: {e}. A estrutura da página pode ter mudado.")
        return []
    
    return posts

def build_rss(posts, channel_id, filename):
    """Cria e salva o arquivo RSS com os posts extraídos."""
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
        
        post_title = post.get('title', 'Novo post da comunidade')
        SubElement(item, 'title').text = post_title
        
        description_content = post.get('text', 'Conteúdo não disponível.')
        SubElement(item, 'description').text = description_content
        
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
