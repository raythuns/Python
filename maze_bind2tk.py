import tkinter as tk
from maze import *


keypress_event = {
    'a': try_move_to_left,
    'A': try_move_to_left,
    'd': try_move_to_right,
    'D': try_move_to_right,
    'w': try_move_to_up,
    'W': try_move_to_up,
    's': try_move_to_down,
    'S': try_move_to_down,
}

root = box = textvar = None


def a_default_box():
    return [['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
            ['w', ' ', ' ', ' ', 'w', ' ', ' ', ' ', ' ', 'w', 'w'],
            ['w', 'w', ' ', 'w', 'w', ' ', 'w', 'w', ' ', 'w', 'w'],
            ['w', ' ', ' ', 'p', 'w', ' ', 'w', ' ', ' ', ' ', 'w'],
            ['w', ' ', 'w', 'w', 'w', 'w', ' ', ' ', 'w', ' ', 'w'],
            ['w', ' ', ' ', ' ', ' ', 'w', ' ', 'w', 'w', ' ', 'w'],
            ['w', 'w', ' ', 'w', ' ', ' ', ' ', 'w', ' ', ' ', 'w'],
            ['w', 'w', ' ', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
            ['w', 'w', ' ', ' ', 'w', 'w', ' ', ' ', ' ', 'w', 'w'],
            ['w', 'w', 'w', ' ', ' ', ' ', ' ', 'w', ' ', ' ', ' '],
            ['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w']]


def update_box(textvar):
    sbox = ''.join(before_print_box(box))
    pbox = sbox.replace(':\n', '\n')
    textvar.set(pbox)


def keypress(event):
    c = event.char
    if c in keypress_event:
        keypress_event[c](box)
        update_box(textvar)
        if test_win(box):
            root.quit()


def main():
    global root, box, textvar
    root = tk.Tk()
    box = a_default_box()
    textvar = tk.StringVar()
    update_box(textvar)
    label = tk.Label(root, textvariable=textvar,
                     justify='left', font=('monospace', 9))
    label.pack()
    root.bind('<Key>', keypress)
    root.mainloop()


if __name__ == '__main__':
    main()
