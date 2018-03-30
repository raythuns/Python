import functools
import hashlib

caches = {}


def _before(self):
    _hash = None
    if self.request.method == 'GET':
        _hash_str = ''.join([self.request.method, self.request.uri])
        _hash = hashlib.md5(_hash_str.encode('utf-8')).hexdigest()
        if _hash in caches.keys():
            headers, write_buffer = caches[_hash]
            if headers:
                date_tmp = self._headers['Date']
                self._headers = headers.copy()
                self._headers['Date'] = date_tmp
                self._headers_written = True
            self._write_buffer = write_buffer
            return True, _hash
    return False, _hash


def _after(self, _hash):
    headers = None
    if self._headers_written:
        headers = self._headers.copy()
    write_buffer = self._write_buffer.copy()
    caches[_hash] = (headers, write_buffer)


def cached(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        cache, _hash = _before(self)
        if not cache:
            method(self, *args, **kwargs)
            if _hash:
                _after(self, _hash)
    return wrapper


def cached_async(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        cache, _hash = _before(self)
        if not cache:
            await method(self, *args, **kwargs)
            if _hash:
                _after(self, _hash)
    return wrapper
