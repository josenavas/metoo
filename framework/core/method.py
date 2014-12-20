import inspect
from framework.types import BaseType

class Method(object):
    def __init__(self, function, uri, name, docstring, annotations):
        self.uri = uri
        self.name = name
        self.docstring = docstring

        if type(annotations['return']) != tuple:
            annotations['return'] = (annotations['return'],)

        outputs = annotations.pop('return')
        inputs = annotations

        for key, annotation in inputs.items():
            if not issubclass(annotation, BaseType):
                raise TypeError("Annotation for %r in %r is not a registered type." % (key, function.__name__))


        for annotation in outputs:
            if not issubclass(annotation, BaseType):
                raise TypeError("Return annotation %r in %r is not a registered type." % (annotation, function.__name__))


        self.outputs = outputs
        self.inputs = inputs

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

        return [t.instantiate(r, study, '%s output %d' % (self.name, i))
                for i, (t, r) in enumerate(zip(self.outputs, results))]


    def _resolve_kwargs(self, kwargs):
        if len(kwargs) > len(self._input_names):
            raise ValueError("Expected %d inputs, received %d." %
                             (len(self._input_names), len(kwargs)))
        resolved_kwargs = {}
        for input_name in self._input_names:
            type_ = self.inputs[input_name]

            if input_name in kwargs:
                resolved_kwargs[input_name] = type_.dereference(kwargs[input_name])
            elif input_name in self._defaults:
                resolved_kwargs[input_name] = type_.dereference(self._defaults[input_name])
            else:
                raise TypeError("Missing input %r." % input_name)
        return resolved_kwargs
