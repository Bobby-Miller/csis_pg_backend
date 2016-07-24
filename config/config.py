from csv import reader

with open('C:/users/millebo/PycharmProjects/csis_pg_backend/config/csis_config.txt', 'r') as data:
    reader = reader(data, delimiter="=")
    configs = {}
    for config in reader:
        try:
            configs[config[0]] = config[1]
        except IndexError:
            pass

bool_dict = {'True': True, 'False': False}

configs['test'] = bool_dict[configs['test']]
configs['status_timer'] = float(configs['status_timer'])
configs['report_timer'] = float(configs['report_timer'])

class Configs:
    def __init__(self):
        self.configs = configs
        self.test = configs['test']
        if self.test:
            self.data_path = self.configs['test_data_path']
        else:
            self.data_path = self.configs['data_path']

    @property
    def data_path(self):
        return self._data_path

    @data_path.setter
    def data_path(self, path):
        self._data_path = path