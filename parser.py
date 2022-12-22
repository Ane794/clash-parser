import re
import sys

from ruamel import yaml


class Parser:
    @staticmethod
    def read_yaml(_path: str, **_kwargs):
        _file = open(_path, 'r', **_kwargs)
        _yaml = yaml.safe_load(_file)
        _file.close()
        return _yaml

    @staticmethod
    def yaml(_origin, _parser):
        _result = _origin

        for _key in ['rules', 'proxies', 'proxy-groups']:
            _result[_key] = (_parser.get(f'prepend-{_key}') if _parser.get(f'prepend-{_key}') else []) + \
                            (_origin.get(_key) if _origin.get(_key) else []) + \
                            (_parser.get(f'append-{_key}') if _parser.get(f'append-{_key}') else [])

        # TODO: mix-[proxy, rule]-providers

        # TODO: mix-object

        for _command in _parser.get('commands'):
            _result = Parser._execute(_result, _command)

        return _result

    @staticmethod
    def _execute(_origin, _command):
        _result = _origin

        _target_keys = ['']
        _value_str = ''
        _op = ''

        # 分析定位, 運算符.
        _flag = False
        for _ in range(len(_command)):
            if _command[_] == '(':
                _flag = True
            elif _command[_] == ')':
                _flag = False
            elif not _flag:
                if _command[_] == '.':
                    _target_keys.append('')
                elif _command[_] == '+' or _command[_] == '=':
                    if _target_keys[-1] == '':
                        _target_keys.pop()
                    _op = _command[_]
                    _value_str = _command[_ + 1:]
                    break
                else:
                    _target_keys[-1] += _command[_]
            else:
                _target_keys[-1] += _command[_]

        _value = None
        if (_op == '+' or _op == '=') and _value_str:
            # 分析設定值.
            if _value_str.startswith('[]'):
                _split = _value_str.find('|')
                if _split != -1:  # e.g. []proxyNames|foo
                    _key = _value_str[2:_split]
                    _reg = _value_str[_split + 1:]
                else:  # e.g. []proxyNames
                    _key = _value_str[2:]
                    _reg = ''
                _value = list(filter(
                    lambda _: re.match(_reg, _),
                    [_.get('name')
                     for _ in _result.get(
                        {
                            'proxyNames': 'proxies',
                            'groupNames': 'proxy-groups',
                        }[_key]
                    )],
                ))
            else:
                _value = _value_str

        elif not _op and not _value_str:
            if not _target_keys[-1].endswith('-'):
                return _result
            _op = '-'
            _target_keys[-1] = _target_keys[-1][0:-1]
        else:
            return _result

        _objs = []
        _o = _result
        for _ in range(len(_target_keys) - 1):
            _objs.append(_o)
            _o = _o[Parser._get_key(_o, _target_keys[_])]

        _key = Parser._get_key(_o, _target_keys[-1])
        if _op == '-':
            _o.pop(_key)
        elif _op == '+':
            _o.insert(_key, _value)
        elif _op == '=':
            _o.__setitem__(_key, _value)

        for _ in range(len(_target_keys) - 2, -1, -1):
            _p = _objs.pop()
            _p[Parser._get_key(_p, _target_keys[_])] = _o
            _o = _p

        _result = _o

        return _result

    @staticmethod
    def _get_key(_obj, _key):
        if type(_obj) is list:
            if _key.isdecimal():
                return int(_key) if int(_key) <= len(_obj) else len(_obj)
            else:
                for _ in range(len(_obj)):
                    if _obj[_].get('name') == _key:
                        return _
        return _key


if __name__ == '__main__':
    origin_file = sys.argv[1]
    parser_file = sys.argv[2]

    origin = Parser.read_yaml(origin_file, encoding='UTF-8')
    parser = Parser.read_yaml(parser_file, encoding='UTF-8')

    result = yaml.dump(
        Parser.yaml(origin, parser),
        Dumper=yaml.RoundTripDumper,
        allow_unicode=True,
    )

    print(result)
