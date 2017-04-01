# -*-coding ="UTF-8"-*-


class FileUtil:

    def __init__(self):
        self

    def _open_file(self, file_path):
        self._file = open(file_path, 'rb+')

    def _close_file(self):
            self._file.close()


class A(object):
    def __init__(self):
        self._name = "123"
        self.gName = "312"
        self.__private_name = "private"

    def get_name(self):
        return self._name

    def set_name(self, _name):
        self.__private_name = _name


def test():
    print('test')
    a = A()
    print(a.get_name())
    a.set_name("123")
    print(a.gName)

    my_array = dict()
    my_array['123'] = '321'
    print(my_array['123'])


def test_entry():
    test()
