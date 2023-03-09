
from flask import (
    json,
    request
)
from bson import ObjectId
from functools import wraps
from hunabku.Config import Config

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
    Specilaized decorator to use in the methods of the class that inherit from  HunabkuPluginBase
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
        if _verbose:
            print('------ Adding endpoint ' + path + ' with methods' + str(methods))
        class_name, func_name = func.__qualname__.split('.')
        if class_name not in _endpoints:
            _endpoints[class_name] = []
        _endpoints[class_name].append(
            {'path': path, 'methods': methods, 'func_name': func_name})

        @wraps(func)
        def _impl(self, *method_args, **method_kwargs):
            response = func(self, *method_args, **method_kwargs)
            return response
        _impl.__name__ = func.__qualname__ ##WARNING: this is required to avoid overwrite methods in the class
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
            for endpoint_data in _endpoints[type(self).__name__]:
                path = endpoint_data['path']
                func_name = endpoint_data['func_name']
                methods = endpoint_data['methods']
                func = getattr(self, func_name)
                self.app.add_url_rule(path, view_func=func, methods=methods)

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
        plugins = list(_endpoints.keys())
        current = type(self).__name__
        plugins.remove(current)
        paths = []
        for register in _endpoints[current]:
            paths.append(register['path'])
        for path in paths:
            for plugin in plugins:
                for register in _endpoints[plugin]:
                    if path == register['path']:
                        self.logger.error(
                            "ERROR: can't not load plugin, {} because the path {} is already loaded in plugin {}".format(
                                current, path, plugin))
                        return False
        return True
