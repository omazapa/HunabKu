
import sys


class Config:
    """
    Config class provides a way to create and manage a configuration object in Python.
    This class uses the __setattr__, __getattr__, keys, __getitem__, __setitem__, get, 
    and update methods to enable easy access and modification of configuration values.

    Overall, the Config class provides a convenient way to manage configuration values
    in Python with an easy-to-use API.
    """

    def __init__(self):
        self.__docs__ = {}
        self.__fromparam__ = False
        if "__docs__" in self.__docs__:
            del self.__docs__["__docs__"]
        if "__fromparam__" in self.__docs__:
            del self.__docs__["__fromparam__"]

    def __setattr__(self, key: str, value: any):
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
        self.__docs__[key] = ""

    def __getattr__(self, key: str):
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
        _keys = list(self.__dict__.keys())
        _keys.remove("__docs__")
        _keys.remove("__fromparam__")
        return _keys

    def __getitem__(self, key: str):
        return self.__dict__[key]

    def __setitem__(self, key: str, value: any):
        self.__dict__[key] = value

    def __call__(self, **kwargs):
        doc = ""
        if "doc" in kwargs:
            doc = kwargs["doc"]
            del kwargs["doc"]
        name = list(kwargs.keys())[0]
        self[name] = kwargs[name]
        self.__doc[name] = doc
        return self

    def get(self, key: str) -> any:
        return self.__dict__.get(key, None)

    def update(self, config):
        self.__dict__.update(config.__dict__)

    def __iadd__(self, other):
        name = list(other.keys())[0]
        value = other[name]
        doc = other.__docs__[name]
        self[name] = value
        self.__docs__[name] = doc
        self.__fromparam__ = False
        if "__fromparam__" in self.__docs__:
            del self.__docs__["__fromparam__"]
        return self

    def fromparam(self):
        return self.__fromparam__

    def doc(self, doc):
        """
        Used when Param(db="Colav").doc("MongoDB database name") is called,
        Param only has one key.
        """
        if self.fromparam():
            name = list(self.keys())[0]
            self.__docs__[name] = doc
            return self
        else:
            print("ERROR: this method only can be call from class Param",
                  file=sys.stderr)
            sys.exit(1)


class Param:
    """
    Class to pass parameters to the Hunabku configuration system:

    from hunabku.Config import Config, Param
    class MyPlugin(HunabkuPluginBase)
        config = Config()
        config += Param(db="test",doc="Database name")
        config += Param(port=8080).doc("port to connect is a remote service") #is possible pass documentation using the method .doc
        config += Param(debug=True) # you can leave a parameter without documentation if you prefer.

    """
    def __new__(cls, **kwargs):
        if len(kwargs) == 0:
            print(
                "ERROR: Param can not be empty, at least one param have to be provided ex: Param(var='test')")
            sys.exit(1)

        if len(kwargs) > 2:
            print("ERROR: A maximum of two parameters can be passed, the parameter and the doc for the parameter ex: Param(db='test', doc='databaset name')")
            sys.exit(1)

        name = list(kwargs.keys())[0]
        if len(kwargs) == 2:
            doc = ""
            if "doc" in kwargs:
                doc = kwargs["doc"]
                del kwargs["doc"]
            else:
                print(f"ERROR: in Parameter {name}, doc parameter not provide.\n" +
                      "       Two parameters can be provided but the second one have to be 'doc' ex: Param(db='test', doc='databaset name')")
                sys.exit(1)

        name = list(kwargs.keys())[0]
        value = kwargs[name]
        config = Config()
        config.__fromparam__ = True
        config[name] = value
        config.__docs__[name] = ""
        return config
