import requests
import time
import pandas as pd
import os
import datetime
import warnings
import json
import re
from Person import Person


class DataDownloader(object):
    apiUrl = None
    token = None
    # token1 = None
    is_server_limit = None
    #     code_region_db = None
    current_region = None

    def __init__(self):
        self.apiUrl = "https://api-ip.fssprus.ru/api/v1.0/"
        self.token = self.get_token()

    #         self.token1 = self.get_token1()
    #         self.code_region_db = self.__init_code_region()

    #     def __init_code_region(self):
    #         db = pd.read_csv('KOD_region.csv')
    #         return db

    def get_token(self):
        tok = open('token.txt')
        token = tok.read()
        token = token.split('\n')
        return token[0]

    def to_string(self, person):
        result = "&region={}&firstname={}&lastname={}&secondname={}&birthday={}".format(person.region, person.firstName,
                                                                                        person.lastName,
                                                                                        person.secondName,
                                                                                        person.birthday)
        return result

    def GetTaskState(self, task):
        comStr = 'status?token={}&task={}'.format(self.token, task)
        resp = self.GetTaskCommand(comStr)
        print(' ')
        print(resp)
        print(' ')
        if (resp.get('code') != None):
            self.is_server_limit = resp['code']

        return resp['response']['status']

    def GetTaskCommand(self, comStr):
        line = self.apiUrl + comStr
        #     print(line)
        r = requests.get(line)
        return r.json()

    def get_result_json_by_task(self, task):
        comStr = 'result?token={}&task={}'.format(self.token, task)
        line = self.apiUrl + comStr
        #     print(line)
        r = requests.get(line)
        if (r.json()['code'] == 429):
            self.is_server_limit = 429
        return r

    def add_to_db(self, data):
        # если папка существует
        if (os.path.exists('db')):
            print('Database exists')
            #     зайти в папку
            os.chdir('db')
            #     проверить файл в папке
            if not os.path.isfile('dataset.xlsx'):

                #         создать файл
                db = pd.DataFrame(
                    columns=['name', 'lastname', 'secondname', 'birthday', 'hometown', 'number_ip', 'credit', 'details',
                             'department', 'status'])

                db = pd.concat([db, data])
                db.to_excel('dataset.xlsx')
            else:
                db = pd.read_excel('dataset.xlsx')
                db = pd.concat([db, data])
                db.to_excel('dataset.xlsx')

            db = pd.read_excel('dataset.xlsx')
            db = db[db.columns.drop(list(db.filter(regex='^Unnamed')))]
            db.to_excel('dataset.xlsx')

            os.chdir('..')
            return db
        # если не существует
        else:
            print('Database doesn\'t exist')
            os.makedirs('db')
            os.chdir('db')
            db = pd.DataFrame(
                columns=['name', 'lastname', 'secondname', 'birthday', 'hometown', 'number_ip', 'credit', 'details',
                         'department', 'status'])
            db = pd.concat([db, data])
            #         db = db.loc[:, ~db.columns.str.contains('^Unnamed')]
            #         db.to_excel('dataset.xlsx')
            #         db = pd.read_excel('dataset.xlsx')
            db = db[db.columns.drop(list(db.filter(regex='^Unnamed')))]
            db.to_excel('dataset.xlsx')
            os.chdir('..')
            return db

    def new_init(self):
        warnings.filterwarnings('ignore')
        df = self.load_tables()

        for i in range(len(df)):
            print(" ")
            print("Обрабатывается {}й человек".format(i))
            if (len(df[df['СТАТУС'] != 0]) > 0):
                if (df['СТАТУС'][i] != 0):
                    self.check_req_limits()
                    if (self.is_server_limit == 429):
                        return self.is_server_limit

                    person = self.create_person(df['ФИО'][i], df['ДАТА'][i])
                    if (person != None):
                        code = self.get_person_info(person)
                        if (code == 429 or code == 430):
                            df = df[df['СТАТУС'] != 0]
                            df.to_excel('input.xlsx')
                            return self.is_server_limit
                        elif (code == 0):
                            df['СТАТУС'][i] = 0
                            df.to_excel('input.xlsx')
            else:
                break

        df.to_excel('input.xlsx')

        return self.is_server_limit

    def get_response_by_start_json(self, js):
        url = self.apiUrl + 'search/group'
        data = json.dumps(js)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=data, headers=headers)
        return r.json()

    def create_person(self, fio, date):
        fio_split = fio.split(' ')
        if len(fio_split) == 3:
            first_name = fio_split[1]
            second_name = fio_split[0]
            last_name = fio_split[2]
        else:
            print('Некорректно введенное ФИО {}'.format(fio))
            return None

        is_letter_contains = re.search('[a-zA-Zа-яА-Я]', date)
        if (is_letter_contains == None):
            date = self.create_date(date)
        else:
            print('Некорректно введенная дата рождения {}'.format(date))
            return None

        person = Person(first_name, second_name, last_name, date)
        return person

    def create_date(self, date):
        datespl = date.split(".")
        if (len(datespl) > 3):
            date = datespl[2] + '.' + datespl[1] + '.' + datespl[0]
        return date

    def get_person_info(self, person):
        js1 = self.get_json(person)

        self.get_info(js1)
        if (self.is_server_limit == 429):
            if (js1['token'] == self.token):
                js1['token'] == self.token1
                self.get_info(js1)
            elif (js1['token'] == self.token):
                js1['token'] == self.token
                self.get_info(js1)
            else:
                print('сервер не отвечает, перезапуск через минуту')
                time.sleep(60)
                js1['token'] == self.token1
                self.get_info(js1)
            # return self.is_server_limit

        if (self.is_server_limit == 429):
            print('Программа ожидает снятия ограничений сервера')

        #         self.get_info(js2)
        #         if (self.is_server_limit == 429):
        #             if (js2['token'] == self.token):
        #                 js2['token'] == self.token1
        #                 print('Меняем токен')
        #                 self.get_info(js2)
        #             elif (js2['token'] == self.token):
        #                 js2['token'] == self.token
        #                 print('Меняем токен')
        #                 self.get_info(js2)
        #             else:
        #                 print('сервер не отвечает, перезапуск через минуту')
        #                 time.sleep(60)
        #                 js2['token'] == self.token1
        #                 self.get_info(js2)
        return self.is_server_limit

    def get_info(self, js, indexes):
        r = self.get_response_by_start_json(js)
        #         print(' ')
        #         print(r)
        #         print(' ')

        # if 429, check into xl last task
        self.check_response_status(r['code'])
        if(self.is_server_limit == 429):
            tasks_db = pd.read_excel('tasks.xlsx')
            tasks_db = tasks_db[tasks_db.columns.drop(list(tasks_db.filter(regex='^Unnamed')))]
            tasks_db = tasks_db[tasks_db['status'] != 0]
            # maybe need to use for iterations
            if (len(tasks_db) > 0):
                task = tasks_db['task'][0]
                status = self.GetTaskState(task)

                tasks_db = pd.read_excel('tasks.xlsx')
                tasks_db = tasks_db[tasks_db.columns.drop(list(tasks_db.filter(regex='^Unnamed')))]
                length = len(tasks_db)
                tasks_db.loc[length, 'task'] = task
                tasks_db.loc[length, 'status'] = status
                tasks_db.loc[length, 'time'] = datetime.datetime.now()
                tasks_db.loc[length, 'index1'] = indexes[0]
                tasks_db.loc[length, 'index2'] = indexes[1]
                tasks_db.to_excel("tasks.xlsx")

            else: return 'статус 429, нет свободных тасков', None

        if (self.check_response_status(r['code'])):
            if (r['code'] == 0):
                task = r['response']['task']
                status = self.GetTaskState(task)
                if (self.is_server_limit == 429):
                    return self.is_server_limit, r

                #                 add task to xl

                #                 start_time = time.time()
                #                 while (status != 0):
                #                     time.sleep(3)
                # status = self.GetTaskState(task)

                tasks_db = pd.read_excel('tasks.xlsx')
                tasks_db = tasks_db[tasks_db.columns.drop(list(tasks_db.filter(regex='^Unnamed')))]
                length = len(tasks_db)
                tasks_db.loc[length, 'task'] = task
                tasks_db.loc[length, 'status'] = status
                tasks_db.loc[length, 'time'] = datetime.datetime.now()
                tasks_db.loc[length, 'index1'] = indexes[0]
                tasks_db.loc[length, 'index2'] = indexes[1]
                tasks_db.to_excel("tasks.xlsx")

                if (self.is_server_limit == 429):
                    return self.is_server_limit, task

            if (self.get_result(task)):
                return 0, r

            else:
                return self.is_server_limit, r

        else:
            print('произошла херня')

    def get_result(self, task):
        result = self.get_result_json_by_task(task)
        if (self.is_server_limit == 429):
            return False

        #         ts = pd.read_excel('timing.xlsx')
        #         el_ind = len(ts)
        #         req = result.json()['status']
        #         ts.loc[el_ind, 'request'] = req
        #         ts.loc[el_ind, 'time'] = datetime.datetime.now()
        #         ts = ts[ts.columns.drop(list(ts.filter(regex='^Unnamed')))]
        #         ts.to_excel('timing.xlsx')
        #         print('Отработало')

    def add_data_by_json(self, result):
        dt = pd.DataFrame(
            columns=['name', 'lastname', 'secondname', 'birthday', 'hometown', 'number_ip', 'credit', 'details',
                     'department', 'status'])

        resp_count = 0
        #     вытаскиваем жсон
        length = len(result.json()['response']['result'])
        for i in range(length):
            res = result.json()['response']['result'][i]['result']

            if (res != None):
                length_res = len(res)
                if (length_res) > 0:
                    resp_count += 1
                for j in range(0, length_res):
                    el = len(dt)
                    spl = res[j]['name'].split()
                    dt.loc[el, 'name'] = spl[1]
                    dt.loc[el, 'lastname'] = spl[0]
                    dt.loc[el, 'secondname'] = spl[2]
                    dt.loc[el, 'birthday'] = spl[3]
                    s = ''
                    len_s = len(spl)
                    for k in range(4, len_s):
                        s += ' ' + spl[k]
                    dt.loc[el, 'hometown'] = s
                    dt.loc[el, 'number_ip'] = res[j]['exe_production']
                    dt.loc[el, 'credit'] = res[j]['subject']
                    dt.loc[el, 'details'] = res[j]['details']
                    dt.loc[el, 'department'] = res[j]['department']
                    dt.loc[el, 'status'] = res[j]['ip_end']

        #     добавляем обработанного челика в общую бд
        db = self.add_to_db(dt)

        return True

    def check_response_status(self, code):
        if (code == 401):
            print('invalid token')
            self.is_server_limit = code
        elif (code == 400):
            print("invalid request params. Code 400")
            self.is_server_limit = code
        elif (code == 429):
            print('Перезапустите программу. Code 429: чрезмерное количество запросов')
            self.is_server_limit = code
        else:
            return True
        return False

    def get_json(self, person):
        sqr = {
            "token": self.token,
            "request": []}

        for i in range(0, 50):
            item = {"type": 1,
                    "params": {"firstname": person.firstName, "lastname": person.lastName,
                               "secondname": person.secondName, "region": i + 1,
                               "birthdate": person.birthday
                               }}
            sqr['request'].append(item)

        return sqr

    def check_req_limits(self):
        ts = pd.read_excel('timing.xlsx')
        ts = ts[ts.columns.drop(list(ts.filter(regex='^Unnamed')))]

        сount_hour = \
            ts[(ts['time'] > (datetime.datetime.now() - datetime.timedelta(hours=1))) & (ts['request'] == 'success')][
                'time'].count()
        count_day = \
            ts[(ts['time'] > (datetime.datetime.now() - datetime.timedelta(days=1))) & (ts['request'] == 'success')][
                'time'].count()

        if сount_hour > 100 or count_day > 1000:
            self.is_server_limit = 429

    def load_tables(self):
        df = pd.read_excel('input.xlsx')
        df = df[df.columns.drop(list(df.filter(regex='^Unnamed')))]
        df['ДАТА'] = df['ДАТА'].astype(str)
        len_df = len(df)
        for i in range(len_df):
            df['ДАТА'][i] = df['ДАТА'][i].replace('-', '.')
            df['ДАТА'][i] = df['ДАТА'][i].replace(' ', '.')

        return df

    def recreate_database(self):
        input_db = pd.DataFrame(columns=['ФИО', 'ДАТА', 'СТАТУС'])
        input_db.to_excel('input.xlsx')

        timing_db = pd.DataFrame(columns=['request', 'time', 'resp_count'])
        timing_db.to_excel('timing.xlsx')

        with open("token.txt", "w") as file:
            file.write("")

d = DataDownloader()
per = Person('МАРИАННА', 'АРМЕНАКОВНА', 'АВАКЯН', '20.02.1975')
per.firstName


# переделать получение жсона для множества людей
js1 = d.get_json(per)

# отладка по методу
status, token = d.get_info(js1, [0, 49])
print('status: {}'.format(status))
print('token: {}'.format(token))