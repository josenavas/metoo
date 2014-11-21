import inspect

class Method(object):
    def __init__(self, uri, name, function, annotations, docstring):
        self.uri = uri
        self.name = name
        self.annotations = annotations
        self.docstring = docstring

        spec = inspect.getfullargspec(function)
        if spec.defaults:
            kwarg_start = -len(spec.defaults)
            arg_names = spec.args[:kwarg_start]
            kwargs_ = dict(zip(spec.args[kwarg_start:], spec.defaults))
        else:
            arg_names = spec.args

        self.arg_names = arg_names
        def wrapped_action(*args, **kwargs):
            if len(args) != len(arg_names):
                raise Exception()
            for arg, name in zip(args, arg_names):
                if type(arg) != annotations[name]:
                    raise Exception()
            for name in kwargs:
                if type(kwargs[name]) != annotations[name]:
                    raise Exception()

            f_result = function(*[a.data for a in args], **kwargs)
            if type(f_result) != tuple:
                f_result = (f_result,)
            return_types = annotations['return']
            if type(return_types) != tuple:
                return_types = (annotations['return'],)

            results = []
            for r, t in zip(f_result, return_types):
                results.append(t(r))
            return tuple(results)

        self._action = wrapped_action

    def __call__(self, study, *args, hmac=None, **kwargs):
        # Parallelism goes here
        result = self._action(*self._resolve_uris(*args), **kwargs)
        for result_artifact in result:
            result_artifact.save(study)

    def _resolve_uris(self, *artifact_uris):
        if len(self.arg_names) != len(artifact_uris):
            raise ValueError("Expected %d artifact URIs, received %d." %
                             (len(self.arg_names), len(artifact_uris)))

        artifacts = []
        for arg_name, uri in zip(self.arg_names, artifact_uris):
            artifact_cls = self.annotations[arg_name]
            artifact = artifact_cls.from_uri(uri)
            artifacts.append(artifact)
        return artifacts
