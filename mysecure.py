import getpass
import pyaes
import sqlite3
import hashlib
import string
import random


conn = None
_name_lock = None


class Key:
    _k = None

    @staticmethod
    def set(key: bytes):
        if key is None:
            Key._k = None
            return
        Key._k = list(key)
        for i in range(len(Key._k)):
            Key._k[i] ^= hash('salt')

    @staticmethod
    def get():
        return bytes([Key._k[i] ^ hash('salt') for i in range(len(Key._k))])

    @staticmethod
    def setted():
        if Key._k:
            return True
        return False


def init_db(path=None):
    global conn, _name_lock
    if path is None:
        for i in range(len(__file__)-1, -1, -1):
            if __file__[i] in ('/', '\\'):
                path = ''.join([__file__[:i+1], 'secure.db'])
                break
    conn = sqlite3.connect(path)
    c = conn.cursor()
    try:
        c.execute('create table verify(id primary key not null'
                  ', verify_key text not null, name_lock text not null)')
        c.execute('create table content(id integer primary key autoincrement'
                  ' not null, name text not null, account text not null, pass'
                  'word text not null, extra text, random_key text not null)')
        print('create new sqlite3 database file (%s) success.' % path)
    except sqlite3.OperationalError:
        pass
    c.close()
    _name_lock = None


def new_random_key(length=32):
    return ''.join(random.sample(
        string.ascii_letters + string.digits, length))


def aes_encrypts(s: str, key, no_padding=False):
    if isinstance(s, str):
        s = s.encode('utf-8')
    if isinstance(key, str):
        key = key.encode('utf-8')
    aes_ = pyaes.AESModeOfOperationCBC(key)
    if no_padding and len(s)/16-int(len(s)/16) == 0:
        s_ = s
    else:
        s_ = pyaes.util.append_PKCS7_padding(s)
    r = list()
    for i in range(int(len(s_)/16)):
        r.append(aes_.encrypt(s_[i*16:(i+1)*16]))
    return b''.join(r)


def aes_decrypts(b: bytes, key, no_padding=False):
    if isinstance(key, str):
        key = key.encode('utf-8')
    aes_ = pyaes.AESModeOfOperationCBC(key)
    r = list()
    for i in range(int(len(b)/16)):
        r.append(aes_.decrypt(b[i*16:(i+1)*16]))
    if no_padding:
        return b''.join(r).decode('utf-8')
    return pyaes.util.strip_PKCS7_padding(b''.join(r)).decode('utf-8')


def add_sign(s: str):
    s_ = list(s)
    for i in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        s_[i] = '\x7f'
    return ''.join(s_)


def veri_sign(s: str):
    for i in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        if s[i] != '\x7f':
            return False
    return True


def get_password(prompt):
    _pw = getpass.getpass(prompt)
    if len(_pw) not in range(4, 19):
        print('incorrect password length (must 4-18).')
        return None
    for ch in _pw:
        if 'A' <= ch <= 'Z' or 'a' <= ch <= 'z' or '0' <= ch <= '9':
            continue
        if ch in ('!', '@', '#', '$', '-', '_'):
            continue
        print('incorrect password spell (must by 0-9 a-Z !@#$-_ ).')
        return None
    return _pw


def require_key():
    if Key.setted():
        return True
    if conn is None:
        init_db()
    c = conn.cursor()
    c.execute('select verify_key from verify where id=0')
    v = c.fetchone()
    if v is None:
        c.execute('select count(*) from content')
        if c.fetchone()[0] != 0:
            return False
        print('creating new password to your database:')
        passwd = get_password('Password:')
        passwd2 = get_password('Password Again:')
        if passwd is None or passwd != passwd2:
            print('inconsistent password.')
            return False
        Key.set(hashlib.sha256(passwd.encode('utf-8')).digest())
        rs = new_random_key()
        nk = new_random_key()
        signed = add_sign(rs)
        enc = aes_encrypts(signed, Key.get(), True)
        enc2 = aes_encrypts(nk, Key.get(), True)
        c.execute('insert into verify values (0, ?, ?)', (enc, enc2))
        conn.commit()
        c.close()
    else:
        print('verifying your password of database:')
        passwd = get_password('Password:')
        if passwd is None:
            return False
        Key.set(hashlib.sha256(passwd.encode('utf-8')).digest())
        try:
            dec = aes_decrypts(v[0], Key.get(), True)
            verified = veri_sign(dec)
        except UnicodeDecodeError:
            verified = False
        if not verified:
            print('incorrect password.')
            Key.set(None)
            return False
    return True


