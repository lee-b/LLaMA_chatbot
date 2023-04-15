from . import msg
from .model import ModelInfo


def process_reset_command(prompt, thread_id, server, model_info: ModelInfo):
	# reset a discussion
	msg.reset(thread_id)
	return "resetting..."


def process_full_history_command(prompt, thread_id, server, model_info: ModelInfo):
	# reprint the discussion?
	return msg.full_history(thread_id)


def process_save_command(prompt, thread_id, server, model_info: ModelInfo):
	# save the discussion thread to the db
	database[thread_id + ": " + s.split(" ")[1]] = msg.full_history(thread_id)
	save_db()
	return "saved"


def process_load_command(prompt, thread_id, server, model_info: ModelInfo):
	# load the discussion thread?? -- to where?
	full_history = ""

	try:
		full_history = database[thread_id + ": " + s.split(" ")[1]]
		msg.load_history(thread_id, full_history)
		return "loaded"
	except:
		reply = "error: db entry not found"

	return ""


def process_list_threads_command(prompt, thread_id, server, model_info: ModelInfo):
	reply = ""

	for key in database.keys():
		expected_key_prefix = thread_id + ": " ## ??? looks ropey

		if key.startswith(expected_key_prefix):
			reply += "> " + key + "\n"

	if reply == "":
		reply = "no threads found"

	return reply


def process_raw_command(prompt, thread_id, server, model_info: ModelInfo):
	# handle raw text formatting?
	return msg.predict(s[len("!raw "):], server, model_info)


def process_shell_command(prompt, thread_id, server, model_info: ModelInfo):
	# handle special display formatting of shell code?
	prompt = "```bash\n# " + s[len("!sh "):] + " then exit.\n"

	reply = msg.predict(prompt, server, model_info)[len(prompt):]

	reply2 = ""

	for s_ in reply.split("\n"):
		if not "exit" in s_:
			reply2 += s_ + "\n"
		else:
			break

	reply = reply2

	return reply


def process_python_command(prompt, thread_id, server, model_info: ModelInfo):
	# handle special display formatting of python code?
	prompt = "```python\n# " + s[len("!sh "):] + "\n"
	reply = msg.predict(prompt, server, model_info)#[len(prompt):]
	return reply


command_map = {
	"reset": process_reset_command,
	"full_history": process_full_history_command,
	"save": process_save_command,
	"load": process_load_command,
	"list_threads": process_list_threads_command,
	"raw": process_raw_command,
	"sh": process_shell_command,
	"py": process_python_command,
}
