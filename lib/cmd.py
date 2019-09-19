'''
Created by Valentin Solina, Part of mipyshell project
Super simple, VT100 compatible, Command line interpreter helper class
'''

import sys
sread = sys.stdin.read
swrite = sys.stdout.write


class Cmd:
    def __init__(self):
        self._line = ""
        self._idx = 0
        self.prompt = "cmd> "
        self.history = []
        self._history_idx = 0
        pass
    
    def cmdloop(self):
        self.redraw_line()
#        sys.stdout.swrite(self.prompt)
        self._idx = 0#len(self.prompt)
        kmap_1ch = {'\x7f': self._backspace, '\t': self._tab, '\n': self._enter}
        kmap_2ch = {'A': self._up, 'B': self._down, 'C': self._right, 'D': self._left, 'H': self._home, 'F': self._end}
        kmap_3ch = {'3': self._delete}#, '5': self._pgup, '6': self._pgdown}
        while True:
            c = sread(1)
            if c == '\x1b':
                c2 = sread(1)
                if c2 == '[':
                    c3 = sread(1)
                    if c3 in kmap_2ch.keys():
                        kmap_2ch[c3]()
                    elif c3 in kmap_3ch.keys():
                        _ = sread(1)
                        kmap_3ch[c3]()
            elif c in kmap_1ch.keys():
                kmap_1ch[c]()
            else:
                if len(self._line) == self._idx:
                    self._line += c
                    self._idx += 1
                    swrite(c)
                else:
                    self._line = self._line[:self._idx] + c + self._line[self._idx:]
                    self._idx += 1
                    self.redraw_line()
    
    def redraw_line(self):
        swrite("\033[256D")
#        swrite("\033[{}D".format(len(self.prompt) + self._idx))
        swrite("\033[2K")
        swrite(self.prompt)
        swrite(self._line)
        if len(self._line) - self._idx > 0:
            swrite("\033[{}D".format(len(self._line) - self._idx))

    def execute_command(self, command):
        print("Executing command: {}".format(command))

    def complete(self, line):
        return line, False

    def _enter(self):
        swrite("\n")
        if len(self._line) > 0:
            self.history.append(self._line)
            self.execute_command(self._line)

        self._line = ""
        swrite(self.prompt)
        self._idx = 0#len(self.prompt)
        self._history_idx = 0

    def _left(self):
        if self._idx > 0:
            swrite("\033[{}D".format(1))
            self._idx -= 1

    def _right(self):
        if self._idx < len(self._line):
            swrite("\033[{}C".format(1))
            self._idx += 1

    def _home(self):
        swrite("\033[{}D".format(self._idx))
        self._idx = 0

    def _end(self):
        swrite("\033[{}C".format(len(self._line)-self._idx))
        self._idx = len(self._line)

    def _backspace(self):
        if self._idx > 0:
            self._line = self._line[:self._idx-1] + self._line[self._idx:]
            self._idx -= 1
            self.redraw_line()

    def _delete(self):
        if self._idx < len(self._line):
            self._line = self._line[:self._idx] + self._line[self._idx+1:]
            self.redraw_line()

    def _tab(self):
        l, redraw = self.complete(self._line)
        if redraw:
            self._line = l
            self._idx = len(l)
            self.redraw_line()
        pass

    def _up(self):
        if len(self.history) > self._history_idx * -1:
            self._history_idx -= 1
            self._line = self.history[self._history_idx]
            self._idx = len(self._line)
            self.redraw_line()

    def _down(self):
        if self._history_idx * -1 > 0:
            self._history_idx += 1
            self._line = self.history[self._history_idx]
            self._idx = len(self._line)
            self.redraw_line()
        pass


#Cmd().cmdloop()

