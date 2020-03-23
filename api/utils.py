# Base for the API management (No need for Django Rest :P)


import json
import random

from django.http import JsonResponse
from django.views import View

import string
from django.utils.text import slugify


class StatusCode(View):
    # Success Codes
    HTTP_200_OK = 200
    # Client Error Codes
    HTTP_400_BAD_REQUEST = 400
    #Server Error Codes
    HTTP_500_INTERNAL_SERVER_ERROR = 500



# This class is for wrapping the json response
class JsonWrapper(JsonResponse):
    def __init__(self, data, flag):
        wrapper_dic = {
            'status': flag,
            'data': data
        }
        super(JsonWrapper, self).__init__(wrapper_dic, status=flag, json_dumps_params={"indent": 4})


# Decorator for getting data from raw body data
def get_raw_data(func):
    def get_data(request, *args, **kwargs):
        json_data = request.body

        try:
            request.DATA = json.loads(json_data.decode('utf-8'))

        except Exception as e:
            dic = {'message': "Please provide json data and GET Method is not allowed", "error": e.args}
            flag = StatusCode.HTTP_400_BAD_REQUEST
            return JsonWrapper(dic, flag)

        return func(request, *args, **kwargs)

    return get_data

#API base View Extended from Django generic view
class ApiView(View):

    flag = StatusCode.HTTP_400_BAD_REQUEST
    NULL_VALUE_VALIDATE = [None, '', ' ']

    def get(self, request, *args, **kwargs):
        dic = {'message': "GET Method is not allowed"}
        return JsonWrapper(dic, StatusCode.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        dic = {'message': "POST Method is not allowed"}
        return JsonWrapper(dic, StatusCode.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, request, *args, **kwargs):
        dic = {'message': "PUT Method is not allowed"}
        return JsonWrapper(dic, StatusCode.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        dic = {'message': "DELETE Method is not allowed"}
        return JsonWrapper(dic, StatusCode.HTTP_405_METHOD_NOT_ALLOWED)



def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(random_string_generator())
    class_obj = instance.__class__
    qs_exists = class_obj.objects.filter(slug=slug).exists()

    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug, randstr=random_string_generator(size=4))

        return unique_slug_generator(instance, new_slug=new_slug)
    return slug