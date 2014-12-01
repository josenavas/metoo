from qiime.types import type_registry, Primitive

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
Decimal = primitive_factory('Decimal', float)
String = primitive_factory('String', str)
Boolean = primitive_factory('Boolean', bool)
