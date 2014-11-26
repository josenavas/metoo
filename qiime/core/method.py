import inspect

class Method(object):
    def __init__(self, function, uri, name, docstring, annotations):
        self.uri = uri
        self.name = name
        self.docstring = docstring

        if type(annotations['return']) != tuple:
            annotations['return'] = (annotations['return'],)

        self.outputs = annotations.pop('return')
        self.inputs = annotations

        spec = inspect.getfullargspec(function)
        if spec.defaults:
            kwarg_start = -len(spec.defaults)
            defaults = dict(zip(spec.args[kwarg_start:], spec.defaults))
        else:
            defaults = {}

        self._input_names = spec.args
        self._defaults = defaults
        self._function = function

    def __call__(self, study, **kwargs):
        kwargs = self._resolve_kwargs(kwargs)
        results = self._function(**kwargs)

        if type(results) != tuple:
            results = (results,)

        if len(results) != len(self.outputs):
            raise Exception()

        for result_idx, (result, result_type) in enumerate(zip(results, self.outputs)):
            if not isinstance(result, result_type.data_type):
                raise TypeError()

            # TODO handle output naming better
            result_type.save(result, study, '%s output %d' % (self.name, result_idx + 1))

    def _resolve_kwargs(self, kwargs):
        if len(kwargs) > len(self._input_names):
            raise ValueError("Expected %d inputs, received %d." %
                             (len(self._input_names), len(kwargs)))
        resolved_kwargs = {}
        for input_name in self._input_names:
            type_ = self.inputs[input_name]

            if input_name in kwargs:
                resolved_kwargs[input_name] = type_.load(kwargs[input_name])
            elif input_name in self._defaults:
                resolved_kwargs[input_name] = type_.load(self._defaults[input_name])
            else:
                raise TypeError("Missing input %r." % input_name)
        return resolved_kwargs
