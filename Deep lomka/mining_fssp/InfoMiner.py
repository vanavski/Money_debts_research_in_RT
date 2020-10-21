import requests
import time
import pandas as pd
import os
import datetime
import warnings
import json
import re
from Person import Person
from RequestsBrain import RequestsBrain
from Database import Database

class DataMiner(object):
    requests_brain = None
    database = None

    def __init__(self):
        self.requests_brain = RequestsBrain()
        self.database = Database()

    # change method
    def get_old_json(self, person):
        sqr = {
            "token": self.requests_brain.token,
            "request": []}

        for i in range(0, 50):
            item = {"type": 1,
                    "params": {"firstname": person.firstName, "lastname": person.lastName,
                               "secondname": person.secondName, "region": i + 1,
                               "birthdate": person.birthday
                               }}
            sqr['request'].append(item)

        return sqr


    def execute_data_miner(self, command_number):
        dataset = self.database.load_person_dataset()

        if (command_number == 1):
    #   берем первые 50 элементов,  получить индексы, закинуть в жсон, проставить статус 2
            persons_50, indexes = self.database.load_50_person_for_json(dataset)
            p_json = self.get_json(persons_50)

            status, result_data = self.get_info(p_json, indexes)
        else:
            counter = 0
            # index_status_array = []
            for i in range(len(dataset)):
                if (dataset['status'][i] != 0):
                    # сто запросов в час
                    if (counter < 100):
                        print('Время обработки запроса: {}'.format(datetime.datetime.now()))
                        print('запрос номер: {}'.format(counter))
                        print('i: {}'.format(i))
                        person = Person(dataset['first_name'][i], dataset['last_name'][i])
                        status, result_data = self.requests_brain.single_request(person)
                        print('status: {}'.format(status))

                        self.database.update_people_status_single_requests(i, status)

                        if status == 0:
                            self.database.save_data_to_result_dataset(result_data)
                        elif status == 429:
                            print('429, break')
                            break
                        counter += 1
                    else:
                        print('Запросы кончились')
                        break

    def get_json(self, people_50):
        if len(people_50) > 50:
            print('на вход подано больше 50 людей')
            return 0

        sqr = {
            "token": self.requests_brain.token,
            "request": []}

        for i in range(0, 50):
            item = {"type": 1,
                    "params": {"firstname": people_50['first_name'][i],
                               "secondname": people_50['second_name'][i], "region": 16
                               }}
            sqr['request'].append(item)

        return sqr

    def get_info(self, json_item, indexes):
        # получаем ответ по стартовому жсону, смотрим на его статус
        response_start_json = self.requests_brain.get_response_by_start_json(json_item)

        self.requests_brain.set_response_status(response_start_json['code'])

        # если статус 429, чекаем непроверенные жсоны в бд
        if(self.requests_brain.is_server_limit == 429):
            # загружаем бд и проверяем таски, которые еще не обработались
            task_db = self.database.load_tasks_db()
            tasks_db_2 = task_db[task_db['status'] != 0]
            # maybe need to use for iterations
            if (len(tasks_db_2) > 0):

                # вытаскиваем первый такой таск, нужно как-то вынести его индекс,
                # чтобы потом обновить, если таск обработаем и получим данные

                task = tasks_db_2['task'][0]
                indexes = [tasks_db_2['index1'][0], tasks_db_2['index2'][0]]

                status, result_data = self.get_status_and_data(task, indexes, response_start_json)

                if (status == 0):
                    # обновить в бд статус на таск
                    self.database.update_task_status(task_db, task, status)

                return status, result_data, indexes

            else:
                sys_status = 429
                task = 'нет свободных тасков'
                return sys_status, task, indexes

        elif (self.requests_brain.is_server_limit == 0):
            task = response_start_json['response']['task']
            # добавить таск в базу данных для отслеживания, если статус будет 2
            self.database.load_data_to_task_db(task, 2, indexes)

            status, result_data = self.get_status_and_data(task, indexes, response_start_json)

            # после обновить значения в базе данных людей по индексам
            if (status == 0):
                self.database.update_task_status(task, status)

            return status, result_data, indexes

        else:
            print(self.requests_brain.is_server_limit)

    def get_status_and_data(self, task, indexes):
        response = self.requests_brain.GetTaskState(task)
        self.database.load_data_to_task_db(task, response['status'], indexes)
        if (self.requests_brain.is_server_limit != 0):
            return self.requests_brain.is_server_limit, response

        # ТОЛЬКО БЛЯТЬ ЗДЕСЬ ПОЛУЧАЮ РЕЗУЛЬТАТ ПО ТАСКУ НОРМАЛЬНЫЙ КАКОГО ХУЯ
        result_data = self.requests_brain.get_result_json_by_task(task)
        if (self.requests_brain.is_server_limit == 0):
            return self.requests_brain.is_server_limit, result_data

        else:
            return self.requests_brain.is_server_limit, result_data


# first
miner = DataMiner()
# добавить время начала, индексы, какой идет из 100 и время обработки каждого элемента
miner.execute_data_miner(2)


# per = Person('Ренат', 'Булатов', 'Мирзезянович', '30.11.1980')
# per.firstName
# # переработать загрузку в жсон по разным людям из файла
# json_item = miner.get_old_json(per)
#
# status, token, indxs = miner.get_info(json_item, [0, 49])
# print('status: {}'.format(status))
# print('token: {}'.format(token))

# second
# TODO: проверить код на проверку чисто таска
# miner = DataMiner()
# result_data = miner.requests_brain.get_result_json_by_task('f5636ee9-65d3-4db8-b097-3098a68bb8e6')
# print(result_data)

# TODO: написать код на проверку обработки людей