'''
Created by Valentin Solina, Part of mipyshell project
Super simple, VT100 compatible, Command line interpreter helper class
'''

import sys

class Cmd:
    def __init__(self):
        self._line = ""
        self._idx = 0
        self.prompt = "cmd> "
        self.history = []
        self._history_idx = 0
        pass
    
    def cmdloop(self):
        sys.stdout.write(self.prompt)
        self._idx = 0#len(self.prompt)
        while True:
            c = sys.stdin.read(1)
            if c == '\x1b':
                c2 = sys.stdin.read(1)
                if c2 == '[':
                    c3 = sys.stdin.read(1)
                    if c3 == 'A':
                        self._up()
                    if c3 == 'B':
                        self._down()
                    if c3 == 'C':
                        self._right()
                    if c3 == 'D':
                        self._left()
                    if c3 == 'H':
                        self._home()
                    if c3 == 'F':
                        self._end()

                    if c3 == '3':
                        _ = sys.stdin.read(1)
                        self._delete()
                    if c3 == '5':
                        _ = sys.stdin.read(1)
                        self._pgup()
                    if c3 == '6':
                        _ = sys.stdin.read(1)
                        self._pgdown()
            elif c == '\x7f':
                self._backspace()
            elif c == '\t':
                self._tab()
            elif c == '\n':
                self._enter()
            
            else:
                if len(self._line) == self._idx:
                    self._line += c
                else:
                    self._line = self._line[:self._idx] + c + self._line[self._idx:]
                self._idx += 1
                self.redraw_line()
#                sys.stdout.write(c)
    
    def redraw_line(self):
        sys.stdout.write("\033[256D")
#        sys.stdout.write("\033[{}D".format(len(self.prompt) + self._idx))
        sys.stdout.write("\033[2K")
        sys.stdout.write(self.prompt)
        sys.stdout.write(self._line)
        if len(self._line) - self._idx > 0:
            sys.stdout.write("\033[{}D".format(len(self._line) - self._idx))

    def execute_command(self, command):
        print("Executing command: {}".format(command))

    def complete(self, line):
        return line, False

    def _enter(self):
        sys.stdout.write("\n")
        if len(self._line) > 0:
            self.history.append(self._line)
            self.execute_command(self._line)

        self._line = ""
        sys.stdout.write(self.prompt)
        self._idx = 0#len(self.prompt)
        self._history_idx = 0

    def _left(self):
        if self._idx > 0:
            sys.stdout.write("\033[{}D".format(1))
            self._idx -= 1

    def _right(self):
        if self._idx < len(self._line):
            sys.stdout.write("\033[{}C".format(1))
            self._idx += 1

    def _home(self):
        sys.stdout.write("\033[{}D".format(self._idx))
        self._idx = 0

    def _end(self):
        sys.stdout.write("\033[{}C".format(len(self._line)-self._idx))
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

