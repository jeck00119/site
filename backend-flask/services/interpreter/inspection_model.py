from src.utils import CamelModel


class InspectionsModel(CamelModel):
    columns: list
    column_types: list
    inspections: dict
