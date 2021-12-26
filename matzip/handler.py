from rest_framework import views


def request_data_handler(data, required_fields=None, other_fields=None):
    formatted_data = data
    if isinstance(required_fields, list):
        for field in required_fields:
            try:
                value = formatted_data[field]
            except KeyError:
                raise Exception('필수 파라미터' + field + '가 누락되었습니다.')

    if isinstance(other_fields, list):
        for field in other_fields:
            try:
                value = formatted_data[field]
            except KeyError:
                formatted_data[field] = None

    return formatted_data


def exception_handler(exc, context):
    response = views.exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code
    return response
