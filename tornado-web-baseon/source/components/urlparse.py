from tornado.web import url


def urlparse(rule, shadow_list):
    rst = []
    for s in shadow_list:
        if (len(s) > 2 and isinstance(s[2], str)) or\
                (len(s) > 3 and isinstance(s[3], str)):
            rst.append(url(r'%s/%s' % (rule, s[0]),
                           *s[1:-1], name=s[-1]))
        else:
            rst.append((r'%s/%s' % (rule, s[0]), *s[1:]))
    return rst
