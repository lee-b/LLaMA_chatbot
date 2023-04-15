import datetime
import re

import requests

'''

Contributed by SagsMug. Thank you SagsMug.
https://github.com/oobabooga/text-generation-webui/pull/175

'''

import asyncio
import json
import random
import string

import websockets


def random_hash():
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(9))


params = {}


async def run(context, server):
    default_context = {
        'max_new_tokens': 200,
        'do_sample': True,
        'temperature': 0.5,
        'top_p': 0.9,
        'typical_p': 1,
        'repetition_penalty': 1.05,
        'top_k': 0,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
    }
    params = {}
    params.update(default_context)
    params.update(context)
    session = random_hash()

    n = 0

    async with websockets.connect(f"ws://{server}:7860/queue/join") as websocket:
        while content := json.loads(await websocket.recv()):
            msg_content = content["msg"]

            if msg_content == "send_hash":
                await websocket.send(json.dumps({
                    "session_hash": session,
                    "fn_index": 7
                }))
            elif msg_content == "estimation":
                    pass
            elif msg_content == "send_data":
                    await websocket.send(json.dumps({
                        "session_hash": session,
                        "fn_index": 7,
                        "data": [
                            params["prompt"],
                            params['max_new_tokens'],
                            params['do_sample'],
                            params['temperature'],
                            params['top_p'],
                            params['typical_p'],
                            params['repetition_penalty'],
                            params['top_k'],
                            params['min_length'],
                            params['no_repeat_ngram_size'],
                            params['num_beams'],
                            params['penalty_alpha'],
                            params['length_penalty'],
                            params['early_stopping'],
                        ]
                    }))
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

async def get_result_stream(params, server):
    s = "PLACEHOLDER"
    async for response in run(params, server):
        if s == response:
            break
        s = response
        yield response
        await asyncio.sleep(1)

async def get_result(params, server):
    s = "PLACEHOLDER"
    async for response in run(params, server):
        if s == response:
            break
        s = response
        # Print intermediate steps
#        print(response)

    # Print final result
#    print(response)
    print("LOL420\n\n" + s + "\n\nLOL420\nA")
    return s

print("ready")

import threading

class RunThread(threading.Thread):
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        super().__init__()

    def run(self):
        self.result = asyncio.run(self.func(*self.args, **self.kwargs))

def run_async(func, *args, **kwargs):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        thread = RunThread(func, args, kwargs)
        thread.start()
        thread.join()
        return thread.result
    else:
        return asyncio.run(func(*args, **kwargs))

def predict(input, server, temperature=0.7,top_p=0.01,top_k=40,max_tokens=500,no_repeat_ngram_size=0,num_beams=1,do_sample=True,length_penalty=5):
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

    return run_async(get_result, params, server)

async def predict_stream(input, server, temperature=0.7,top_p=0.01,top_k=40,max_tokens=500,no_repeat_ngram_size=0,num_beams=1,do_sample=True,length_penalty=5):
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

prompt = open("prompt.txt", "r").read().format(date=str(datetime.datetime.now()))
input_text = open("input.txt", "r").read().split("\n")[0].format(date=str(datetime.datetime.now()))

s = prompt

threads = {}

def reset(thread_id):
    global threads
    prompt = open("prompt.txt", "r").read().format(date=str(datetime.datetime.now()))
    threads[thread_id] = prompt

def full_history(thread_id):
    return threads[thread_id]

def load_history(thread_id, history):
    threads[thread_id] = history

def send_message(txt, thread_id, server):
    global threads

    input_text = open("input.txt", "r").read().split("\n")[0].format(date=str(datetime.datetime.now()))

    if not thread_id in threads:
        reset(thread_id)

    assistant_input_text = open("assistant_input.txt", "r").read().split("\n")[0].format(date=str(datetime.datetime.now()))

    threads[thread_id] += input_text + txt + "\n" + assistant_input_text
    tmp = predict(threads[thread_id], server, max_tokens=500, temperature=0.7, top_p=0.01, top_k=40, )
    tmp = (tmp[len(threads[thread_id]):])

    print(tmp)

    threads[thread_id] += tmp + "\n"
    return tmp

async def send_message_stream(txt, thread_id):
    global threads

    input_text = open("input.txt", "r").read().split("\n")[0].format(date=str(datetime.datetime.now()))

    if not thread_id in threads:
        reset(thread_id)

    assistant_input_text = open("assistant_input.txt", "r").read().split("\n")[0].format(date=str(datetime.datetime.now()))
    threads[thread_id] += input_text + txt + "\n" + assistant_input_text

    tmp = ""
    async for i in predict_stream(threads[thread_id], server, max_tokens=500, temperature=0.7, top_p=0.01, top_k=40, ):
        yield i[len(threads[thread_id]):]
        tmp = i[len(threads[thread_id]):]

    threads[thread_id] += tmp + "\n"
