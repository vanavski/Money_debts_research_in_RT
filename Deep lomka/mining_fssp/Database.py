import pandas as pd
import datetime
import os

class Database(object):
    def save_data_to_result_dataset(self, data):
        dt = pd.DataFrame(
            columns=['name', 'lastname', 'secondname', 'birthday', 'hometown', 'number_ip', 'credit', 'details',
                     'department', 'status'])

        resp_count = 0

        length = len(data['response']['result'])
        for i in range(length):
            res = data['response']['result'][i]['result']

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
                    columns=['name', 'lastname', 'secondname', 'birthday', 'hometown', 'number_ip', 'credit',
                             'details',
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


    def load_person_dataset(self):
        dataset = pd.read_excel('person_dataset.xlsx')
        return dataset

    def load_50_person_for_json(self, dataset):
        inds = dataset.index[dataset[:49]].tolist()
        indexes = [inds[0], inds[49]]
        dataset = dataset[dataset[inds[0]:inds[49]]]
        for i in range(len(dataset)):
            dataset['status'][i] = 2
        return dataset, indexes

    def update_people_status(self, status, indexes):
        df = self.load_person_dataset()
        for i in range(indexes[0], indexes[1]):
            df['status'][i] = status
        df.to_excel('person_dataset.xlsx')

    def update_people_status_single_requests(self, index, status):
        df = self.load_person_dataset()
        df.loc[index, 'status'] = status
        df.to_excel('person_dataset.xlsx')



    def load_tasks_db(self):
        tasks_db = pd.read_excel('tasks.xlsx')
        tasks_db = tasks_db[tasks_db.columns.drop(list(tasks_db.filter(regex='^Unnamed')))]
        return tasks_db

    def load_data_to_task_db(self, task, status, indexes):
        tasks_db = pd.read_excel('tasks.xlsx')
        tasks_db = tasks_db[tasks_db.columns.drop(list(tasks_db.filter(regex='^Unnamed')))]
        length = len(tasks_db)
        tasks_db.loc[length, 'task'] = task
        tasks_db.loc[length, 'status'] = status
        tasks_db.loc[length, 'time'] = datetime.datetime.now()
        tasks_db.loc[length, 'index1'] = indexes[0]
        tasks_db.loc[length, 'index2'] = indexes[1]
        tasks_db.to_excel("tasks.xlsx")

    def update_task_status(self, task, status):
        task_db = pd.read_excel('tasks.xlsx')
        task_db = task_db[task_db.columns.drop(list(task_db.filter(regex='^Unnamed')))]
        inds = task_db.index[task_db['task'] == task].tolist()
        task_db.iloc[inds[0], 'status'] = status
        task_db.to_excel('tasks.xlsx')
