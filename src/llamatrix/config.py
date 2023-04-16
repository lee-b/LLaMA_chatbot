import os

from .model import ModelInfo


class Config:
	def __init__(self):
		self.matrix_server = os.getenv("MATRIX_SERVER")
		self.matrix_user = os.getenv("MATRIX_USER")
		self.matrix_password = os.getenv("MATRIX_PASSWORD")
		self.matrix_room = os.getenv("MATRIX_ROOM")

		self.prompt_text_template = open("config/prompt.txt", "r").read()
		self.input_text_template = open("config/input.txt", "r").read()
		self.assistant_input_text_template = open("config/assistant_input.txt", "r").read()

		self.model_info = ModelInfo(self.prompt_text_template) # use defaults for now

		self.db_path = "database.json"
