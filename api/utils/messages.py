messages = {
    'error_page_number': 'Не корректный номер страницы',
    'error_id': 'Не корректный id',
    404: 'На сайте нет информации по данному запросу',
    'not_response': "Запрос к сайту завершился ошибкой",
    'error_parce': 'Ошибка парсинга',
    '404_all': 'Ничего не найдено',
}


def GetMessage(status):
    message = messages['not_response']
    if status == 404:
        message = messages[404]
    elif status == 500:
        message = messages['error_parce']
    return {"message": message}
