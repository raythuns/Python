#!/usr/bin/env python
import sys


def before_print_box(box):
  for i in range(len(box)):
    for j in range(len(box[0])):
      if box[i][j] == 'w':
        j2 = j-1 if j > 0 else 0
        if box[i][j2] == 'p' or box[i][j2] == ' ':
          yield ':w:'
        else:
          yield 'w:'
      else:
        j3 = j+1 if j < len(box[0])-1 else len(box[0])-1
        if box[i][j3] == 'w':
          yield box[i][j]
        else:
          yield box[i][j] + ' '
    yield '\n'


def print_box(box):
  sbox = ''.join(before_print_box(box))
  pbox = sbox.replace(':\n', '\n')
  sys.stdout.write(pbox)


def get_sub(box):
  for i in range(len(box)):
    for j in range(len(box[0])):
      if box[i][j] == 'p':
        return i, j
  raise ValueError('get_sub(): p is not exist.')


def test_win(box):
  sub = get_sub(box)
  i = sub[0]
  j = sub[1]
  if (i-1 < 0 or i+1 >= len(box)) or (j-1 < 0 or j+1 >=len(box[0])):
    print('You Win!')
    return True
  return False


def try_move_to_left(box):
  sub = get_sub(box)
  i = sub[0]
  j = sub[1]
  j2 = j-1 if j > 0 else 0
  if box[i][j2] == ' ':
    box[i][j] = ' '
    box[i][j2] = 'p'
    return True
  return False


def try_move_to_right(box):
  sub = get_sub(box)
  i = sub[0]
  j = sub[1]
  j2 = j+1 if j < len(box[0])-1 else len(box[0])-1
  if box[i][j2] == ' ':
    box[i][j] = ' '
    box[i][j2] = 'p'
    return True
  return False


def try_move_to_up(box):
  sub = get_sub(box)
  i = sub[0]
  j = sub[1]
  i2 = i-1 if i > 0 else 0
  if box[i2][j] == ' ':
    box[i][j] = ' '
    box[i2][j] = 'p'
    return True
  return False


def try_move_to_down(box):
  sub = get_sub(box)
  i = sub[0]
  j = sub[1]
  i2 = i+1 if i < len(box)-1 else len(box)-1
  if box[i2][j] == ' ':
    box[i][j] = ' '
    box[i2][j] = 'p'
    return True
  return False


def main():
  box = [['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'], \
         ['w', ' ', ' ', ' ', 'w', ' ', ' ', ' ', ' ', 'w', 'w'], \
         ['w', 'w', ' ', 'w', 'w', ' ', 'w', 'w', ' ', 'w', 'w'], \
         ['w', ' ', ' ', 'p', 'w', ' ', 'w', ' ', ' ', ' ', 'w'], \
         ['w', ' ', 'w', 'w', 'w', 'w', ' ', ' ', 'w', ' ', 'w'], \
         ['w', ' ', ' ', ' ', ' ', 'w', ' ', 'w', 'w', ' ', 'w'], \
         ['w', 'w', ' ', 'w', ' ', ' ', ' ', 'w', ' ', ' ', 'w'], \
         ['w', 'w', ' ', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'], \
         ['w', 'w', ' ', ' ', 'w', 'w', ' ', ' ', ' ', 'w', 'w'], \
         ['w', 'w', 'w', ' ', ' ', ' ', ' ', 'w', ' ', ' ', ' '], \
         ['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w']]
  # sub = list(get_sub(box))
  end = False
  while not test_win(box) and not end:
     print_box(box)
     for c in sys.stdin.readline().strip('\n'):
       if c == 'w':
         if try_move_to_up(box):
           sys.stdout.write('up.')
       elif c == 'a':
         if try_move_to_left(box):
           sys.stdout.write('left.')
       elif c == 's':
         if try_move_to_down(box):
           sys.stdout.write('down.')
       elif c == 'd':
         if try_move_to_right(box):
           sys.stdout.write('right.')
       elif c == 'q':
         end = True
         break
       else:
         break
     sys.stdout.write('\n')


if __name__ == '__main__':
  main()