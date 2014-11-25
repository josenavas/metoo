from qiime.types import type_registry, PrimitiveType

def primitive_factory(class_name, primitive):
    class _(PrimitiveType):
        @classmethod
        def normalize(cls, data):
            return primitive(data)

        @classmethod
        def load(cls, data):
            return cls.normalize(data)
    _.__name__ = class_name
    type_registry.primitive(_)
    return _

Integer = primitive_factory('Integer', int)
Decimal = primitive_factory('Decimal', float)
String = primitive_factory('String', str)
Boolean = primitive_factory('Boolean', bool)
