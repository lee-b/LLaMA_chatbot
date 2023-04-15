import asyncio
import os
import sys

from nio.exceptions import LocalProtocolError

from .client import AsyncClient
from .db import init_db, save_db, database
from .model import ModelInfo
from .topic_manager import TopicManager


class Config:
	def __init__(self):
		self.matrix_server = os.getenv("MATRIX_SERVER")
		self.matrix_user = os.getenv("MATRIX_USER")
		self.matrix_password = os.getenv("MATRIX_PASSWORD")
		self.matrix_room = os.getenv("MATRIX_ROOM")

		self.prompt_text_template = open("prompt.txt", "r").read()
		self.input_text_template = open("input.txt", "r").read()
		self.assistant_input_text_template = open("assistant_input.txt", "r").read()

		self.model_info = ModelInfo(self.prompt_text_template) # use defaults for now


async def async_main() -> None:
	global client, database

	config = Config()

	timeout_msecs = 30000

	database = init_db("database.json")

	try:
		client = AsyncClient(config.matrix_server, config.matrix_user)
		print(await client.login(config.matrix_password))
	except LocalProtocolError as e:
		print("ERROR: {r}\n\tProbably invalid server credentials; couldn't log in!", file=sys.stderr)
		return 1

	topic_manager = TopicManager()

	try:
		await client.sync()
		await client.join(config.matrix_room)

		message_cb = lambda room, event: message_callback(
			room, event,
			config.input_text_template,
			config.matrix_user,
			config.assistant_input_text_template,
			config.matrix_server,
			config.model_info,
			topic_manager,
		)

		client.add_event_callback(message_cb, RoomMessageText)

		await client.sync_forever(timeout=timeout_msecs)

	finally:
		save_db("database.json", database)


def main():
    asyncio.run(async_main())
