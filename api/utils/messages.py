messages = {
    'error_page_number': 'Не корректный номер страницы',
    'error_id': 'Не корректный id',
    404: 'Страница не найдена',
    500: 'Ошибка сервера',
    'not_response': "Запрос к сайту завершился ошибкой",
    'error_parce': 'Ошибка парсинга',
    '404_all': 'Ничего не найдено',
    'rule34_connection_error': "Невозможно подключиться к сайту rule34",
    'rule34_error': 'Произошла ошибка при обработке данных с rule34',
    'shikimori_error': 'Произошла ошибка при обработке данных с shikimori',
    'shikimori_connection_error': "Невозможно подключиться к сайту shikimori",
}


def GetMessage(status):
    message = messages['not_response']
    if status == 404:
        message = messages[404]
    elif status == 500:
        message = messages['error_parce']
    return {"message": message}