def get_name_lock_key():
    global _name_lock
    if _name_lock is None:
        c = conn.cursor()
        c.execute('select name_lock from verify where id=0')
        _name_lock = c.fetchone()[0]
        c.close()
    _name_lock_de = aes_decrypts(_name_lock, Key.get(), True)
    return add_sign(_name_lock_de)


def add_mode():
    while True:
        a = input('(ADD)>> ')
        if len(a) > 5 and a[:5] == 'name ':
            name = a[5:]
            print('Name:', name)
            account = input('Account: ')
            if len(account) == 0:
                continue
            passwd = getpass.getpass('Password: ')
            if len(passwd) == 0:
                continue
            passwd2 = getpass.getpass('Password Again: ')
            if passwd != passwd2:
                print('inconsistent password.')
                continue
            extra = input('Add Extra: ')
            random_key = new_random_key()
            name_en = aes_encrypts(name, get_name_lock_key())
            account_en = aes_encrypts(account, random_key)
            passwd_en = aes_encrypts(passwd, random_key)
            extra_en = aes_encrypts(extra, random_key)
            random_key_en = aes_encrypts(random_key, Key.get(), True)
            c = conn.cursor()
            c.execute('insert into content values (NULL, ?, ?, ?, ?, ?)', (
                name_en, account_en, passwd_en, extra_en, random_key_en))
            conn.commit()
            c.close()
        elif a in ('exit', 'quit'):
            break


def command_list():
        c = conn.cursor()
        c.execute('select name from content')
        datas = list(set(i[0] for i in c.fetchall()))
        row_pos = 0
        min_col = 5
        for data in datas:
            name = aes_decrypts(data, get_name_lock_key())
            if row_pos < min_col-1:
                print(name, end='\t')
                row_pos += 1
            else:
                print(name)
                row_pos = 0
        if len(datas) % min_col > 0:
            print('')
        c.close()


def view_mode():
    while True:
        a = input('(VIEW)>> ')
        if len(a) > 5 and a[:5] in ('name ', 'info '):
            name = a[5:]
            name_en = aes_encrypts(name, get_name_lock_key())
            c = conn.cursor()
            c.execute('select random_key, account, password, extra'
                      ' from content where name=?', (name_en,))
            datas = c.fetchall()
            print('find %d account(s).' % len(datas))
            random_key_cache = []
            for i in range(len(datas)):
                random_key = aes_decrypts(datas[i][0], Key.get(), True)
                account = aes_decrypts(datas[i][1], random_key)
                print('[%d] %s' % (i+1, account))
                random_key_cache.append(random_key)
            if len(datas) > 0:
                if a[:5] == 'name ':
                    a1 = input('Choose to view password: ')
                    for n in a1.split(' '):
                        if n.isdecimal() and 0 < int(n) <= len(datas):
                            idx = int(n)-1
                            passwd = aes_decrypts(
                                datas[idx][2], random_key_cache[idx])
                            print('[%s] |%s|' % (n, passwd))
                        else:
                            break
                else:
                    a1 = input('Choose to view extra: ')
                    for n in a1.split(' '):
                        if n.isdecimal() and 0 < int(n) <= len(datas):
                            idx = int(n)-1
                            extra = aes_decrypts(
                                datas[idx][3], random_key_cache[idx])
                            print('[%s]:\n%s' % (n, extra))
                        else:
                            break
            c.close()
        elif a == 'list':
            command_list()
        elif a in ('exit', 'quit'):
            break


def remove_mode():
    while True:
        a = input('(REMOVE)>> ')
        if len(a) > 5 and a[:5] == 'name ':
            name = a[5:]
            name_en = aes_encrypts(name, get_name_lock_key())
            c = conn.cursor()
            c.execute('select random_key, account, id'
                      ' from content where name=?', (name_en,))
            datas = c.fetchall()
            print('find %d account(s).' % len(datas))
            for i in range(len(datas)):
                random_key = aes_decrypts(datas[i][0], Key.get(), True)
                account = aes_decrypts(datas[i][1], random_key)
                print('[%d] %s' % (i+1, account))
            if len(datas) > 0:
                a1 = input('Choose to delete: ')
                for n in a1.split(' '):
                    if n.isdecimal() and 0 < int(n) <= len(datas):
                        c.execute('delete from content where id=?',
                                  (datas[int(n)-1][2],))
                    else:
                        break
                conn.commit()
            c.close()
        elif a in ('exit', 'quit'):
            break


