# -*-coding="UTF-8"-*-


from enum import Enum


class MsgType(Enum):
    ER_NEED_IDENTIFIER = 0
    ER_UNEXPECTED_TOKEN = 1
    ER_EXPECT_TOKEN = 2

_er_str = {
    MsgType.ER_NEED_IDENTIFIER: 'need identifier:',
    MsgType.ER_UNEXPECTED_TOKEN: 'unexpected token:',
    MsgType.ER_EXPECT_TOKEN: 'expect token:'
}


def show_compile_warn(_line_num, _col_num, _msg_type, _msg):
    print('')


def show_compile_error(_line_num, _col_num, _msg_type, *_msgs):
    _result = _er_str[_msg_type]
    for msg in _msgs:
        _result += msg
    _result += '(' + str(_line_num) + ',' + str(_col_num) + ')'
    _result = "\033[39;31m%s\033[5m" % _result
    print(_result)
    exit(0)


