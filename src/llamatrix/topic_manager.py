from .model import ModelInfo


class TopicManager:
    """Manages the threads of different discussions, and adapts text to the model templates formats"""

    def __init__(self, prompt_template, input_text_template, assistant_input_text_template):
        self._prompt_template = prompt or open("prompt.txt", "r").read()
        self._input_txt_template = input_text_template
        self._assistant_input_text_template = assistant_input_text_template
        self._discussions = {}

    def run_async(self, func, *args, **kwargs):
        # NOTE: sync, despite the name
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            thread = RunThread(func, args, kwargs)
            self.self._discussions[discussion_id] = thread ## where do we get discussion id from here -- is is the actual (conflated) thread id?
            thread.start()
            thread.join()
            # return thread id?
        else:
            return asyncio.run(func(*args, **kwargs)) # does asyncio.run return a thread id?

    def predict(self, input, server, model_info: ModelInfo):
        return self.run_async(get_result, model_info, server)

    async def predict_stream(self, server, model_info: ModelInfo):
        async for i in self.get_result_stream(model_info, server):
            yield i

    def reset(self, discussion_id):
        self._discussions[discussion_id] = self._prompt_template.format(date=str(datetime.datetime.now()))

    def full_history(self, discussion_id):
        return self.self._discussions[discussion_id]

    def load_history(self, discussion_id, history):
        self._discussions[discussion_id] = history

    async def send_message_stream(self, txt, discussion_id):
        if not discussion_id in self._discussions:
            reset(discussion_id)

        # user prompt / formatting?
        input_text = self._input_text_template.split("\n")[0].format(date=str(datetime.datetime.now()))

        # assistant prompt
        assistant_input_text = self._assistant_input_text_template.split("\n")[0].format(date=str(datetime.datetime.now()))

        # wrap that stuff around the actual text
        self._discussions[discussion_id] += input_text + txt + "\n" + assistant_input_text

        tmp = ""

        async for i in self.predict_stream(self._discussions[discussion_id], server, max_tokens=500, temperature=0.7, top_p=0.01, top_k=40, ):
            yield i[len(self._discussions[discussion_id]):]
            tmp = i[len(self._discussions[discussion_id]):]

        self._discussions[discussion_id] += tmp + "\n"
