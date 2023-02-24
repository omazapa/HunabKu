class Str(str):
    """
    Clase personalizada que hereda de la clase str.
    Permite definir un docstring para una cadena.
    """
    def __new__(cls, value, doc=None):
        obj = str.__new__(cls, value)
        obj.__doc__ = doc
        return obj


class Config:
    """
    Config class provides a way to create and manage a configuration object in Python.
    This class uses the __setattr__, __getattr__, keys, __getitem__, __setitem__, get, 
    and update methods to enable easy access and modification of configuration values.

    Overall, the Config class provides a convenient way to manage configuration values
    in Python with an easy-to-use API.
    """
    def __setattr__(self, key: Str, value: any):
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
        if isinstance(value, str):
            value = Str(value)
        self.__dict__[key] = value

    def __getattr__(self, key: Str):
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

    def keys(self) -> list[str]:

        keys = []
        for key in self.__dict__.keys():
            keys.append(Str(key))
        return keys

    def __getitem__(self, key: Str):
        return self.__dict__[key]

    def __setitem__(self, key: Str, value):
        if isinstance(value, str):
            value = Str(value)
        self.__dict__[key] = value

    def get(self, key: Str):
        return self.__dict__.get(key, None)

    def update(self, config):
        self.__dict__.update(config)


class Param:
    def __new__(self, **kwargs):
        doc = ""
        if "doc" in kwargs:
            doc = kwargs["doc"]
            del kwargs["doc"]
        name = Str(list(kwargs.keys())[0])
        name.__doc__ = doc
        value = kwargs[name]
        if isinstance(value, str):
            value = Str(value)
        config = Config()
        config[name] = value
        config[name].__doc__ = doc
        return config
