from config.config import Configs
from types import GeneratorType
from collections import namedtuple as nt
import csv
import os
from math import isnan


class Stats(Configs):
    def __init__(self, batch: nt):
        super().__init__()
        self.batch = batch
        self.file_path = self.batch[0] + '/' + self.batch[1] + '_stats.txt'

    def exists(self) -> bool:
        """
        :return: (bool) Summary file exists for the given batch.
        """
        return os.path.isfile(self.file_path)

    def data(self) -> GeneratorType:
        """
        Pulls data from file, yielded line by line.
        :return: generated list
        """
        if self.exists():
            with open(self.file_path, 'r') as file_data:
                reader = csv.reader(file_data, delimiter='\t')
                for data in reader:
                    yield data

    def field_zip(self) -> GeneratorType:
        """
        Converts txt file names to db names, throws out unwanted data columns, and
        returns a dict for each line mapped to db name
        :return: generated dicts {db_name: value}
        """
        data = self.data()
        data_labels = next(data)
        field_dict = {
            'ID': 'id',
            'Overall Result': 'overall_result',
            'RE Station Result': 'round_end',
            'FE Station Result': 'flat_end',
            'ODP Station Result': 'outer_dimension',
            'SS Station Result': 'sepia_screen',
            'Time': 'time',
            'RE Valid Master': 'round_valid_master',
            'RE Part Present': 'round_present',
            'RE Part Orientation': 'round_orientation',
            'RE Part Valid': 'round_valid',
            'RE Inner Bright': 'round_inner_bright',
            'RE Inner Small Dark': 'round_inner_small_dark',
            'RE Inner Large': 'round_inner_large_dark',
            'RE Outer Bright': 'round_outer_bright',
            'RE Outer Small Dark': 'round_outer_small_dark',
            'RE Outer Large Dark': 'round_outer_large_dark',
            'RE IDA Bright': 'round_inner_bright_area',
            'RE IDA Large Dark': 'round_inner_large_dark_area',
            'RE IDA Small Dark': 'round_inner_small_dark_area',
            'RE ODA Bright': 'round_outer_bright_area',
            'RE ODA Large Dark': 'round_outer_large_dark_area',
            'RE ODA Small Dark': 'round_outer_small_dark_area',
            'RE M Center X': 're_m_center_x',
            'RE M Center Y': 're_m_center_y',
            'RE UUT Center X': 're_uut_center_x',
            'RE UUT Center Y': 're_uut_center_y',
            'FE Valid Master': 'flat_valid_master',
            'FE Part Orientation': 'flat_orientation',
            'FE Part Valid': 'flat_valid',
            'FE Inner Diameter': 'flat_ID',
            'FE Obstruction': 'flat_obstruction',
            'FE Chip': 'flat_chip',
            'FE  Inner Dia Min': 'flat_inner_diameter_min',
            'FE Inner Dia Max': 'flat_inner_diameter_max',
            'FE  Obstr Area': 'flat_obstruction_area',
            'FE Chip Area': 'flat_chip_area',
            'ODP Position': 'dimension_position',
            'ODP Length': 'dimension_length',
            'ODP Bumps': 'dimension_bumps',
            'ODP Chips': 'dimension_chips',
            'ODP Envelope': 'dimension_envelope',
            'ODP Nose': 'dimension_nose',
            'ODP # Images': 'odp_num_images',
            'ODP Length mm': 'dimension_length_mm',
            'ODP Max Bump mm': 'dimension_bump_max',
            'ODP Max Chip mm': 'dimension_chip_max',
            'ODP Env mm': 'dimension_envelope_mm',
            'ODP Max Env Frame': '_',
            'ODP  Nose W Min/Max': 'dimension_nose_min_max',
            'ODP  W Min/Max Frame': '_',
            'ODP Mdn OD mm': 'dimension_median_od',
            'SS Valid': 'sepia_valid',
            'SS Bright Defect': 'sepia_bright_spot',
            'SS Blemish Defect': 'sepia_blemish',
            'SS Spot/Crack Defect': 'sepia_spot_crack',
            'SS Bright DA mm^2': 'sepia_bright_area',
            'SS Blemish DA mm^2': 'sepia_blemish_area',
            'SS Spot/Crack DA mm^2': 'sepia_spot_crack_area',
            'SS  # Frames': 'ss_num_frames',
        }
        ignore_fields = [
            'ID',
            'Time',
            'RE M Center X',
            'RE M Center Y',
            'RE UUT Center X',
            'RE UUT Center Y',
            'ODP # Images',
            'SS  # Frames',
            'ODP Max Env Frame',
            'ODP  W Min/Max Frame',
        ]
        ignore_list = []
        field_list = []
        for i, label in enumerate(data_labels):
            if label in ignore_fields:
                ignore_list.append(i)
            else:
                field_list.append(field_dict[label])
        for data_line in data:
            data_list = []
            for i, data in enumerate(data_line):
                if i not in ignore_list:
                    data_list.append(data)
            yield dict(zip(field_list, data_list))

    @staticmethod
    def field_map(dict_gen, name, func) -> GeneratorType:
        for d in dict_gen:
            d[name] = func(d[name])
            yield d

    def floatinate(self, value):
        try:
            if isnan(float(value)):
                return 0
            return float(value)
        except TypeError:
            return 0

    @staticmethod
    def test_names():
        return ['round_end',
                'flat_end',
                'outer_dimension',
                'sepia_screen',
                'round_valid_master',
                'round_present',
                'round_orientation',
                'round_valid',
                'round_inner_bright',
                'round_inner_small_dark',
                'round_inner_large_dark',
                'round_outer_bright',
                'round_outer_small_dark',
                'round_outer_large_dark',
                'flat_valid_master',
                'flat_orientation',
                'flat_valid',
                'flat_ID',
                'flat_obstruction',
                'flat_chip',
                'dimension_position',
                'dimension_length',
                'dimension_bumps',
                'dimension_chips',
                'dimension_envelope',
                'dimension_nose',
                'sepia_valid',
                'sepia_bright_spot',
                'sepia_blemish',
                'sepia_spot_crack']

    @staticmethod
    def measurement_names():
        return ['round_inner_bright_area',
                'round_inner_large_dark_area',
                'round_inner_small_dark_area',
                'round_outer_bright_area',
                'round_outer_large_dark_area',
                'round_outer_small_dark_area',
                'flat_inner_diameter_min',
                'flat_inner_diameter_max',
                'flat_obstruction_area',
                'flat_chip_area',
                'dimension_length_mm',
                'dimension_bump_max',
                'dimension_chip_max',
                'dimension_envelope_mm',
                'dimension_nose_min_max',
                'dimension_median_od',
                'sepia_bright_area',
                'sepia_blemish_area',
                'sepia_spot_crack_area'
                ]

    def type_map(self) -> GeneratorType:
        """
        Mapping the line dicts to their respective types (bool or float
        :return:
        """
        test_names = self.test_names()
        measurement_names = self.measurement_names()
        d = self.field_zip()
        for name in test_names:
            d = self.field_map(d, name, lambda v: 1 if v == 'Pass' else 0)
        for name in measurement_names:
            d = self.field_map(d, name, self.floatinate)
        return d

    def group_count_average(self):
        """
        Group dicts by their overall result, then count and average all data.
        :return: (dict) overall_result: measurements: 'average': average value
                                                      'count':   non-zero count
                                        tests:        'tests':   average %
        """
        group_dict = {}
        measurement_names = self.measurement_names()
        test_names = self.test_names()
        for data_dict in self.type_map():
            # Create a group/line for each result type - Good, Fail, Fail-OD, NA,
            # backward
            group = data_dict['overall_result']
            if group not in group_dict:
                # All measurement fields in the measurements dict. Test fields in the
                # tests dict. The count is incremented every loop, and used to average
                # the tests after the loop is complete.
                group_dict[group] = {
                    'measurements': {
                        'averages': {},
                        'counts': {},
                    },
                    'tests': {},
                    'count': 1
                }
            else:
                group_dict[group]['count'] += 1
            for name, val in data_dict.items():
                # Each measurement 'average' will be totaled, and then divided by count
                # in a subsequent loop.
                averages = group_dict[group]['measurements']['averages']
                counts = group_dict[group]['measurements']['counts']
                if name in measurement_names:
                    if name not in averages:
                        averages[name] = val
                        counts[name] = 1 if val != 0 else 0
                    else:
                        averages[name] += val
                        counts[name] += 1 if val != 0 else 0
                # Each test is summed, then in a later loop is divided by total count.
                elif name in test_names:
                    tests = group_dict[group]['tests']
                    if name not in tests:
                        tests[name] = val
                    else:
                        tests[name] += val

        # Measurements are divided by their respective counts, and tests are divided by
        # total count.
        for group in group_dict.values():
            averages = group['measurements']['averages']
            counts = group['measurements']['counts']
            for name, average in averages.items():
                try:
                    averages[name] = round(average / counts[name], 5)
                except ZeroDivisionError:
                    pass

            for name, test in group['tests'].items():
                try:
                    test /= group['count']
                    group['tests'][name] = round((test * 100), 2)
                except ZeroDivisionError:
                    pass
        return group_dict
