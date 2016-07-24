from config.config import Configs
import os
from datetime import datetime
from typing import NamedTuple
from operator import itemgetter
from shutil import rmtree


class Segment(Configs):

    def parse_all_folder_data(self) -> list:
        """
        Pull all folder names from the csis_config data_path variable,
        and parse it into a list containing: file path, batch name,
        batch date, batch time
        :return: list of: (namedtuple) Parse:[file_path, batch_name, batch_datetime]
        """

        point = NamedTuple('Parse', (('folder_path', str), ('batch_name', str),
                                     ('end_datetime', datetime)))

        def parse(folder):
            return folder[0].split("\\")[-1].split("-")
        parsed_folders = [
            point(
                *(x[0],
                  parse(x)[0],
                  datetime(year=int(parse(x)[1][0:4]), month=int(parse(x)[1][4:6]),
                           day=int(parse(x)[1][6:8]), hour=int(parse(x)[2][0:2]),
                           minute=int(parse(x)[2][2:4]), second=int(parse(x)[2][4:6]))
                  )
            )
            for x in os.walk(self.data_path)
            if x[0] != self.data_path and len(x[0].split("\\")) == 2
            ]
        return parsed_folders

    def sorted_segments(self) -> list:
        """Sorts parsed folders by datetime
        :return: (list of namedtuples) sorted segments"""
        segment_list = self.parse_all_folder_data()
        sorted_segment_list = sorted(segment_list, key=itemgetter(2))
        return sorted_segment_list

    def current_segment(self) -> NamedTuple:
        """
        sorts parsed folders and returns most recent batch set
        :return: (namedtuple) most recent batch info
        """
        return self.sorted_segments()[-1]

    def delete_finished_segments(self) -> None:
        """
        Delete all but the most recent segment folder tree.
        :return: None
        """
        finished_segments = self.sorted_segments()[:-1]
        for segment in finished_segments:
            rmtree(path=segment.folder_path)
