import requests
from bs4 import BeautifulSoup
from gtts import gTTS


"""берем слова и картинки с сайта"""
class GetEnglishWords:
    def __init__(self):
        self.list_eng = list()
        self.list_rus = list()
        self.list_images = list()
        self.list_sounds = list()
        self.base_url = 'https://kreekly.com'

    def run(self, url):
        full_page = requests.get(url)

        soup = BeautifulSoup(full_page.text, 'lxml')
        convert = soup.find_all("div", class_="dict-word")
        con_soup = BeautifulSoup(str(convert), 'html.parser')
        words_eng = con_soup.find_all("span", class_="eng")  # список английских слов
        words_rus = con_soup.find_all("span", class_="rus")  # список русских слов
        img_tags = con_soup.find_all('img')  # список путей картинок

        for i in range(0, len(img_tags)):
            # добавлеие озвучки слова
            tts = gTTS(text=words_eng[i].text, lang='en')
            save_name = "Sounds/" + words_eng[i].text + ".mp3"
            tts.save(save_name)
            self.list_sounds.append(save_name)
            # добавление русского и английского слова
            self.list_eng.append(words_eng[i].text)
            self.list_rus.append(words_rus[i].text)
            # получение картинки
            img_url = self.base_url + img_tags[i]['src']
            img_data = requests.get(img_url).content

            with open("Images/" + words_eng[i].text + ".jpg", 'wb') as f:  # добавление картинок в новый список
                self.list_images.append("Images/" + words_eng[i].text + ".jpg")
                f.write(img_data)

        return self.list_eng, self.list_rus, self.list_images, self.list_sounds