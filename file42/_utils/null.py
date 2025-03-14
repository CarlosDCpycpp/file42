class SingletonMeta(type):
    def __new__(cls, name: str, bases: tuple, namespace: dict):
        _instance = None
        namespace['_instance'] = _instance
        return super().__new__(cls, name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
            return cls._instance
        raise RuntimeError(f'An instance of the Singleton class "{cls.__name__}" already exists.')


def obj(cls: type) -> object:
    return SingletonMeta(cls.__name__, cls.__bases__, dict(cls.__dict__))()


@obj
class Null:
    def __str__(self):
        return f'<{self.__class__.__name__}>'

    def __bool__(self):
        return False
