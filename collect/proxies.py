from typing import Any

import yaml


def parse_proxies(filename='proxies.yaml') -> list[str]:
    '''Parses proxies config file and returns list of connection strings'''
    with open(filename) as f:
        root: dict[str, Any] = yaml.safe_load(f)

    global_login = root.get('login', None)
    global_password = root.get('password', None)
    global_proto = root.get('proto', None)
    global_port = root.get('port', None)

    result = []
    for proxy in root['proxies']:
        login = proxy.get('login', global_login)
        password = proxy.get('password', global_password)
        proto = proxy.get('proto', global_proto)
        port = proxy.get('port', global_port)
        ip = proxy['ip']

        result.append(f'{proto}://{login}:{password}@{ip}:{port}')

    return result
