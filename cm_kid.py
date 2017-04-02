# -*-coding ="UTF-8"-*-

from codecs import decode
from enum import Enum


class FileUtil:

    def __init__(self):
        self._file = None

    def get_char_to(self):
        buffer = self._file.read()
        buffer = decode(buffer, 'UTF-8')
        print(buffer)

    def open_file(self, file_path):
        try:
            self._file = open(file_path, 'rb+')
        except IOError:
            print('文件打开失败!\n')
            exit(0)

    def close_file(self):
            self._file.close()

    def __del__(self):
        print("object destructor")
        self.close_file()


class A(object):
    def __init__(self):
        self._name = "123"
        self.gName = "312"
        self.__private_name = "private"

    def func(self):
        self.p1()

    def get_name(self):
        return self._name

    def set_name(self, _name):
        self.__private_name = _name

    def p1(self):
        print('base p1')


class B(A):
    def __init__(self):
        A.__init__(self)

    def p1(self):
        print('inherit p1')


class Color(Enum):
    red = 1
    blue = 2


def foo1(temp):
    temp.set_name('hello')


def foo2(array):
    array.append(100)


def test():
    file = FileUtil()
    file.open_file('resources/target.c')
    file.get_char_to()
    temp = file
    del file
    del temp
    a = A()
    b = B()
    a.func()
    b.func()
    foo1(b)
    print(b.get_name())
    array = [1, 2, 3]
    foo2(array)
    print(array[3])
    color = Color.red
    print(Color.red.value)
    if color == Color.red:
        print('red')
    elif color == Color.blue:
        print('blue')


def test_entry():
    #test()
    print('hello world')
