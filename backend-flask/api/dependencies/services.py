def get_service_by_type(service_type):
    def lake():
        return service_type()
    return lake

