import math
import re

from repo.repositories import InspectionsRepository
from src.metaclasses.singleton import Singleton
from src.utils import frame_to_base64


class Inspection:
    def __init__(self, measurement, value_type=None, meas_unit=None, threshold_low=None, threshold_high=None,
                 meas_type=None, offset=None, result=None, skip=None, group=None):
        self.measurement = measurement
        self.value_type = value_type
        self.meas_unit = meas_unit
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.meas_type = meas_type
        self.offset = offset
        self.result = result
        self.skip = skip
        self.group = group


class InspectionListService(metaclass=Singleton):
    def __init__(self):
        self.inspection_list: dict[str, Inspection] = {}
        self.inspection_list_repo = InspectionsRepository()
        self.images_dict = {}

    def load_inspection_list(self):
        inspections_table = self.inspection_list_repo.get()
        if inspections_table is None:
            print("No inspections configured - skipping inspection list loading")
            return
        for key in inspections_table.inspections:
            self.inspection_list[key] = Inspection(value_type=inspections_table.inspections[key]['Value Type'],
                                                   meas_unit=inspections_table.inspections[key]['Meas Unit'],
                                                   threshold_low=inspections_table.inspections[key]['Meas Lower Limit'],
                                                   threshold_high=inspections_table.inspections[key]['Meas Upper Limit'],
                                                   meas_type=inspections_table.inspections[key]['Meas Type'],
                                                   offset=inspections_table.inspections[key]['Offset'],
                                                   result=None,
                                                   measurement=None,
                                                   skip=inspections_table.inspections[key]['Skip'],
                                                   group=inspections_table.inspections[key]['Group'])

    def find_inspection_by_name(self, name: str):
        try:
            return self.inspection_list[name]
        except KeyError:
            return None

    def add_inspection(self, dic):
        for k, v in dic.items():
            self.inspection_list[k].measurement = v

    def add_image(self, group_name, frame):
        self.images_dict[group_name] = frame_to_base64(frame).decode('utf-8')

    def fix_missing_pins_shift(self):
        pins_nok = dict()
        for key in self.inspection_list:
            if re.search("c[0-9]+p[0-9]+[xy]", key):
                if self.inspection_list[key].measurement is not None:
                    if self.inspection_list[key].measurement < (self.inspection_list[key].offset - 1) or self.inspection_list[
                        key].measurement > (self.inspection_list[key].offset + 1):
                        pins_nok[key[:-1] + "x"] = self.inspection_list[key[:-1] + "x"].measurement
                        pins_nok[key[:-1] + "y"] = self.inspection_list[key[:-1] + "y"].measurement
                        pins_nok[key[:-1] + "z"] = self.inspection_list[key[:-1] + "z"].measurement
                        self.inspection_list[key].measurement = float('nan')
                        self.inspection_list[key[:-1] + "y"].measurement = float('nan')
                        self.inspection_list[key[:-1] + "z"].measurement = float('nan')
                else:
                    self.inspection_list[key].measurement = float('nan')
                    self.inspection_list[key[:-1] + "y"].measurement = float('nan')
                    self.inspection_list[key[:-1] + "z"].measurement = float('nan')

        if len(pins_nok) > 0:
            for key, value in pins_nok.items():
                measure = value
                if measure is not None:
                    for key in self.inspection_list:
                        if re.search("c[0-9]+p[0-9]+x", key):
                            if (self.inspection_list[key].offset - 1) < measure < (self.inspection_list[key].offset + 1) and \
                                    (self.inspection_list[key[:-1] + "y"].offset - 1) < pins_nok[key[:-1] + "y"] < (
                                    self.inspection_list[key[:-1] + "y"].offset + 1):
                                self.inspection_list[key].measurement = measure
                                self.inspection_list[key[:-1] + "y"].measurement = pins_nok[key[:-1] + "y"]
                                self.inspection_list[key[:-1] + "z"].measurement = pins_nok[key[:-1] + "z"]
                                break

    def add_offsets_to_measurement(self):
        for key in self.inspection_list:
            if not self.inspection_list[key].measurement:
                self.inspection_list[key].measurement = 0

            if self.inspection_list[key].offset and not math.isnan(self.inspection_list[key].measurement):
                self.inspection_list[key].measurement = round((self.inspection_list[key].measurement - self.inspection_list[key].offset), 3)

    def set_results_from_measurements(self):
        for key in self.inspection_list:
            if self.inspection_list[key].threshold_low <= self.inspection_list[key].measurement <= self.inspection_list[key].threshold_high:
                self.inspection_list[key].result = 'Pass'
            else:
                self.inspection_list[key].result = 'Fail'

    def has_fails(self):
        fail_bool_lst = [False if self.inspection_list[key].result == 'Pass' else True for key in self.inspection_list]

        if True in fail_bool_lst:
            return True

        return False

    def group_has_fails(self, group_name):
        fail_bool_lst = [False if self.inspection_list[key].result == 'Pass' else True for key in self.inspection_list if self.inspection_list[key].group == group_name]

        if True in fail_bool_lst:
            return True

        return False

    def save_offsets(self):
        inspections_table = self.inspection_list_repo.get()
        if inspections_table is None:
            print("No inspections configured - skipping offset saving")
            return

        for key in self.inspection_list:
            if self.inspection_list[key].offset != 'N/A':
                self.inspection_list[key].offset = self.inspection_list[key].measurement

        for key in inspections_table.inspections:
            if self.inspection_list[key].offset:
                inspections_table.inspections[key]['Offset'] = self.inspection_list[key].offset

        self.inspection_list_repo.update(inspections_table)

    def show_results(self):
        show_dict = {}

        for key in self.inspection_list.keys():
            if self.inspection_list[key].group not in show_dict.keys():
                status = "Fail" if self.group_has_fails(self.inspection_list[key].group) else "Pass"
                show_dict[self.inspection_list[key].group] = {}
                show_dict[self.inspection_list[key].group]['name'] = self.inspection_list[key].group
                show_dict[self.inspection_list[key].group]['status'] = status
                show_dict[self.inspection_list[key].group]['image'] = self.images_dict[self.inspection_list[key].group]
                show_dict[self.inspection_list[key].group]['data'] = []
                show_dict[self.inspection_list[key].group]['data'].append(
                    {
                        'inspection_name': key,
                        'value': self.inspection_list[key].measurement,
                        'expected': self.inspection_list[key].threshold_low,
                        'pass': True if self.inspection_list[key].result == "Pass" else False
                    }
                )
            else:
                # show_dict[self.inspection_list[key].group]['status'] = show_dict[self.inspection_list[key].group]['status'] and self.inspection_list[key].result
                show_dict[self.inspection_list[key].group]['data'].append(
                    {
                        'inspection_name': key,
                        'value': self.inspection_list[key].measurement,
                        'expected': self.inspection_list[key].threshold_low,
                        'pass': True if self.inspection_list[key].result == "Pass" else False
                    }
                )

        li = []
        for key, v in show_dict.items():
            li.append(v)

        return li
