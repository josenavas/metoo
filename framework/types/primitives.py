from framework.types import type_registry, Primitive

def primitive_factory(class_name, primitive):
    class _(Primitive):
        @classmethod
        def normalize(cls, data):
            try:
                return primitive(data)
            except ValueError:
                raise TypeError()

    _.__name__ = class_name
    type_registry.primitive(_)
    return _

Integer = primitive_factory('Integer', int)
Decimal = primitive_factory('Decimal', float) # TODO should this be Real
Boolean = primitive_factory(
    'Boolean',
    lambda e: True if e == b'true' else False # TODO handle this better
)
String = primitive_factory(
    'String',
    lambda e: e.decode('utf-8') if isinstance(e, bytes) else str(e)
)

# TODO add Date type
