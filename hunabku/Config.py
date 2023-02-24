class Wrap:
    def __new__(cls, value, doc=None):
        class SubWrap(value.__class__):
            def __new__(_cls, _value, _doc=None):
                obj = _value.__class__.__new__(_cls, _value)
                obj.__doc__ = _doc
                return obj
        return SubWrap(value, doc)

class Config:
    """
    Config class provides a way to create and manage a configuration object in Python.
    This class uses the __setattr__, __getattr__, keys, __getitem__, __setitem__, get, 
    and update methods to enable easy access and modification of configuration values.

    Overall, the Config class provides a convenient way to manage configuration values
    in Python with an easy-to-use API.
    """
    def __setattr__(self, key: Wrap, value: Wrap):
        """
        Set the attribute `value` to the given `key` in the `__dict__` dictionary of the `Config` object.

        Parameters
        ----------
        key : str
            The key of the attribute.
        value : Any
            The value to be set to the attribute.

        Returns
        -------
        None
        """
        self.__dict__[key] = value

    def __getattr__(self, key: Wrap):
        """
        Retrieve the attribute value for the given `key` from the `__dict__` dictionary of the `Config` object.

        Parameters
        ----------
        key : str
            The key of the attribute.

        Returns
        -------
        Any
            The value of the attribute with the given `key`.
        """
        value = self.__dict__.get(key, None)
        if value is not None:
            return value
        else:
            self.__dict__[key] = Config()
            return self.__dict__[key]

    def keys(self) -> list[Wrap]:
        return self.__dict__.keys()

    def __getitem__(self, key: Wrap):
        return self.__dict__[key]

    def __setitem__(self, key: Wrap, value: Wrap):
        self.__dict__[key] = value

    def get(self, key: Wrap) -> Wrap:
        return self.__dict__.get(key, None)

    def update(self, config:Config):
        self.__dict__.update(config.__dict__)


class Param:
    def __new__(self, **kwargs):
        doc = ""
        if "doc" in kwargs:
            doc = kwargs["doc"]
            del kwargs["doc"]
        name = Wrap(list(kwargs.keys())[0])
        name.__doc__ = doc
        value = kwargs[name]
        value = Wrap(value)
        config = Config()
        config[name] = value
        config[name].__doc__ = doc
        return config
