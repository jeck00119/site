import os
from typing import Union

from pydantic import BaseModel
from tinydb import TinyDB, where
from tinydb.database import Table

from repo.repository_exceptions import UidNotUnique, UidNotFound, NoConfigurationChosen
from src.metaclasses.singleton import Singleton


class BaseRepo(metaclass=Singleton):
    def __init__(self, db_name):
        super().__init__()
        self._configuration_path = ''
        self.databaseName = db_name
        self.db: Union[Table, None] = None

    @property
    def configuration_path(self):
        return self._configuration_path

    @configuration_path.setter
    def configuration_path(self, value):
        self._configuration_path = value

    def set_db(self, configuration_name):
        if configuration_name:
            path = f"{os.getcwd()}/config_db/{configuration_name}"
        else:
            path = f"{os.getcwd()}/config_db"

        try:
            os.listdir(path)
        except FileNotFoundError:
            os.mkdir(path)

        self.configuration_path = path
        self.db = TinyDB(path + f"/{self.databaseName}.json", sort_keys=True, indent=4, ).table(f"{self.databaseName}")

    def reset_db(self):
        self.db = None
        self._configuration_path = ''

    def get_configuration_path(self):
        return self._configuration_path

    def read_all(self):
        return self.db.all() if self.db is not None else []

    def create(self, model):
        if self.db is not None:
            if self.db.get(where("uid") == model.uid):
                raise UidNotUnique
            self.db.insert(model.model_dump())
        else:
            raise NoConfigurationChosen

    def read_id(self, uid):
        if self.db is not None:
            found = self.db.get(where("uid") == uid)
            if found:
                return found
            else:
                raise UidNotFound
        else:
            raise NoConfigurationChosen

    def update(self, model):
        if self.db is not None:
            if self.db.get(where("uid") == model.uid):
                self.db.update(model.model_dump(), cond=where("uid") == model.uid)
            else:
                raise UidNotFound
        else:
            raise NoConfigurationChosen

    def update_field(self, uid, field_name, value):
        model_dict = self.read_id(uid)
        model = self.convert_dict_to_model(model_dict)
        updated_model = model.copy(update={field_name: value})
        self.update(updated_model)

    def convert_dict_to_model(self, data: dict) -> BaseModel:
        pass

    def delete(self, uid):
        if self.db is not None:
            if self.db.get(where("uid") == uid):
                self.db.remove(where("uid") == uid)
            else:
                raise UidNotFound
        else:
            raise NoConfigurationChosen

    def find_by_query(self, condition):
        return self.db.search(condition)
