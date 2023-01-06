import telebot
from telebot import types
from bs4 import BeautifulSoup as bs
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

global article_themes, sub_art_themes, diff_levels

TOKEN = "#"
bot = telebot.TeleBot(TOKEN)


def headers(url):
     r = requests.get(url)
     soup = bs(r.text, "lxml")
     head = soup.find_all('h3')
     head_new = []
     for each in head:
         new = each.text
         head_new.append(new)
     return head_new

def sub_headers(url):
     r = requests.get(url)
     soup = bs(r.text, "lxml")
     sections = soup.find_all('section') 
     sub_head = list()
     for section in sections:
         first = section.find('a')
         sub_head.append(first.text)
     return sub_head
 
url_alg = 'https://ru.algorithmica.org/' 
article_themes = headers(url_alg)
sub_art_themes = sub_headers(url_alg)
   

def parser_art(word):
    url = 'https://ru.algorithmica.org/'
    r = requests.get(url)
    soup = bs(r.text, "lxml")
    sections = soup.find_all('section') 
    art_dict = dict()
    for section in sections:
        first = section.find('a').text
        items = section.find_all('a')
        art_dict[first] = {}
        for item in items:
            item_text = item.text
            item_url = item.get('href')
            art_dict[first][item_text] = item_url
    for elem in art_dict:
        if elem==word:
            return art_dict[elem]

def parser_head_art(word):
    
    
    url = 'https://ru.algorithmica.org/'
    r = requests.get(url)
    soup = bs(r.text, "lxml")
    sections = soup.find_all('section')
    headers = soup.find_all('h3')
    flag = False
    names = []
    k = 0
    for section in sections:
        first = section.find('a')
        if first.find_previous().find_previous().text==word:
            flag = True
        if flag==True:
            if first.find_previous().find_previous() in headers and k!=0:
                break
            else:
                names.append(first.text)
                k+=1
    return names

def cut_numbers(st):
    for i in range(len(st)):
        if st[i]==' ':
            break
    return st[i+1:]

def get_link(st):
    st = st.lower().split()
    new_st = ''
    for elem in st:
        if st!='-':
            new_st+=elem + '-'
    new_st = new_st[:-1:]
    return new_st
    

def parser_leetcode(diff):
    button = []
    url_problems = 'https://leetcode.com/problems/'
    s = Service('C:/Users/.../chromedriver.exe')
    driver = webdriver.Chrome(service=s)
    
    driver.get('https://leetcode.com/problemset/algorithms/')
    button = driver.find_elements(By.CLASS_NAME, 'ml-auto.cursor-pointer')[0]
    button.click()
    time.sleep(2)
    
    soup = bs(driver.page_source, 'lxml')
    flag = True
    while flag:
        try:
            task_name = soup.find_all('span', class_='mr-2 text-lg font-medium text-label-1 dark:text-dark-label-1')[0]
            flag = False
        except IndexError:
            driver.get('https://leetcode.com/problemset/algorithms/')
            button = driver.find_elements(By.CLASS_NAME, 'ml-auto.cursor-pointer')[0]
            button.click()
            time.sleep(2)
            soup = bs(driver.page_source, 'lxml')
            

    task_name =cut_numbers(task_name.text)
    task_link = url_problems + get_link(task_name)
    task = task_name + ': ' + task_link
       
    return task
    

    

@bot.message_handler(commands=['start'])
def hello_message(message):
    
    offer = '''Найду нужный тебе алгоритм из своего каталога 💻
    
Отправлю случайную задачу из leetcode ✏️

Для того чтобы продолжить, нажми на /continue и перейди в меню 📜'''

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} 🤘\nВот, что я могу:')
    bot.send_message(message.chat.id, offer)
    
    


@bot.message_handler(commands=['continue', 'back'])
def button_message(message):
    
    if message.text=='/continue' or message.text=='/back' or message.text=='Порешать задачу':
        if message.text=='/back':
             bot.send_message(message.chat.id, 'Вы вернулись назад')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = []
        items.append(types.KeyboardButton("Найти алгоритм"))
        items.append(types.KeyboardButton("Порешать задачу"))
        
        for i in range(2):
            markup.add(items[i])
            
        bot.send_message(message.chat.id,'Выберите, что Вас интересует',reply_markup=markup)
    
    elif message.text == 'Найти алгоритм':
         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
         
         for theme in article_themes:
             markup.add(types.KeyboardButton(theme))
        
         mes = '''Выберите категорию

Нажмите /back, чтобы вернуться обратно 🔙'''
            
         bot.send_message(message.chat.id, mes,reply_markup=markup)
    
    
    elif message.text in article_themes:
        word = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        options = parser_head_art(word)
        for option in options:
            markup.add(types.KeyboardButton(option))
        mes = '''Выберите категорию

Нажмите /back, чтобы вернуться обратно 🔙'''
        bot.send_message(message.chat.id, mes,reply_markup=markup)
    
        
    

@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text=="Найти алгоритм":
        button_message(message)
    elif message.text in article_themes:
        button_message(message)
        
    elif message.text in sub_art_themes:
         word = message.text
         mes = 'Вот, что я нашел по Вашему запросу ✅:\n\n'
         res = parser_art(word)
         flag = False
         for art in res:
             if flag==False:
                 mes+=f'Небольшое вступление о разделе *{art}*: {res[art]}\n\n'
                 flag = True
                 pass
             else:
                 mes+=f'{art}: {res[art]}'+'\n'
         mes+='\nНажмите /back, чтобы вернуться обратно 🔙'
         bot.send_message(message.chat.id, mes, parse_mode= 'Markdown' )
             
        
    elif message.text == 'Порешать задачу':
        text = 'Интенсивно ищу задачу 🥵\n\nПожалуйста, подождите 🙏'
        bot.send_message(message.chat.id, text, parse_mode= 'Markdown' )
        diff = message.text
        task = parser_leetcode(diff)
        mes = 'Ну, что ж, предлагаю пораскинуть мозгами над такой задачей:\n\n'
        mes+= task + '\n\n'
        mes+= 'Нажмите /back, чтобы вернуться обратно 🔙'
        bot.send_message(message.chat.id, mes, parse_mode= 'Markdown' )
             
   
    
        
bot.polling(none_stop=True, interval=0)