def change_mode():
    while True:
        a = input('(CHANGE)>> ')
        if len(a) > 5 and a[:5] == 'name ':
            name = a[5:]
            name_en = aes_encrypts(name, get_name_lock_key())
            c = conn.cursor()
            c.execute('select random_key, account, extra, id'
                      ' from content where name=?', (name_en,))
            datas = c.fetchall()
            print('find %d account(s).' % len(datas))
            random_key_cache = []
            for i in range(len(datas)):
                random_key = aes_decrypts(datas[i][0], Key.get(), True)
                account = aes_decrypts(datas[i][1], random_key)
                print('[%d] %s' % (i+1, account))
                random_key_cache.append(random_key)
            if len(datas) > 0:
                a1 = input('Choose to change password/extra: ')
                for n in a1.split(' '):
                    if n.isdecimal() and 0 < int(n) <= len(datas):
                        passwd = getpass.getpass('[%s]New Password: ' % n)
                        if len(passwd) == 0:
                            continue
                        passwd2 = getpass.getpass(
                            '[%s]New Password Again: ' % n)
                        if passwd != passwd2:
                            print('inconsistent password.')
                            continue
                        extra = input('[%s]Add Extra: ' % n)
                        idx = int(n)-1
                        passwd_ch_en = aes_encrypts(
                            passwd, random_key_cache[idx])
                        if len(extra) > 0:
                            extra_de = aes_decrypts(
                                datas[idx][2], random_key_cache[idx])
                            if len(extra_de) > 0:
                                extra_ch = extra_de + '\n' + extra
                            else:
                                extra_ch = extra
                            extra_ch_en = aes_encrypts(
                                extra_ch, random_key_cache[idx])
                            c.execute(
                                'update content set password=?,'
                                ' extra=? where id=?',
                                (passwd_ch_en, extra_ch_en, datas[idx][3]))
                        else:
                            c.execute(
                                'update content set password=? where id=?',
                                (passwd_ch_en, datas[idx][3]))
                    else:
                        break
                    conn.commit()
                    c.close()
        if a in ('exit', 'quit'):
            break


def change_password():
    if conn is None:
        init_db()
    old_passwd = get_password('Old Password: ')
    c = conn.cursor()
    c.execute('select verify_key, name_lock from verify where id=0')
    v = c.fetchone()
    if v:
        old_key = hashlib.sha256(old_passwd.encode('utf-8')).digest()
        dec = aes_decrypts(v[0], old_key, True)
        if not veri_sign(dec):
            print('incorrect password.')
            return
        new_passwd = get_password('New Password: ')
        new_passwd2 = get_password('New Password Again: ')
        if len(new_passwd) == 0 or new_passwd != new_passwd2:
            print('inconsistent password.')
            return
        new_key = hashlib.sha256(new_passwd.encode('utf-8')).digest()
        enc = aes_encrypts(dec, new_key, True)
        enc2 = aes_encrypts(aes_decrypts(v[1], old_key, True),
                            new_key, True)
        c.execute('select id, random_key from content')
        rows = c.fetchall()
        rencs = []
        for row in rows:
            random_key_de = aes_decrypts(row[1], old_key, True)
            rencs.append((aes_encrypts(random_key_de, new_key, True),
                          row[0]))
        c.execute('update verify set verify_key=?, name_lock=? where id=0',
                  (enc, enc2))
        c.executemany('update content set random_key=? where id=?', rencs)
        conn.commit()
    else:
        print('database error.')
    c.close()


def main():
    while True:
        try:
            a = input('>> ')
        except KeyboardInterrupt:
            print('\nBye.')
            break
        if len(a) == 0:
            continue
        try:
            if a == 'add':
                if require_key():
                    add_mode()
                    Key.set(None)
            elif a == 'view':
                if require_key():
                    view_mode()
                    Key.set(None)
            elif a == 'remove':
                if require_key():
                    remove_mode()
                    Key.set(None)
            elif a == 'change':
                if require_key():
                    change_mode()
                    Key.set(None)
            elif a == 'passwd':
                change_password()
            elif a == 'help':
                print('Usage:\tadd | view | remove |'
                      ' change | passwd')
                print('Then:\tlist | name | info')
            elif a in ('quit', 'exit'):
                raise SystemExit
        except SystemExit:
            print('Bye.')
            break
        except KeyboardInterrupt:
            Key.set(None)
            print('')


if __name__ == '__main__':
    print('Welcome to MySecure !')
    main()
