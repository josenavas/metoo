import inspect

class Method(object):
    def __init__(self, function, uri, name, docstring, annotations):
        self.uri = uri
        self.name = name
        self.docstring = docstring

        if type(annotations['return']) != tuple:
            annotations['return'] = (annotations['return'],)
        self.annotations = annotations

        spec = inspect.getfullargspec(function)
        if spec.defaults:
            kwarg_start = -len(spec.defaults)
            arg_order = spec.args[:kwarg_start]
            defaults = dict(zip(spec.args[kwarg_start:], spec.defaults))
        else:
            arg_order = spec.args
            defaults = {}

        self._arg_order = arg_order
        self._defaults = defaults
        self._function = function

    def __call__(self, study, *args, **kwargs):
        args = self._resolve_args(args)
        kwargs = self._resolve_kwargs(kwargs)
        results = self._function(*args, **kwargs)

        if type(results) != tuple:
            results = (results,)

        if len(results) != len(self.annotations['return']):
            raise Exception()

        for result_idx, (result, result_type) in enumerate(zip(results, self.annotations['return'])):
            if not isinstance(result, result_type.data_type):
                raise TypeError()

            # TODO handle output naming better
            result_type.save(result, study, '%s output %d' % (self.name, result_idx + 1))

    def _resolve_args(self, args):
        if len(self._arg_order) != len(args):
            raise ValueError("Expected %d arguments, received %d." %
                             (len(self._arg_order), len(args)))

        resolved_args = []
        for arg_name, arg in zip(self._arg_order, args):
            type_ = self.annotations[arg_name]
            resolved_args.append(type_.load(arg))
        return resolved_args

    def _resolve_kwargs(self, kwargs):
        resolved_kwargs = {}
        for key in self._defaults:
            type_ = self.annotations[key]

            if key in kwargs:
                resolved_kwargs[key] = type_.load(kwargs[key])
            else:
                resolved_kwargs[key] = type_.load(self._defaults[key])
        return resolved_kwargs
