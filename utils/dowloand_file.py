import requests

def download_file(url):
    """Загрузка файла по ссылке"""
    
    response = requests.get(url)
    
    return response.content
