# -*-coding="UTF-8"-*-


from enum import Enum
from cm_token import TokenType


class MsgType(Enum):
    # 编译时候的错误
    COMPILE_ER_NEED_IDENTIFIER = 'need identifier:'
    COMPILE_ER_NEED_TYPE_SPECIFIER = 'need type specifier:'
    COMPILE_ER_NEED_CONST_INT = 'need const integer:'
    COMPILE_ER_NEED_FUNCTION_NAME = 'need function name:'
    COMPILE_ER_NEED_EXPRESSION = 'need expression:'
    COMPILE_ER_NEED_STATEMENT = 'need statement:'
    COMPILE_ER_NEED_ARRAY_SIZE = 'need array size:'
    COMPILE_ER_NEED_ARRAY_NAME = 'need array name:'
    COMPILE_ER_ASSIGN_TYPE_ERROR = 'can not assign exp:'
    COMPILE_ER_UNDEFINED_IDENTIFIER = 'undefined identifier:'
    COMPILE_ER_UNEXPECTED_TOKEN = 'unexpected token:'
    COMPILE_ER_EXPRESSION_NOT_ASSIGNABLE = 'expression in the left is not assignable:'
    COMPILE_ER_EXPECT_TOKEN = 'expect token:'
    COMPILE_ER_DUPLICATED_NAME = 'name already exists in the same scope:'
    COMPILE_ER_VOID_VARIABLE = 'void can not define the variable:'
    COMPILE_ER_VOID_ONLY_PARAMETER = '\'void\' must be the only parameter:'
    COMPILE_ER_VOID_ARGUMENTS = '\'void\' can not be the argument of function call:'
    COMPILE_ER_FUNCTION_CALL_TOO_MUCH_ARGUMENTS = 'too much arguments in function calling:'
    COMPILE_ER_FUNCTION_CALL_TOO_FEW_ARGUMENTS = 'too few arguments in function calling:'
    COMPILE_ER_FUNCTION_CALL_PARAMETER_FIT_ERROR = 'no fitted arguments in function calling:'
    COMPILE_ER_RETURN_TYPE = 'return error type:'

    #  运行环境时候的出错
    RUNTIME_ER_NO_ENTRY = 'no entry in the code: need main function'
    RUNTIME_ER_PUSH_VAR = 'the variable pushed is not local variable'
    RUNTIME_ER_ARRAY_OUT_OF_INDEX = 'array out of index'
    RUNTIME_ER_INPUT_ERROR_NO_INTEGER = 'input error: input must be integer'
    RUNTIME_ER_OUTPUT_ERROR_NO_OUTPUT = 'output error: no output'


def show_compile_warn(_line_num, _col_num, _msg_type: MsgType, _msg):
    print('warn: {}:({},{})'.format(_msg_type.value + _release_tuple(_msg), _line_num, _col_num))


def show_compile_error(_line_num, _col_num, _msg_type, *_msgs):
    _result = _msg_type.value
    # for msg in _msgs:
    #     if isinstance(msg, TokenType):
    #         _result += msg.name
    #     else:
    #         _result += msg
    _result += _release_tuple(_msgs)
    _result += '(' + str(_line_num) + ',' + str(_col_num) + ')'
    _result = "\033[39;31m%s\033[5m" % _result
    print(_result)
    exit(0)


#  运行环境报错
def run_time_error(_msg_type, *_msgs):
    _result = 'run time error: '
    _result += _msg_type.value
    _result += _release_tuple(_msgs)
    _result = "\033[39;31m%s\033[5m" % _result
    print(_result)
    exit(0)


# 因为传了三层的 *msg 所以大部分情况下 msg会被包装成3个。。。
def _release_tuple(_packets):
    _str = ''
    for elem in _packets:
        if isinstance(elem, tuple):
            _str += _release_tuple(elem)
        elif isinstance(elem, TokenType):
            _str += elem.name
        else:
            _str += elem
    return _str


class GenGraph(object):
    def __init__(self):
        try:
            self._file = open('resources/ast.puml', 'wb+')
            self._nodes = []
            self._relation = []
        except IOError:
            print('\'resources/ast.puml\' 打开失败!\n')
            exit(0)

    def __del__(self):
        self._file.close()

    # 写入到文件中去
    def write(self):
        self._head()
        self._content()
        self._tail()

    def add_node(self, _name, label):
        self._nodes.append((_name, label))

    def add_relation(self, _from, _to):
        self._relation.append((_from, _to))

    def _head(self):
        _head_str = '@startdot\ndigraph G {\n'
        self._file.write(bytes(_head_str, encoding='UTF-8'))

    def _tail(self):
        _tail_str = '\n}\n@enddot'
        self._file.write(bytes(_tail_str, encoding='UTF-8'))

    def _content(self):
        _content_str = ''
        for _node in self._nodes:
            _content_str += '{}[label="{}"]\n'.format(_node[0], _node[1])

        for _rel in self._relation:
            _content_str += '{}->{}\n'.format(_rel[0], _rel[1])
        self._file.write(bytes(_content_str, 'UTF-8'))
