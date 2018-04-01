import functools
import hashlib

from urllib import parse

caches = {}
cache_zone = {}


def _cut_uri(uri):
    path = parse.urlparse(uri).path
    for i in range(len(path)-1, -1, -1):
        if path[i] == '/':
            path = path[:i]
        elif '0' <= path[i] <= '9':
            continue
        return path


def _before(self):
    _hash = None
    if self.request.method == 'GET':
        _hash_str = ''.join([self.request.method, self.request.uri])
        _hash = hashlib.md5(_hash_str.encode('utf-8')).hexdigest()
        if _hash in caches.keys():
            headers, write_buffer, status_code = caches[_hash]
            if headers:
                date_tmp = self._headers['Date']
                self._headers = headers.copy()
                self._headers['Date'] = date_tmp
                self._headers_written = True
            self._write_buffer = write_buffer
            self.set_status(status_code)
            return True, _hash
    return False, _hash


def _after(self, _hash):
    headers = None
    path = _cut_uri(self.request.uri)
    if _hash:
        if self._headers_written:
            headers = self._headers.copy()
        write_buffer = self._write_buffer.copy()
        status_code = self.get_status()
        caches[_hash] = (headers, write_buffer, status_code)
        if path in cache_zone:
            cache_zone[path].append(_hash)
        else:
            cache_zone[path] = [_hash]
    elif (self.request.method in ['PUT', 'PATCH', 'POST']
          and self.get_status() == 201) or (
            self.request.method == 'DELETE'
            and self.get_status() == 204):
        if path in cache_zone:
            for __hash in cache_zone[path]:
                del caches[__hash]
            del cache_zone[path]


def cached(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        cache, _hash = _before(self)
        if not cache:
            method(self, *args, **kwargs)
            _after(self, _hash)
    return wrapper


def cached_async(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        cache, _hash = _before(self)
        if not cache:
            await method(self, *args, **kwargs)
            _after(self, _hash)
    return wrapper
