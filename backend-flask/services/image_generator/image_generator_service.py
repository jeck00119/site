from repo.repositories import ImageGeneratorRepository
from services.image_generator.img_generator_model import ImageGeneratorModel
from services.image_generator.implementation.image_generator import ImageGenerator
from src.metaclasses.singleton import Singleton


class ImageGeneratorService(metaclass=Singleton):
    def __init__(self):
        self.image_generator_repository = ImageGeneratorRepository()
        self.img_data_objects:dict[str, ImageGenerator] = {}


    # def initialize_image_generator(self):
    #     for image_generator_doc in self.image_generator_repository.read_all():
    #         self._initialize_generator(image_generator_doc['uid'])


    def get_image_generators(self):
        return self.image_generator_repository



    def initialize_generator(self,  uid):
        img_data = self.image_generator_repository.read_id(uid)
        if img_data:
            img_data_model = ImageGeneratorModel(**img_data)
            self.img_data_objects[uid] = ImageGenerator(img_data_model)
            return f'initialized'
        else:
            return f'uninitliazed'

    def grab_from_generator(self, uid):
        if uid in self.img_data_objects.keys():
            image = self.img_data_objects[uid].get_frame()
        else:
            self.initialize_generator(uid)
            image = self.img_data_objects[uid].get_frame()

        return image






