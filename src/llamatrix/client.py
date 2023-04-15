from nio import AsyncClient, MatrixRoom, RoomMessageText

from . import msg
from .db import database, save_db, load_db
from .model import ModelInfo


async def edit_markdown_message(room: MatrixRoom, message: str, original_event_id: str = None):
    content = {
        "msgtype": "m.text",
        "body": " * " + message,
        "m.new_content": {
            "msgtype": "m.text",
            "body": message,
        },
        "m.relates_to": {"rel_type": "m.replace", "event_id": original_event_id},
    }

    #
    return await client.room_send(
        room_id=room.room_id,
        message_type="m.room.message",
        content=content,
    )


def process_message(s, thread_id, server, model_info: ModelInfo):
	reply = None

	if s == "!reset":
		msg.reset(thread_id)
		reply = "resetting..."
	elif s == "!full_history":
		reply = msg.full_history(thread_id)
	elif s.split(" ")[0] == "!save":
		database[thread_id + ": " + s.split(" ")[1]] = msg.full_history(thread_id)
		save_db()
		reply = "saved"
	elif s.split(" ")[0] == "!load":
		full_history = ""
		try:
			full_history = database[thread_id + ": " + s.split(" ")[1]]
			msg.load_history(thread_id, full_history)
			reply = "loaded"
		except:
			reply = "error: db entry not found"
#	elif s.split(" ")[0] == "!list_threads":
#		reply = ""
#		for key in database.keys():
#			if key.startswith(thread_id + ": "):
#				reply += "> " + key + "\n"
#		if reply == "":
#			reply = "no threads found"
	elif s.split(" ")[0] == "!raw":
		reply = msg.predict(s[len("!raw "):], server, model_info)
#	elif s.split(" ")[0] == "!sh":
#		prompt = "```bash\n# " + s[len("!sh "):] + " then exit.\n"
#		reply = msg.predict(prompt, server, model_info)[len(prompt):]
#		reply2 = ""
#		for s_ in reply.split("\n"):
#			if not "exit" in s_:
#				reply2 += s_ + "\n"
#			else:
#				break
#		reply = reply2
#	elif s.split(" ")[0] == "!py":
#		prompt = "```python\n# " + s[len("!sh "):] + "\n"
#		reply = msg.predict(prompt, server, model_info)#[len(prompt):]
	return reply


def set_typing_state(typing, room):
	typing_task = client.room_typing(
		room.room_id,
		typing_state=typey,
		timeout=10000
	)

	loop = asyncio.get_running_loop()

	loop.create_task(typing_task)


async def stream_message(room, stream):
	set_typing_state(True, room)

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
		set_typing_state(True, room)

		print(m.event_id)

		m = await edit_markdown_message(room, i, me)

	set_typing_state(False, room)

	return


async def message_callback(room: MatrixRoom, event: RoomMessageText, input_text_template, matrix_user, assistant_input_text_template, server, model_info) -> None:
	if event.sender == matrix_user:
		return

	pm = process_message(event.body, event.sender, server, model_info)
	if pm != None:
		await client.room_send(room_id=room.room_id, message_type="m.room.message", content={"msgtype": "m.text", "body": pm})
	else:
		loop = asyncio.get_running_loop()

		send_message_task = msg.send_message_stream(
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
