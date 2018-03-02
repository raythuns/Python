import json
import os


CONFIG = {
    'PATH': os.path.dirname(os.path.abspath(__file__)),
}


class _JSONDBHandler:
    handler = {
        'path': None,
        'opened': False,
        'cache': None,
        'change': False,
    }

    @staticmethod
    def open(database):
        root = find = None
        if _JSONDBHandler.handler['opened']:
            raise RuntimeError("Don't open repeat.")
        _JSONDBHandler.handler['path'] = CONFIG['PATH'].strip('\\/')+'/'
        path0 = _JSONDBHandler.handler['path'] + 'jsondb.json'
        try:
            with open(path0, 'rt', encoding='utf-8') as f:
                root = json.load(f)
        except FileNotFoundError:
            root = {'collection': ['database'], 'database': {
                        'field': {
                            '0': {'name': 'name',
                                  'type': 'char',
                                  'length': 64}},
                        'document': [{'0': 'jsondb'}]}}
            _JSONDBHandler.handler['change'] = True
        path1 = _JSONDBHandler.handler['path'] + database + '.json'
        try:
            with open(path1, 'rt', encoding='utf-8') as f:
                find = json.load(f)
        except FileNotFoundError:
            find = {'collection': []}
            root['database']['document'].append({'0': database})
            _JSONDBHandler.handler['change'] = True
        _JSONDBHandler.handler['opened'] = True
        _JSONDBHandler.handler['cache'] = {
            'root': root, 'find': find, 'trans': None, 'name': database}

    @staticmethod
    def save():
        if not _JSONDBHandler.handler['opened']:
            raise RuntimeError("Handler is closed.")
        if _JSONDBHandler.handler['change']:
            path0 = _JSONDBHandler.handler['path'] + 'jsondb.json'
            with open(path0, 'wt', encoding='utf-8') as f:
                json.dump(_JSONDBHandler.handler['cache']['root'], f)
            path1 = _JSONDBHandler.handler['path'] + \
                _JSONDBHandler.handler['cache']['name'] + '.json'
            with open(path1, 'wt', encoding='utf-8') as f:
                json.dump(_JSONDBHandler.handler['cache']['root'], f)
            _JSONDBHandler.handler['change'] = False

    @staticmethod
    def close():
        if not _JSONDBHandler.handler['opened']:
            raise RuntimeError("Handler is closed.")
        _JSONDBHandler.save()
        _JSONDBHandler.handler['path'] = None
        _JSONDBHandler.handler['opened'] = False
        _JSONDBHandler.handler['cache'] = None
