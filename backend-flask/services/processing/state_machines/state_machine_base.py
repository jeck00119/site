import time

from services.processing.state_machines.state_machine_abstract import StateMachineAbstract
from src.utils import bcolors


class StateMachineBase(StateMachineAbstract):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._components_to_process = ['36529dec-1603-43fc-9dfb-04ec98a00a3a']

    def _identification(self):
        self._init_state("IDENTIFICATION")
        ##############################
        self._capability_service.init_excel_headers(self.interpreter_service.inspection_list)

        ##############################
        time.sleep(1)
        super()._identification()

    def _processing(self):
        self._init_state("PROCESSING")
        ##############################
        result = self._components_service.process_component(self._components_to_process[0])
        self.interpreter_service.add_inspection(result.data)
        self.interpreter_service.add_offsets_to_measurement()
        self.interpreter_service.set_results_from_measurements()

        # self.interpreter_service.save_offsets()

        self._capability_service.add_row_to_excel(self.interpreter_service.inspection_list)

        ##############################
        time.sleep(1)
        super()._processing()

    def _capability(self):
        self._init_state("CAPABILITY")
        ##############################

        ##############################
        time.sleep(1)
        super()._capability()

    def _exit(self):
        self._init_state("EXIT")
        ##############################
        self._capability_service.save_excel_report()
        ##############################
        time.sleep(1)
        super()._exit()

    def _init_state(self, state):
        self._start_time = time.time()
        ##############################
        ##############################
        self._current_state = state
        self._message_to_deque({'event': f'Entered: {self._current_state}'})


if __name__ == "__main__":
    sm = StateMachineBase(ws_callback='')
    sm.T_start()
    # sm.get_graph().draw(f'end.png', prog='dot')
    print(f'{bcolors.OKGREEN}{sm.timings}{bcolors.ENDC}')