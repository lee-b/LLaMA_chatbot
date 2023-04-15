import asyncio
import datetime
import json
import random
import re
import websockets

import requests

from .model import ModelInfo
from .utils import random_hash, RunThread


async def run(model_info: ModelInfo, server):
    session = random_hash()

    n = 0

    async with websockets.connect(f"ws://{server}:7860/queue/join") as websocket:
        while content := json.loads(await websocket.recv()):
            msg_content = content["msg"]

            if msg_content == "send_hash":
                hash_dict_json = json.dumps({
                    "session_hash": session,
                    "fn_index": 7
                })
                await websocket.send(hash_dict_json)

            elif msg_content == "estimation":
                    pass

            elif msg_content == "send_data":
                    hash_dict_json = json.dumps({
                        "session_hash": session,
                        "fn_index": 7,
                        "data": model_info.model_params_as_list(),
                    })

                    await websocket.send()

            elif msg_content == "process_starts":
                    pass

            elif msg_content in ("process_generating", "process_completed"):
                    ret_me = content["output"]["data"][0]
                    do_it = False

                    print(ret_me[len(params["prompt"]):])

                    if "Human (" in ret_me[len(params["prompt"]):]:
                        ret_me = ret_me[:ret_me.rindex("Human (") - 1]
                        do_it = True

                    yield ret_me

                    if do_it:
                        break

#                    print(content["output"]["data"][0])

                    # You can search for your desired end indicator and 
                    #  stop generation by closing the websocket here

                    if (content["msg"] == "process_completed"):
                        break


async def get_result_stream(model_info: ModelInfo, server):
    s = "PLACEHOLDER"

    async for response in run(model_info, server):
        if s == response:
            break
        s = response
        yield response
        await asyncio.sleep(1)


async def get_result(model_info, server):
    s = "PLACEHOLDER" ### ???

    async for response in run(model_info, server):
        if s == response:
            break

        s = response

        # Print intermediate steps
#        print(response)

    # Print final result
#    print(response)

    print("LOL420\n\n" + s + "\n\nLOL420\nA") ### ???

    return s


def predict(input, server, model_info: ModelInfo):
    return run_async(get_result, model_info, server)


async def predict_stream(input, server, thread_manager, model_info: ModelInfo):
    s = input

    params = {
        'prompt': s,
        'max_new_tokens': max_tokens,
        'do_sample': do_sample,
        'temperature': temperature,
        'top_p': top_p,
        'typical_p': 1,
        'repetition_penalty': 1.1,
        'top_k': top_k,
        'min_length': 10,
        'no_repeat_ngram_size': no_repeat_ngram_size,
        'num_beams': num_beams,
        'penalty_alpha': 0,
        'length_penalty': length_penalty,
        'early_stopping': True,
    }

    async for i in get_result_stream(params, server):
        yield i


class ThreadManager:
    def __init__(self, prompt_template=None):
        self._prompt_template = prompt or open("prompt.txt", "r").read()
        self._threads = {}

    def new(self, func, args, kwargs):
        return thread

    def run_async(self, func, *args, **kwargs):
        # NOTE: sync, despite the name
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            thread = RunThread(func, args, kwargs)
            self._threads[thread.thread_id] = thread
            thread.start()
            thread.join()
        else:
            return asyncio.run(func(*args, **kwargs))

    def reset(self, thread_id):
        self._threads[thread_id] = self.prompt_template.format(date=str(datetime.datetime.now()))

    def full_history(self, thread_id):
        return self._threads[thread_id]

    def load_history(_threadthread_id, history):
        self._threads[thread_id] = history

    async def send_message_stream(self, txt, thread_id, input_txt_template, assistant_input_text_template):
        if not thread_id in self._threads:
            reset(thread_id)

        input_text = input_text_template.split("\n")[0].format(date=str(datetime.datetime.now()))
        assistant_input_text = assistant_input_text_template.split("\n")[0].format(date=str(datetime.datetime.now()))

        self._threads[thread_id] += input_text + txt + "\n" + assistant_input_text

        tmp = ""
        async for i in predict_stream(self._threads[thread_id], server, max_tokens=500, temperature=0.7, top_p=0.01, top_k=40, ):
            yield i[len(self._threads[thread_id]):]
            tmp = i[len(self._threads[thread_id]):]

        self._threads[thread_id] += tmp + "\n"
