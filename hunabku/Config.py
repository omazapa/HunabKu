
import sys
import os
import logging


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
    def __new__(cls, **kwargs):
        if len(kwargs) == 0:
            print(
                "ERROR: Param can not be empty, at least one param have to be provided ex: Param(var='test')")
            sys.exit(1)

        if len(kwargs) > 2:
            print("ERROR: A maximum of two parameters can be passed, the parameter and the doc for the parameter ex: Param(db='test', doc='databaset name')")
            sys.exit(1)

        name = list(kwargs.keys())[0]
        doc = ""
        if len(kwargs) == 2:
            if "doc" in kwargs:
                doc = kwargs["doc"]
                del kwargs["doc"]
            else:
                print(f"ERROR: in Parameter {name}, doc parameter not provide." + os.linesep +
                      "       Two parameters can be provided but the second one have to be 'doc' ex: Param(db='test', doc='databaset name')")
                sys.exit(1)

        name = list(kwargs.keys())[0]
        value = kwargs[name]
        config = Config()
        config.__fromparam__ = True
        config[name] = value
        config.__docs__[name] = doc
        return config


class ConfigGenerator:
    config = Config()

    config += Param(host="localhost", doc="Hostname or ip for flask server.")

    config += Param(port=8080,
                    doc="Port for flask server.")

    config += Param(log_file="hunabku.log",
                    doc="Name for logging file. "
                        "This is only enable in logging level different to DEBUG.")

    config += Param(use_reloader=True,
                    doc="Flask allows to reload the endpoint if something is changed in the code.\n"
                        "Set this False to void reload code.")

    config += Param(info_level=logging.DEBUG,
                    doc="The logging level, default DEBUG, set it to INFO for production.")

    config += Param(apikey=os.environ["HUNABKU_APIKEY"] if "HUNABKU_APIKEY" in os.environ else "colavudea",
                    doc="Apikey for authentication.")

    def generate_config(self, output_file, hunabku, overwrite):
        if len(hunabku.plugins) == 0:
            hunabku.load_plugins(verbose=False)
        output = "from hunabku.Config import Config"+os.linesep
        output += "config = Config() "+os.linesep*2
        for key in self.config.keys():
            doc = self.config.__docs__[key]
            output += f"# {key} "+os.linesep
            comments = doc.split(os.linesep)
            for comment in comments:
                output += f"# {comment} "+os.linesep

            value = self.config[key]
            if isinstance(value, str):
                output += f'config.{key} = "{value}" '+os.linesep*2
            else:
                output += f'config.{key} = {value} '+os.linesep*2

        for plugin in hunabku.plugins:
            for key in plugin['class'].config.keys():
                output += f"# {key} "+os.linesep
                output += f"#{plugin['class'].config.__docs__[key]} "+os.linesep
                value = plugin["class"].config[key]
                if isinstance(value, str):
                    output += f'config.{plugin["package"]}.{plugin["mod_name"]}.{plugin["mod_name"]}.{key} = "{value}"'+os.linesep*2
                else:
                    output += f'config.{plugin["package"]}.{plugin["mod_name"]}.{plugin["mod_name"]}.{key} = {value}'+os.linesep*2

        if overwrite:
            with open(output_file, "w") as f:
                f.write(output)
                f.close()
            return True
        else:
            if os.path.exists(output_file):
                return False
            else:
                with open(output_file, "w") as f:
                    f.write(output)
                    f.close()
                return True
