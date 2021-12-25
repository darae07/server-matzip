def request_data_handler(data, required_fields, other_fields):
    formatted_data = data
    for field in required_fields:
        try:
            value = formatted_data[field]
        except KeyError:
            raise Exception('필수 파라미터' + field + '가 누락되었습니다.')

    for field in other_fields:
        try:
            value = formatted_data[field]
        except KeyError:
            formatted_data[field] = None
