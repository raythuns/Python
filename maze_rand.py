import random


def base_nodes(row, col):
    return [['n' for _ in range(col)] for _ in range(row)]


def safe_direction(base_direction, r, c, row, col):
    if r == 0:
        base_direction = base_direction.replace('u', '')
    elif r == row-1:
        base_direction = base_direction.replace('d', '')
    if c == 0:
        base_direction = base_direction.replace('l', '')
    elif c == col-1:
        base_direction = base_direction.replace('r', '')
    return base_direction


def rand_direction(pos_r, pos_c, row, col):
    rand_chars = safe_direction('lrud', pos_r, pos_c, row, col)
    rand_num = random.randint(1, len(rand_chars))
    return ''.join(random.sample(rand_chars, rand_num))


def next_node(pos_r, pos_c, next_directiton):
    if next_directiton == 'l':
        pos_c -= 1
    elif next_directiton == 'r':
        pos_c += 1
    elif next_directiton == 'u':
        pos_r -= 1
    elif next_directiton == 'd':
        pos_r += 1
    return pos_r, pos_c


def dfs_visit(nodes, pos_r, pos_c, group):
    for next_direction in nodes[pos_r][pos_c]:
        _next_r, _next_c = next_node(pos_r, pos_c, next_direction)
        if nodes[_next_r][_next_c] == 'n':
            nodes[_next_r][_next_c] = rand_direction(
                _next_r, _next_c, len(nodes), len(nodes[0]))
            dfs_visit(nodes, _next_r, _next_c, group)
        else:
            nodes[pos_r][pos_c] = nodes[pos_r][pos_c].replace(
                next_direction, '')
    if nodes[pos_r][pos_c] == '':
        nodes[pos_r][pos_c] = 'e'
    nodes[pos_r][pos_c] = group + nodes[pos_r][pos_c]


def contact_tree(nodes, r, c):
    def node_state(state):
        num, direc = [], []
        end = False
        for a in state:
            if a in 'lurd':
                direc.append(a)
            elif a == 'b':
                pass
            elif a == 'e':
                end = True
            else:
                num.append(a)
        return int(''.join(num)), set(direc), end
    stack = []
    row = len(nodes)
    col = len(nodes[0])
    while True:
        group, direction, end = node_state(nodes[r][c])
        for find in set(safe_direction('lurd', r, c, row, col)) - direction:
            _next_r, _next_c = next_node(r, c, find)
            g, _, _ = node_state(nodes[_next_r][_next_c])
            if g != group:
                nodes[r][c] = nodes[r][c] + find
                return
        if end and len(stack) != 0:
            r, c, direction = stack.pop()
        else:
            return
        r, c = next_node(r, c, direction.pop())
        if len(direction) != 0:
            stack.append(((r, c), direction))


def dfs_route(nodes):
    row = len(nodes)
    col = len(nodes[0])
    pos = [(r, c) for r in range(row) for c in range(col)]
    random.shuffle(pos)
    gengroup = iter(range(int(row*col-1)))
    beginlist = []
    for r, c in pos:
        if nodes[r][c] == 'n':
            group = str(next(gengroup))
            nodes[r][c] = rand_direction(r, c, row, col)
            dfs_visit(nodes, r, c, group)
            nodes[r][c] = 'b' + nodes[r][c]
            beginlist.append((r, c))
    for r, c in beginlist:
        contact_tree(nodes, r, c)
    return beginlist


def blank_position_in_box(nodes):
    position = {
        'l': lambda r, c: (r, c-1),
        'r': lambda r, c: (r, c+1),
        'u': lambda r, c: (r-1, c),
        'd': lambda r, c: (r+1, c),
    }
    row = len(nodes)
    col = len(nodes[0])
    for r in range(row):
        r_ = r * 2 + 1
        for c in range(col):
            c_ = c * 2 + 1
            yield r_, c_
            for d in nodes[r][c]:
                try:
                    yield position[d](r_, c_)
                except:
                    pass


def find_a_exit(begin_r, begin_c, row, col):
    res_r = res_c = 0
    if begin_r < row/2:
        res_r = row - 1
    if begin_c < col/2:
        res_c = col - 1
    return res_r, res_c


def build_box(row, col):
    nodes = base_nodes(row, col)
    beginlist = dfs_route(nodes)
    box = [['w' for _ in range(col*2+1)] for _ in range(row*2+1)]
    for r, c in blank_position_in_box(nodes):
        box[r][c] = ' '
    r, c = beginlist[0]
    box[r*2+1][c*2+1] = 'p'
    exit_r, exit_c = find_a_exit(r, c, row, col)
    box[exit_r*2+1][0 if exit_c == 0 else exit_c*2+2] = ' '
    return box
