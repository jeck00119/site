import os
import sys
from abc import ABC, abstractmethod
from enum import Enum
from time import time

from transitions.extensions import LockedGraphMachine

from services.capability.capability_service import CapabilityService
from services.components.components_service import ComponentsService
from services.inspection_list.inspection_list_service import InspectionListService
from src.utils import bcolors

os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz/bin/'


class States(Enum):
    IDLE = 0
    IDENTIFICATION = 1
    PROCESSING = 2
    EXIT = 10

    CAPABILITY_INTERMEDIATE = 11
    FAILURE = 98

    @staticmethod
    def get_states():
        states = []
        for val in States:
            states.append(val.name)

        return states


class StateMachineAbstract(ABC):
    timings = {}

    _SAVE_GRAPHS = False

    def __init__(self,
                 components_service:ComponentsService,
                 interpreter_service:InspectionListService,
                 capability_service:CapabilityService,
                 itac_service,
                 cnc_service,
                 ws_callback, runs_target):

        self._components_service = components_service
        self.interpreter_service = interpreter_service
        self.interpreter_service.load_inspection_list()

        self._capability_service = capability_service
        self.itac_service = itac_service
        self.cnc_service = cnc_service


        self._sm_states = [
            {'name': States.IDLE},
            {'name': States.IDENTIFICATION, 'on_enter': [self._identification], 'on_exit': []},
            {'name': States.PROCESSING, 'on_enter': [self._processing.__name__], 'on_exit': []},
            {'name': States.CAPABILITY_INTERMEDIATE, 'on_enter': [self._capability.__name__], 'on_exit': []},
            {'name': States.EXIT, 'on_enter': [self._exit.__name__]},
            {'name': States.FAILURE},
        ]

        self._sm_transitions = [
            {'trigger': 'T_start', 'source': States.IDLE, 'dest': States.IDENTIFICATION},
            {'trigger': 'T_process', 'source': States.IDENTIFICATION, 'dest': States.PROCESSING},
            {'trigger': 'T_process_done', 'source': States.PROCESSING, 'dest': States.CAPABILITY_INTERMEDIATE,
             'conditions': [self._is_capability.__name__]},
            {'trigger': 'T_process_done', 'source': States.PROCESSING, 'dest': States.EXIT,
             'unless': [self._is_capability.__name__]},
            {'trigger': 'T_continue_capability', 'source': States.CAPABILITY_INTERMEDIATE, 'dest': States.PROCESSING},
            {'trigger': 'T_error', 'source': '*', 'dest': States.FAILURE},
        ]

        self.stateMachine: LockedGraphMachine = LockedGraphMachine(model=self, states=self._sm_states,
                                                                   initial=States.IDLE,
                                                                   transitions=self._sm_transitions,
                                                                   auto_transitions=True, title='State-Machine-Process',
                                                                   show_conditions=True, show_state_attributes=True,
                                                                   queued=True)

        self._current_state = "IDLE"
        self._ws_callback = ws_callback

        self._runs_target = runs_target
        self._was_capability = False

        self._start_time = 0
        self._start_time = time()
        self._prev_state_timing = 0
        self._elapsed_time = 0
        self._lastStateTime = 0
        try:
            self._save_method_graph('GraphAtInit', force_save=False)
        except:
            print(
                f'{bcolors.FAIL}Ai o eroare, cauta 123456 sa ma gasesti. Poti citi in requirments.txt ce ar trebui sa faci. Np!{bcolors.ENDC}')
        self._is_capability(subtract=False, emit=True)

    @abstractmethod
    def _identification(self):
        self._save_method_graph(sys._getframe().f_code.co_name)
        self._prev_state_timing = self._get_timing()
        ##############################################################################
        self.T_process()

    @abstractmethod
    def _processing(self):
        self._save_method_graph(sys._getframe().f_code.co_name)
        self._prev_state_timing = self._get_timing()
        ##############################################################################
        self.T_process_done()

    @abstractmethod
    def _capability(self):
        self._current_state = "CAPABILITY"
        self._save_method_graph(sys._getframe().f_code.co_name)
        self._prev_state_timing = self._get_timing()
        ############################
        self.T_continue_capability()

    @abstractmethod
    def _exit(self):
        self._current_state = "EXIT"
        self._save_method_graph(sys._getframe().f_code.co_name)
        self._prev_state_timing = self._get_timing()
        ##############################################################################

    def _is_capability(self, subtract=True, emit=False):
        if self._runs_target == 1:
            return False
        else:
            self._was_capability = True
            if subtract:
                self._runs_target -= 1
                print(f'{bcolors.OKCYAN}Remaining runs::{self._runs_target}{bcolors.ENDC}')
            return True

    def _message_to_deque(self, message):
        self._ws_callback(message)

    def _save_method_graph(self, name, force_save=False):
        print(f'{bcolors.OKGREEN}done:{name}{bcolors.ENDC}')

        if self._SAVE_GRAPHS or force_save:
            self.get_graph().draw(f'{time()}{name}.png', prog='dot')

    def _print_real_time(self):
        print(f'{bcolors.OKBLUE}Real cycle time = {time() - self._start_time}{bcolors.ENDC}')

    def _get_timing(self):
        stop = time()
        state_time = stop - self._start_time
        timing = state_time  # + self._elapsed_time

        if not self._is_capability(subtract=False, emit=False):
            StateMachineAbstract.timings[self.state] = timing

        return timing
