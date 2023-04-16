from nio import AsyncClient, MatrixRoom, RoomMessageText

from . import msg
from .db import database, save_db, load_db
from .model import ModelInfo
from .commands import command_map
from .topic_manager import TopicManager


async def edit_markdown_message(client, room: MatrixRoom, message: str, original_event_id: str = None):
	content = {
		"msgtype": "m.text",
		"body": " * " + message,
		"m.new_content": {
			"msgtype": "m.text",
			"body": message,
		},
		"m.relates_to": {"rel_type": "m.replace", "event_id": original_event_id},
	}

	return await client.room_send(
		room_id=room.room_id,
		message_type="m.room.message",
		content=content,
	)


def process_message(msg, thread_id, server, model_info: ModelInfo):
	first_word = msg.split(' ')[0]

	if first_word.startswith("!"):
		try:
			command = first_word[1:]
			command_handler = command_map[command]
		except KeyError as e:
			return None

		reply = command_handler(msg, thread_id, server, model_info)

	return None


def set_typing_state(client, typing, room):
	typing_task = client.room_typing(
		room.room_id,
		typing_state=typey,
		timeout=10000
	)

	loop = asyncio.get_running_loop()

	loop.create_task(typing_task)


async def stream_message(client, room, stream):
	set_typing_state(client, True, room)

	m = await client.room_send(
		room_id=room.room_id,
		message_type="m.room.message",
		content={
			"msgtype": "m.text",
			"body": 'please wait...'
		}
	)

	me = m.event_id

	async for i in stream:
		set_typing_state(client, True, room)

		print(m.event_id)

		msg = await edit_markdown_message(client, room, i, me)

	set_typing_state(client, False, room)


async def message_callback(client, room: MatrixRoom, event: RoomMessageText, input_text_template, matrix_user, assistant_input_text_template, server, model_info: ModelInfo, topic_manager: TopicManager) -> None:
	if event.sender == matrix_user:
		return

	pm = process_message(event.body, event.sender, server, model_info)

	if pm != None:
		await client.room_send(room_id=room.room_id, message_type="m.room.message", content={"msgtype": "m.text", "body": pm})
	else:
		loop = asyncio.get_running_loop()

		send_message_task = topic_manager.send_message_stream(
			event.body,
			event.sender,
			input_text_template,
			assistant_input_text_template,
		)

		task = stream_message(
			room,
			send_message_task,
		)

		loop.create_task(task)

	print(
		f"Message received in room {room.display_name}\n"
		f"{room.user_name(event.sender)} | {event.body}"
	)
