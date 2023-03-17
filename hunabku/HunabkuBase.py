
from flask import (
    json,
    request
)
from bson import ObjectId
from functools import wraps
from hunabku.Config import Config
import inspect
import os
import sys


class HunabkuJsonEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for Hunabku,
    all the customized stuff for encoding required for our endpoints
    can be handle in this class
    """

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


_endpoints = {}  # global hidden dictionary to register every endpoint by plugin
_verbose = True


def set_verbose(status):
    global _verbose
    _verbose = status


def endpoint(path, methods):
    """
    Specialized decorator to use in the methods of the class that inherit from  HunabkuPluginBase
    this decorator allows to register the path and methods [GET,POST,DELETE,PUT]
    in the flask app.

    example:
    class Hello(HunabkuPluginBase):
    def __init__(self,hunabku):
        super().__init__(hunabku)

    @endpoint('/hello',methods=['GET'])
    def hello(self):
        if self.valid_apikey():
            response = self.app.response_class(
                response=self.json.dumps({'hello':'world'}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.send_apikey_error()

    """
    def wrapper(func):
        global _endpoints
        global _verbose
        current_frame = inspect.currentframe()

        caller_frame = inspect.getouterframes(current_frame, 2)[1]
        filename = caller_frame.filename
        package_name = caller_frame.filename.split(
            "endpoints")[0].split(os.sep)[-2]
        class_name, func_name = func.__qualname__.split('.')

        if _verbose:
            print(
                f'------ Adding endpoint {path} with HTTP(S) methods {str(methods)} from class = {class_name} class method = {func_name}')

        if package_name not in _endpoints:
            _endpoints[package_name] = []
        _endpoints[package_name].append(
            {'path': path, 'methods': methods, 'func_name': func_name, 'class_name': class_name, 'file': filename})

        @wraps(func)
        def _impl(self, *method_args, **method_kwargs):
            response = func(self, *method_args, **method_kwargs)
            return response
        # WARNING: this is required to avoid overwrite methods in the class
        _impl.__name__ = func.__qualname__
        return _impl
    return wrapper


class HunabkuPluginBase(object):
    config = Config()

    def __init__(self, hunabku):
        """
        Base class to handle the plugins.
        Allows to have access to the MondoDB object, custom json methods
        with our encoders, utility functions to check apikeys and send default messages
        in case of error.

        This class allows to register the endpoints setting a decorator in the method
        that is going to hanlde the endpoint.

        """
        self.global_config = hunabku.config
        self.app = hunabku.app
        self.request = request
        self.json = json
        self.logger = hunabku.logger
        self.hunabku = hunabku
        _dumps = self.json.dumps
        _dump = self.json.dump

        # added support to our json encoder
        def json_dumps(
                obj,
                skipkeys=False,
                ensure_ascii=True,
                check_circular=True,
                allow_nan=True,
                cls=HunabkuJsonEncoder,
                indent=None,
                separators=None,
                default=None,
                sort_keys=False):
            return _dumps(
                obj=obj,
                skipkeys=skipkeys,
                ensure_ascii=ensure_ascii,
                check_circular=check_circular,
                allow_nan=allow_nan,
                cls=cls,
                indent=indent,
                separators=separators,
                default=default,
                sort_keys=sort_keys)

        def json_dump(
                obj,
                skipkeys=False,
                ensure_ascii=True,
                check_circular=True,
                allow_nan=True,
                cls=HunabkuJsonEncoder,
                indent=None,
                separators=None,
                default=None,
                sort_keys=False):
            return _dump(
                obj=obj,
                skipkeys=skipkeys,
                ensure_ascii=ensure_ascii,
                check_circular=check_circular,
                allow_nan=allow_nan,
                cls=cls,
                indent=indent,
                separators=separators,
                default=default,
                sort_keys=sort_keys)
        # custimized encoder use by default
        self.json.dumps = json_dumps
        self.json.dump = json_dump

    def apikey_error(self):
        """
        return defualt apikey error
        """
        response = self.app.response_class(
            response=self.json.dumps(
                {'msg': 'The HTTP 401 Unauthorized invalid authentication apikey for the target resource.'}),
            status=401,
            mimetype='application/json'
        )
        return response

    def badrequest_error(self):
        """
        return defualt bad request error
        """
        data = {"error": "Bad Request",
                "message": "Invalid parameters passed. Please fix your request with valid parameters."}
        response = self.app.response_class(response=self.json.dumps(data),
                                           status=400,
                                           mimetype='application/json')
        return response

    def valid_apikey(self):
        if self.request.method == 'POST':
            apikey = self.request.form.get('apikey')
        else:
            apikey = self.request.args.get('apikey')
        if self.global_config["apikey"] == apikey:
            return True
        else:
            return False

    def register_endpoints(self):
        """
        Method to register all the endpoints in flask's app
        """
        global _endpoints
        if self.has_valid_endpoints():
            for endpoint_data in _endpoints[self._get_package_name()]:
                path = endpoint_data['path']
                func_name = endpoint_data['func_name']
                methods = endpoint_data['methods']
                func = getattr(self, func_name)
                self.app.add_url_rule(path, view_func=func, methods=methods)
        else:
            sys.exit(1)

    def valid_parameters(self, params):
        """
        Method to check is the parameters passed to the endpoint are valid,
        if unkown parameter is passed, a bad request is returned.
        """
        if self.request.method == 'POST':
            args = self.request.form
        else:
            args = self.request.args

        for rarg in args:
            if rarg not in params:
                return False
        return True

    @classmethod
    def get_global_endpoints(cls):
        """
        Method to return the global dictionary with all
        the registers  loaded
        """
        return _endpoints

    def has_valid_endpoints(self):
        """
        This method checks before to load the plugin if any paths in the endpoint is repeated.
        this platform does not allows overwrite endpoint paths.
        """
        global _endpoints
        package_name = self._get_package_name()
        class_name = type(self).__name__
        plugins = list(_endpoints.keys())
        plugins.remove(package_name)
        endpoints = []
        for register in _endpoints[package_name]:
            endpoints.append(register)

        for endpoint in endpoints:
            for plugin in plugins:
                for register in _endpoints[plugin]:
                    if endpoint["path"] == register['path']:
                        self.logger.error(
                            f"ERROR: can't not load plugin, package {package_name} class {class_name} class_method {endpoint['func_name']} "
                            f"because the path {endpoint['path']} is already loaded in plugin: package {plugin} class {register['class_name']} "
                            f"class_method {register['func_name']}")
                        return False
        return True

    def _get_package_name(self):
        filename = inspect.getfile(self.__class__)
        package_name = filename.split(
            "endpoints")[0].split(os.sep)[-2]
        return package_name
