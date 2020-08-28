import os

api_key = input('api key: ')

with open(os.path.join(os.path.dirname(__file__), 'config.py'), 'w', encoding='utf-8') as config_file:
    config_file.write(f'API_KEY = "{api_key}"')
