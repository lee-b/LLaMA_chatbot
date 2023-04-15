import asyncio
import os

from nio import AsyncClient, MatrixRoom, RoomMessageText

from . import msg


try:
	f = open("database.json", "r")
	database = eval(f.read())
	f.close()
except:
	f = open("database.json", "w")
	f.write("{}")
	f.close()
	database = {}

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

def process_message(s, thread_id):
	reply = None
	if s == "!reset":
		msg.reset(thread_id)
		reply = "resetting..."
	elif s == "!full_history":
		reply = msg.full_history(thread_id)
	elif s.split(" ")[0] == "!save":
		database[thread_id + ": " + s.split(" ")[1]] = msg.full_history(thread_id)
		f = open("database.json", "w")
		f.write(str(database))
		f.close()
		reply = "saved"
	elif s.split(" ")[0] == "!load":
		full_history = ""
		try:
			full_history = database[thread_id + ": " + s.split(" ")[1]]
			msg.load_history(thread_id, full_history)
			reply = "loaded"
		except:
			reply = "error: db entry not found"
	elif s.split(" ")[0] == "!list_threads":
		reply = ""
		for key in database.keys():
			if key.startswith(thread_id + ": "):
				reply += "> " + key + "\n"
		if reply == "":
			reply = "no threads found"
	elif s.split(" ")[0] == "!raw":
		reply = msg.predict(s[len("!raw "):], server)
	elif s.split(" ")[0] == "!sh":
		prompt = "```bash\n# " + s[len("!sh "):] + " then exit.\n"
		reply = msg.predict(prompt, server)[len(prompt):]
		reply2 = ""
		for s_ in reply.split("\n"):
			if not "exit" in s_:
				reply2 += s_ + "\n"
			else:
				break
		reply = reply2
	elif s.split(" ")[0] == "!py":
		prompt = "```python\n# " + s[len("!sh "):] + "\n"
		reply = msg.predict(prompt)#[len(prompt):]
	return reply

def typey_typey(typey, room):
	lol420 = client.room_typing(
	           room.room_id,
	           typing_state=typey,
	           timeout=10000)
	loop = asyncio.get_running_loop()
	loop.create_task(lol420)

async def stream_message(room, stream):
	typey_typey(True, room)
	m = await client.room_send(room_id=room.room_id, message_type="m.room.message", content={"msgtype": "m.text", "body": 'please wait...'})
	me = m.event_id
	async for i in stream:
		typey_typey(True, room)
		print(m.event_id)
		m = await edit_markdown_message(room, i, me)
	typey_typey(False, room)
	return

async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
	if event.sender == os.getenv("MATRIX_USER"):
		return

	pm = process_message(event.body, event.sender)
	if pm != None:
		await client.room_send(room_id=room.room_id, message_type="m.room.message", content={"msgtype": "m.text", "body": pm})
	else:
		loop = asyncio.get_running_loop()
		loop.create_task(stream_message(room, msg.send_message_stream(event.body, event.sender)))

	print(
		f"Message received in room {room.display_name}\n"
		f"{room.user_name(event.sender)} | {event.body}"
	)


async def async_main() -> None:
	global client
	server = os.getenv("MATRIX_SERVER")
	client = AsyncClient(server, os.getenv("MATRIX_USER"))

	print(await client.login(os.getenv("MATRIX_PASSWORD")))
	await client.sync()
	await client.join(os.getenv("MATRIX_ROOM"))

	client.add_event_callback(message_callback, RoomMessageText)

	print("lol")

	await client.sync_forever(timeout=30000)  # milliseconds

def main():
    asyncio.run(async_main())

