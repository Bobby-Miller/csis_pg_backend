import csv
import os
from collections import namedtuple
from datetime import datetime

from config.config import Configs


class Summary(Configs):
    def __init__(self, batch: namedtuple):
        super().__init__()
        self.batch = batch
        self.file_path = self.batch[0] + '/' + self.batch[1] + '_summary.txt'

    def exists(self):
        """
        :return: (bool) Summary file exists for the given batch
        """
        return os.path.isfile(self.file_path)

    @staticmethod
    def converted_summary_list(summary_list) -> (list, tuple, namedtuple):
        """
        Converts a string-version summary list into it's int and float equivalent
        :param summary_list: List of string values that can be converted to values
        :return: int and float versions of string list.
        """
        converted_list = []
        for item in summary_list:
            try:
                converted_list.append(int(item))
            except ValueError:
                converted_list.append(float(item))
        return converted_list

    def data(self) -> namedtuple:
        """
        Pulls data from a batch summary table.
        :return: (namedtuple) summary table data.
        """
        sleep = int(self.configs['ignore_summary_lines'])
        if self.exists():
            with open(self.file_path, 'r') as file_data:
                reader = csv.reader(file_data, delimiter='\t')
                data_list = []
                for data in reader:
                    if sleep != 0:
                        sleep -= 1
                    else:
                        data_list.append(data)
                point = namedtuple('summary', 'inspected, good, good_percent, '
                                              'fail_general, fail_gen_percent, '
                                              'fail_od, fail_od_percent, fail_backward, '
                                              'fail_backward_percent, n_a, n_a_percent')
                str_list = (data_list[0][1], *data_list[1][1:3], *data_list[2][1:3],
                            *data_list[3][1:3], *data_list[4][1:3], *data_list[5][1:3])
                converted_list = self.converted_summary_list(str_list)
                return point(*converted_list)

    def misc_data(self) -> dict:
        """
        Pulls data formatted with a semicolon instead of tabs.
        :return: dict (date, time, lost_homing, homes)
        """
        if self.exists():
            with open(self.file_path, 'r') as file_data:
                reader = csv.reader(file_data, delimiter=':')
                info_dict = {}
                conversion_dict = {
                    'DATE': 'date',
                    'TIME': 'time',
                    'Lost to Homing': 'lost_homing',
                    'Batch Homes': 'gate_homes',
                }
                for data in reader:
                    try:
                        data[1] = ':'.join(data[1:])
                        info_dict[conversion_dict[data[0]]] = data[1].lstrip()
                    except KeyError:
                        pass
                    except IndexError:
                        pass
                info_dict['date'] = datetime.strptime(info_dict['date'], '%m/%d/%Y')
                info_dict['time'] = datetime.strptime(info_dict['time'], '%I:%M %p').time()
                info_dict['lost_homing'] = int(info_dict['lost_homing'])
                info_dict['gate_homes'] = int(info_dict['gate_homes'])
                return info_dict
