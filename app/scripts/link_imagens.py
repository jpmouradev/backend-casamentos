import requests
from bs4 import BeautifulSoup
import time


def pegar_link_imagem(url_pagina):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        resposta = requests.get(url_pagina, headers=headers, timeout=15)
        resposta.raise_for_status()

        soup = BeautifulSoup(resposta.text, "html.parser")

        meta = soup.find("meta", property="og:image")

        if meta:
            return meta["content"]

        return None

    except Exception as e:
        print(f"Erro: {url_pagina} -> {e}")
        return None


with open("links.txt", encoding="utf-8") as f:
    links = [linha.strip() for linha in f if linha.strip()]


with open("imagens.html", "w", encoding="utf-8") as saida:

    for i, link in enumerate(links, start=1):

        print(f"{i}/{len(links)}")

        imagem = pegar_link_imagem(link)

        if imagem:
            saida.write(f'<img src="{imagem}" alt="">\n')

        time.sleep(0.5)

print("Finalizado!")
