from threading import Thread, Lock

import numpy


class ComponentProcessingThread(Thread):
    def __init__(self, process_queue, components_repository, algorithms_service, interpreter_service, components_repo_lock):
        super().__init__()
        self.process_queue = process_queue
        self.components_repository = components_repository
        self.algorithms_service = algorithms_service
        self.interpreter_service = interpreter_service
        self.components_repo_lock = components_repo_lock
        self.running = False
        self.runningLock = Lock()
        self.results = {}

    def set_running(self, running: bool):
        self.runningLock.acquire()
        self.running = running
        self.runningLock.release()

    def run(self) -> None:
        results = {}

        while True:
            self.runningLock.acquire()
            running = self.running
            self.runningLock.release()

            if not running and self.process_queue.empty():
                break

            task = self.process_queue.get()

            res, component = self.process_algorithm(task.frame, task.component_id)
            results = self.interpret_results(component["name"], component["algorithm_type"], res)
            self.interpreter_service.add_inspection(results)
            inspection = self.interpreter_service.find_inspection_by_name(component["name"])
            self.interpreter_service.add_image(inspection.group, res.imageRoi)

        self.interpreter_service.set_results_from_measurements()
        self.results = {}

    def process_algorithm(self, frame: numpy.ndarray, component_id: str):
        print(f"Component ID: {component_id}")
        print(f"Components repository DB: {self.components_repository.db}")
        self.components_repo_lock.acquire()
        component = self.components_repository.read_id(component_id)
        self.components_repo_lock.release()
        algorithm = self.algorithms_service.create_algorithm(component['algorithm_uid'])
        result = algorithm.execute(frame)
        return result, component

    def interpret_results(self, component_name, algorithm_type, result):
        result_for_itac = {}
        if algorithm_type == "YOLO":
            result_for_itac[component_name] = len(result.data)

        return result_for_itac
