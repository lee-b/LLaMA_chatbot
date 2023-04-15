from enum import Enum, auto, unique

@unique
class ModelParam(Enum):
    MAX_NEW_TOKENS = auto()
    DO_SAMPLE = auto()
    TEMPERATURE = auto()
    TOP_P = auto()
    TYPICAL_P = auto()
    REPETITION_PENALTY = auto()
    TOP_K = auto()
    MIN_LENGTH = auto()
    NO_REPEAT_NGRAM_SIZE = auto()
    NUM_BEAMS = auto()
    PENALTY_ALPHA = auto()
    LENGTH_PENALTY = auto()
    EARLY_STOPPING = auto()

class ModelInfo:
    DEFAULT_PARAMS = {
        ModelParam.MAX_NEW_TOKENS: 200,
        ModelParam.DO_SAMPLE: True,
        ModelParam.TEMPERATURE: 0.5,
        ModelParam.TOP_P: 0.9,
        ModelParam.TYPICAL_P: 1.0,
        ModelParam.REPETITION_PENALTY: 1.05,
        ModelParam.TOP_K = 0.0,
        ModelParam.MIN_LENGTH = 0,
        ModelParam.NO_REPEAT_NGRAM_SIZE = 0,
        ModelParam.NUM_BEAMS = 1,
        ModelParam.PENALTY_ALPHA = 0.0,
        ModelParam.LENGTH_PENALTY = 1.0,
        ModelParam.EARLY_STOPPING = False,
    }

    def __init__(self, prompt, custom_params=None):
        self._prompt = prompt
        self._params = {}
        self._params.update(self.__class__.DEFAULT_PARAMS)

        if custom_params:
            self._params.update(custom_params)

    def prompt(self):
        return self._prompt

    def model_params_as_dict(self):
        return self._params

    def model_params_as_list(self):
        ## What is this for? textgen-web-ui takes params in this order, I guess?
        return [
            self._params[self.prompt()],
            self._params[ModelParam.MAX_NEW_TOKENS],
            self._params[ModelParam.DO_SAMPLE],
            self._params[ModelParam.TEMPERATURE],
            self._params[ModelParam.TOP_P],
            self._params[ModelParam.TYPICAL_P],
            self._params[ModelParam.REPETITION_PENALTY],
            self._params[ModelParam.TOP_K],
            self._params[ModelParam.MIN_LENGTH],
            self._params[ModelParam.NO_REPEAT_NGRAM_SIZE],
            self._params[ModelParam.NUM_BEAMS],
            self._params[ModelParam.PENALTY_ALPHA],
            self._params[ModelParam.LENGTH_PENALTY],
            self._params[ModelParam.EARLY_STOPPING],
        ]
