import operator

from framework.types import type_registry, Parameterized
from framework.core.util import is_list

import framework.types.primitives as p

@type_registry.parameterized
def Range(type_, min_, max_, include_min=True, include_max=True):
    _assert_valid_type(type_, [p.Integer, p.Decimal])
    _assert_valid_args(type_, [min_, max_], allow_none=True)

    if min_ is None:
        include_min = False
    if max_ is None:
        include_max = False

    class Range(Parameterized):
        subtype = type_
        args = (min_, max_, include_min, include_max)

        @classmethod
        def dereference(cls, reference):
            reference = cls.normalize(reference)
            return cls.subtype.dereference(reference)

        @classmethod
        def instantiate(cls, argument, *extras):
            cls.check_type(argument)
            return cls.subtype.instantiate(argument, *extras)

        @classmethod
        def normalize(cls, reference):
            reference = cls.subtype.normalize(reference)
            cls._assert_valid_range(reference)
            return reference

        @classmethod
        def check_type(cls, argument):
            cls.subtype.check_type(argument)
            cls._assert_valid_range(argument)

        @classmethod
        def _assert_valid_range(cls, value):
            left_op = operator.le if include_min else operator.lt
            right_op = operator.le if include_max else operator.lt

            # equivalent to (for example): not (min_ < value < max_)
            if not ((min_ is None or left_op(min_, value)) and
                    (max_ is None or right_op(value, max_))):
                range_str = '%s%s, %s%s' % (
                    '[' if include_min else '(', min_, max_,
                    ']' if include_max else ')')
                raise TypeError('%r not in range %s.' % (value, range_str))

    return Range

@type_registry.parameterized
def List(type_):
    class List(Parameterized):
        subtype = type_
        args = ()

        @classmethod
        def dereference(cls, reference):
            return [cls.subtype.dereference(r) for r in
                    cls.normalize(reference)]

        @classmethod
        def instantiate(cls, argument, study, name):
            cls.check_type(argument)
            return [cls.subtype.instantiate(a, study, '%s_%d' % (name, i))
                    for i, a in enumerate(argument)]

        @classmethod
        def normalize(cls, reference):
            if not is_list(reference):
                reference = (reference,)
            return [cls.subtype.normalize(r) for r in reference]

        @classmethod
        def check_type(cls, argument):
            if not is_list(argument):
                raise TypeError("not a list")
            [cls.subtype.check_type(a) for a in argument]

    return List

@type_registry.parameterized
def ChooseOne(type_, options):
    _assert_valid_args(type_, options)
    opt_set = set(options)
    if len(options) != len(opt_set):
        raise TypeError("Duplicate option in %r." % options)
    options = opt_set

    class ChooseOne(Parameterized):
        subtype = type_
        args = options

        @classmethod
        def annotation(cls):
            return {
                'uri': cls.uri,
                'content': 'parameterized',
                'subtype': cls.subtype.annotation(),
                'args': list(cls.args)
            }

        @classmethod
        def dereference(cls, reference):
            reference = cls.normalize(reference)
            return cls.subtype.dereference(reference)

        @classmethod
        def instantiate(cls, argument, *extras):
            cls.check_type(argument)
            return cls.subtype.instantiate(argument, *extras)

        @classmethod
        def normalize(cls, reference):
            reference = cls.subtype.normalize(reference)
            if reference not in options:
                raise TypeError("%r is not a member of %r." % (reference,
                                                               options))
            return reference

        @classmethod
        def check_type(cls, argument):
            cls.subtype.check_type(argument)

            if argument not in options:
                raise TypeError("%r is not a member of %r." % (argument,
                                                               options))

    return ChooseOne

@type_registry.parameterized
def ChooseMany(type_, options):
    _assert_valid_args(type_, options)
    opt_set = set(options)
    if len(options) != len(opt_set):
        raise TypeError("Duplicate option in %r." % options)
    options = opt_set

    class ChooseMany(Parameterized):
        subtype = type_
        args = options

        @classmethod
        def annotation(cls):
            return {
                'uri': cls.uri,
                'content': 'parameterized',
                'subtype': cls.subtype.annotation(),
                'args': list(cls.args)
            }

        @classmethod
        def dereference(cls, reference):
            return [cls.subtype.dereference(r) for r in
                    cls.normalize(reference)]

        @classmethod
        def instantiate(cls, argument, study, name):
            cls.check_type(argument)
            return [cls.subtype.instantiate(a, study, "%s_%d" % (name, i))
                    for i, a in enumerate(argument)]

        @classmethod
        def normalize(cls, reference):
            if not is_list(reference):
                reference = (reference,)
            results = []
            for r in reference:
                r = cls.subtype.normalize(r)
                if r not in options:
                    raise TypeError(
                        "%r is not a member of %r." % (r, options))
                results.append(r)
            return results

        @classmethod
        def check_type(cls, argument):
            if not is_list(argument):
                raise TypeError("not a list")

            for a in argument:
                cls.subtype.check_type(a)
                if a not in options:
                    raise TypeError(
                        "%r is not a member of %r." % (a, options))

    return ChooseMany

def _assert_valid_args(type_, args, allow_none=False):
    for arg in args:
        if allow_none and arg is None:
            continue
        else:
            type_.normalize(arg)

def _assert_valid_type(type_, valid_types):
    if not any(map(lambda x: issubclass(type_, x), valid_types)):
        raise TypeError("Invalid type %r." % type(type_))
