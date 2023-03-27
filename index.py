import urllib3
import json
import numpy as np
import random
import ydb


endpoint_ ='grpcs://ydb.serverless.yandexcloud.net:2135'
database_ ='/ru-central1/b1gv9gb9fjrubnjut2sa/etn9v3icfe9l4jdnahls'

# create driver in global space.
driver = ydb.Driver(endpoint = endpoint_, database = database_)
# Wait for the driver to become active for requests.
driver.wait(fail_fast=True, timeout=5)
# Create the session
session = driver.table_client.session().create()
 
def save_answer(newid, chat_id, current, choice):
    query = f'INSERT INTO flat_pref (id, chatid, current, choice) VALUES ({newid}, {chat_id}, {current}, {choice});'
    print(query)
    result = session.transaction(ydb.SerializableReadWrite()).execute(
        query,
        commit_tx=True
    )


class eGreedy:
    def __init__(self, n_arms=2, e=0.01):
        self.n_arms = n_arms
        self.e = e
        self.reward_history = [[] for _ in range(n_arms)]
     
    def decide(self):
        # дернуть каждую ручку один раз для первоначальной статистики
        for arm_id in range(self.n_arms):
            if len(self.reward_history[arm_id]) == 0:
                return arm_id
         
        # если случайное число меньше epsilon, то выбрать ручку случайно и закончить
        if np.random.rand() < self.e:
            return np.random.randint(0, self.n_arms)
         
        # если случайное число не меньше epsilon, т.е. мы сюда дошли
        # посчитать средние награды на текущий момент по всем ручкмм
        mean_rewards = [np.mean(history) for history in self.reward_history]
         
        # в качестве ответа выбрать ту ручку, у которой наибольшее среднее
        return int(np.random.choice(
            np.argwhere(mean_rewards == np.max(mean_rewards)).flatten()
        ))
     
    # обновить историю полученных наград у ручки arm_id
    def update(self, arm_id, reward):
        self.reward_history[arm_id].append(reward)

 
http = urllib3.PoolManager()
 
TG_TOKEN='5610384861:AAGOkOLZDgv4yXBMQ6OKDjWwJG0Pzkl_GLc'
URL = f"https://api.telegram.org/bot{TG_TOKEN}/"
 
kb=json.dumps(
    { "inline_keyboard":
        [
            [
                { "text": "Нет", "callback_data": "no" },
                { "text": "Да", "callback_data": "yes" }
            ]
        ]
    }
)
 
choiceText = "Выбрали бы вы себе такую квартиру?"


izbutok = 'https://storage.yandexcloud.net/for-bot-mab/izbutok/{}.jpg'
nedostatok = 'https://storage.yandexcloud.net/for-bot-mab/nedostatok/{}.jpg' 
def send_pic(arm, chat_id):
    random_id = random.randint(1,20)
    urlpic = izbutok
    if arm == 1:
        urlpic = nedostatok
    final_text = urlpic.format(random_id)
    url = URL + f"sendPhoto?photo={final_text}&chat_id={chat_id}"
    http.request("GET", url)
 
def send_question(chat_id):
    # Create data dict
    data = {
        'text': (None, choiceText),
        'chat_id': (None, chat_id),
        'parse_mode': (None, 'Markdown'),
        'reply_markup': (None, kb)
    }
    url = URL + "sendMessage"
    http.request(
       'POST',
       url,
       fields=data
    )



def count_id(chat_id):
    query = f'select COUNT(id) as count_id from flat_pref where chatid = {chat_id};'
    result = session.transaction(ydb.SerializableReadWrite()).execute(
        query,
        commit_tx=True
    )
    count_ = result[0].rows[0].count_id
    #final_text = f"Всего {count_} записей в базе"
    #url = URL + f"sendMessage?text={final_text}&chat_id={chat_id}"
    #http.request("GET", url)
    return count_
    

# создаем объект бандита с двумя ручками
egreedy_policy = eGreedy(n_arms=2, e = 0.2)
# создаем глобальную переменную для текущей выбранной ручки (а еще можно сделать атрибутом в объекте eGreedy)
arm_id = 0
 
def get_next(chat_id):
    # выбираем ручку
    arm = egreedy_policy.decide()
    print(arm)
    send_pic(arm, chat_id)
    # отправляем сразу и меню
    send_question(chat_id)
    return(arm)

def handler(event, context):
    global arm_id
    message = json.loads(event['body'])
    print(message)

    if 'callback_query' in message.keys():
        # получен ответ на меню
        reply = message['callback_query']['data']
        chat_id = message['callback_query']['message']['chat']['id']
        # сохраняем
        save_answer(message["update_id"], chat_id, arm_id==1, reply == "yes")  
        
        #send_feedback(chat_id)
        
        if reply == "no":
            reward_reply = 0
        else:
            reward_reply = 1
        # обновляем
        egreedy_policy.update(arm_id = arm_id, reward = reward_reply)
        if count_id(chat_id) > 9:
            final_text = "Большое спасибо :) Мы собрали необходимое кол-во ответов. " + \
            "По всем вопросам можете писать @danilkrivoruchko"
            url = URL + f"sendMessage?text={final_text}&chat_id={chat_id}"
            http.request("GET", url)
        else:
            arm_id = get_next(chat_id) # получаем новый номер ручки, показываем картинку, выводим меню

    elif ('callback_query' not in message.keys()) and (message['message']['text'].startswith('/') == False):
        final_text = "Взаимодействие с ботом происходит только посредством кнопок :)"
        chat_id = message['message']['chat']['id']
        url = URL + f"sendMessage?text={final_text}&chat_id={chat_id}"
        http.request("GET", url)
    else:
        chat_id = message['message']['chat']['id']
        text = 'Добро пожаловать в наш маленький и шуточный телеграмм бот! ' + \
        'Представьте ситуацию, что Вам необходимо арендовать квартиру. ' +\
        'Вот только все "нормальные" квартиры пропали с рынка. ' + \
        'Остались только квартиры с рядом недостатков. ' + \
        'Вам будут предложены фотографии квартир, и Вы должны выбрать, ' + \
        'согласились бы Вы жить в этой квартире. ' + \
        'Disclaimer: (1) мы не стремимся оскорбить чьи-либо предпочтения в ремонте, ' + \
        '(2) все фотографии взяты с открытых ресурсов.' 

        url = URL + f"sendMessage?text={text}&chat_id={chat_id}"
        http.request("GET", url)
        # получаем номер ручки, показываем картинку, выводим меню
        arm_id = get_next(chat_id)

    # печатаем историю в логи для контроля
    print(egreedy_policy.reward_history)
    return {
        'statusCode': 200
    }
