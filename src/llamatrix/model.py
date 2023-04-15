class ModelInfo:
    DEFAULT_PARAMS = {
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

    def __init__(self, custom_params=None):
        self._params = {}

        self._params.update(self.__class__.DEFAULT_PARAMS)

        if custom_params:
            self._params.update(custom_params)

    def model_params_as_dict(self):
        return self._params

    def model_params_as_list(self):
        ## What is this for -- textgen-web-ui?
        return [
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
