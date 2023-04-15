import asyncio
import datetime
import json
import random
import re
import websockets

import requests

from .model import ModelInfo
from .utils import random_hash, RunThread


async def run_chatbot(model_info: ModelInfo, websockets_server):
    session = random_hash()

    n = 0

    async with websockets.connect(websockets_server) as websocket:
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
                all_data = [model_info.prompt()] + model_info.model_params_as_list()

                hash_dict_json = json.dumps({
                    "session_hash": session,
                    "fn_index": 7,
                    "data": all_data,
                })

                await websocket.send()

            elif msg_content == "process_starts":
                pass

            elif msg_content in ("process_generating", "process_completed"):
                ret_me = content["output"]["data"][0]
                do_it = False

                prompt = model_info.prompt()
                prompt_len = len(prompt)

                print(ret_me[prompt_len:])

                if "Human (" in ret_me[prompt_len:]:
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


async def get_result_stream(model_info: ModelInfo, websockets_server):
    s = "PLACEHOLDER"

    async for response in run_chatbot(model_info, websockets_server):
        if s == response:
            break
        s = response
        yield response
        await asyncio.sleep(1)


async def get_result(model_info, websockets_server):
    s = "PLACEHOLDER" ### ???

    async for response in run_chatbot(model_info, websockets_server):
        if s == response:
            break

        s = response

        # Print intermediate steps
#        print(response)

    # Print final result
#    print(response)

    print("LOL420\n\n" + s + "\n\nLOL420\nA") ### ???

    return s
