import json
import requests
import time

class RequestsBrain(object):

    is_server_limit = None
    api_url_group = 'https://api-ip.fssprus.ru/api/v1.0/search/group'
    api_url = 'https://api-ip.fssprus.ru/api/v1.0/'

    def __init__(self):
        self.token = self.get_token()

    def get_token(self):
        tok = open('token.txt')
        token = tok.read()
        token = token.split('\n')
        return token[0]


    def get_response_by_start_json(self, js):
        data = json.dumps(js)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(self.api_url, data=data, headers=headers)
        return r.json()

    def set_response_status(self, code):
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
            self.is_server_limit = code
            return True
        return False

    def GetTaskState(self, task):
        comStr = 'status?token={}&task={}'.format(self.token, task)
        response = self.GetTaskCommand(comStr)
        # check second status code in response['response']['status'] == 0
        if (response.get('code') != None):
            self.is_server_limit = response['code']
            if (response['response'].get('status') != None):
                return response['response']['status']

    def GetTaskCommand(self, comStr):
        line = self.api_url + comStr
        r = requests.get(line)
        return r.json()

    def GetResult(self, task):
        comStr = 'result?token={}&task={}'.format(self.token, task)
        line = self.api_url + comStr
        #     print(line)
        r = requests.get(line)
        return r.json()

    def single_request(self, person):
        str = self.get_string_for_single_request(person)

        task_json = self.GetTaskCommand(str)

        if (task_json['code'] == 0):
            task_status = 2
            task = task_json['response']['task']
            counter = 0
            while (task_status == 2):
                if (counter < 50):
                    time.sleep(5)
                    task_status = self.GetTaskState(task)
                    if (task_status == 0):
                        result_json = self.GetResult(task)
                        if (result_json['code'] == 0):
                            # task_status = 0
                            return result_json['code'], result_json
                    counter += 1
                else:
                    break

        return 429, None

    def get_result_json_by_task(self, task):
        comStr = 'result?token={}&task={}'.format(self.token, task)
        line = self.api_url + comStr
        result_json = requests.get(line)
        self.set_response_status(result_json.json()['code'])
        return result_json

    def get_string_for_single_request(self, person):
        comStr = "search/physical?token=" + self.token + "&region=16&firstname={}&lastname={}".format(person.firstName, person.lastName)
        return comStr