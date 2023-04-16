import asyncio
import os
import sys

from nio.exceptions import LocalProtocolError

from .client import AsyncClient
from .db import init_db, save_db, database
from .topic_manager import TopicManager
from .config import Config


async def async_main() -> None:
	global database # keeping the global for for now, but gradually reducing its direct usage

	config = Config()

	timeout_msecs = 30000

	try:
		client = AsyncClient(config.matrix_server, config.matrix_user)
		res = await client.login(config.matrix_password)
		print(res)
	except (LocalProtocolError, ValueError) as e:
		print(f"ERROR: {e}\n\tProbably invalid server credentials; couldn't log in!", file=sys.stderr)
		return 1

	database = init_db(config.db_path)

	topic_manager = TopicManager(
		config.prompt_text_template,
		config.input_text_template,
		config.assistant_input_text_template
	)

	try:
		await client.sync()
		await client.join(config.matrix_room)

		message_cb = lambda room, event: message_callback(
			client,
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
		save_db(config.db_path, database)


def main():
    asyncio.run(async_main())
