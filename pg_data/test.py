import unittest
import os
from summary import Summary
from segments import Segment
from datetime import datetime, time
from config.config import Configs
from shutil import rmtree
from db_data import DBData


class TestAid:
    def test_segments_dict(self):
        segments = Segment().parse_all_folder_data()
        segment_dict = {}
        for segment in segments:
            key = segment[1] + str(segment[2].day)
            segment_dict[key] = segment
        return segment_dict


class TestSummaryData(unittest.TestCase):

    def test_exists_false(self):
        os.mkdir(Configs().data_path + '/dummy-20160605-161616')
        test_segments = TestAid().test_segments_dict()
        summary_exists = Summary(test_segments['dummy5']).exists()
        rmtree(Configs().data_path + '/dummy-20160605-161616')
        self.assertEqual(summary_exists, False)

    def test_exists_true(self):
        test_segments = TestAid().test_segments_dict()
        self.assertEqual(Summary(test_segments['test20']).exists(), True)

    def test_summary_data_bjkl(self):
        test_dict = {
            'inspected': 2,
            'good': 1,
            'good_percent': 50.0,
            'fail_general': 1,
            'fail_gen_percent': 50.0,
            'fail_od': 0,
            'fail_od_percent': 0.0,
            'fail_backward': 0,
            'fail_backward_percent': 0.0,
            'n_a': 0,
            'n_a_percent': 0.0
        }
        test_segments = TestAid().test_segments_dict()
        summary = Summary(test_segments['bjkl15'])
        for key, value in test_dict.items():
            self.assertEqual(value, getattr(summary.data(), key))

    def test_summary_misc_data_bjkl(self):
        test_segments = TestAid().test_segments_dict()
        summary = Summary(test_segments['bjkl15'])
        test_dict = {
            'date': datetime(year=2016, month=7, day=15),
            'time': time(hour=13, minute=17),
            'lost_homing': 0,
            'gate_homes': 0,
        }
        for key, value in test_dict.items():
            self.assertEqual(value, summary.misc_data()[key])

batch = TestAid().test_segments_dict()['bnkl15']

print(DBData().update_summary_and_stats(batch))

