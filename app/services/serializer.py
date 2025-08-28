from sqlalchemy.inspection import inspect


class Serializer(object):

    @staticmethod
    def serialize(obj):
        return {c: getattr(obj, c) for c in inspect(obj).attrs.keys()}

    @staticmethod
    def serialize_list(obj_list):
        return [Serializer.serialize(m) for m in obj_list]
