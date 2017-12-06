import requests
import sqlite3
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler
from time import strftime
from pprint import pprint #serve para verificar o que tem na vareavel, parecido com var_dump do PHP
import pdb #RESPONSAVEL POR DEBUGAR O CODIGO
import os #DELETAR ARQUIVOS
from io import open as iopen
from urllib.parse import urlsplit

# VERSÃO 2.9
# BOT AINDA EM DESENVOLVIMENTO
# ATUALIZADO EM 2017-12-06
# RETIREI A PARTE DA HORA. ASSIM O BOT PODE RODAR EM QUALQUER HORARIO.

up = Updater('')


def requests_image(file_url):
    suffix_list = ['jpg', 'gif', 'png', 'tif', 'svg',]
    file_name =  urlsplit(file_url)[2].split('/')[-1]
    file_suffix = file_name.split('.')[1]
    i = requests.get(file_url)
    if file_suffix in suffix_list and i.status_code == requests.codes.ok:
        with iopen(file_name, 'wb') as file:
            file.write(i.content)
    else:
        return False


def go(bot, update):
    # pdb.set_trace() #CODIGO SERA DEBUGADO APARTIR DAQUI
    page = requests.get("https://imgur.com/gallery/hot/viral/page/1/hit?scrolled&set=0")
    soup = BeautifulSoup(page.content, 'html.parser')
    i=1
    for a in soup.find_all('a', href=True):
        if i <= 3:
            pprint (i)
            url = a['href']
            msg = "http://imgur.com"+url
            msg2 = msg
            page2 = requests.get(msg2)
            soup2 = BeautifulSoup(page2.content, 'html.parser')
            url_img = "http:"+soup2.find_all('img')[0]['src']
            exten = url_img.split('.')
            suffix = exten[3]
            nome_arquivo = url_img.split('/')
            nome_file = nome_arquivo[3]
            if(suffix == "jpg" or suffix == "png"):
                descricao_img = soup2.find_all('p')[0].get_text()
                if descricao_img == "Use old embed code":
                    descricao_img = " " + url_img
                # print (descri_img)
                titulo_img = soup2.select('h1.post-title')[0].text.strip()
                descri_img = titulo_img + "\n" +descricao_img
                conn = sqlite3.connect("imgur.db")
                cursor = conn.cursor()
                sql = "SELECT * FROM imgur WHERE url=?"
                cursor.execute(sql, [(msg2)])
                user1 = cursor.fetchone() #retrieve the first row
                if(user1 == None):
                    requests_image(url_img)
                    cursor.execute("INSERT INTO imgur (url, url_img, descri_img, nome_file) VALUES (?,?,?,?)", (msg2,url_img,descri_img,nome_file,))
                    conn.commit()
                    conn.close()
                    msg += "\n" + descri_img
                    # msg += "\n Este Bot Ainda esta em fase de testes. Qualquer problema, por favor, informe @FelipeFM."
                    channel = "@ChannelBotImgur"
                    # bot.send_message(chat_id=channel, text=descri_img, photo=open(nome_file, 'rb'))
                    bot.send_photo(chat_id=channel, photo=open(nome_file, 'rb'), caption=descri_img) #SÓ ENVIA 200 CARACTERES NA DESCRIÇÃO DA FOTO
                    print(nome_file+" Imagem enviada para o canal.")
                    os.remove(nome_file) #REMOVO A FOTO QUE SALVEI
                    print(nome_file + " Imagem removida do HD.")
                else:
                    print (nome_file + " Imagem ja existe no banco de dados.")
            i+=1

up.dispatcher.add_handler(CommandHandler('go', go))

up.start_polling()
