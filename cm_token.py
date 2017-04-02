# -*-coding="UTF-8"-*-


from enum import Enum


# token 类型枚举
class TokenType(Enum):
    TK_IDENTIFIER = 0  # "xyz"
    TK_INTEGER = 1  # "123"
    TK_PLUS = 2  # "+"
    TK_MINUS = 3  # "-"
    TK_STAR = 4  # "*"
    TK_DIV = 5   # "/"
    TK_LESS = 6  # "<"
    TK_NOT_LARGER = 7  # "<="
    TK_LARGER = 8  # ">"
    TK_NOT_LESS = 9  # ">="
    TK_EQUAL = 10   # "=="
    TK_NOT_EQUAL = 11  # "!="
    TK_ASSIGN = 12  # "="
    TK_SEMICOLON = 13  # ";"
    TK_COMMA = 14  # ","
    TK_LEFT_PARENT = 15  # "("
    TK_RIGHT_PARENT = 16  # ")"
    TK_LEFT_BRACKET = 17  # "["
    TK_RIGHT_BRACKET = 18  # "}"
    TK_LEFT_BRACE = 19  # "{"
    TK_RIGHT_BRACE = 20  # "}"

    KW_BEGIN = 21

    KW_ELSE = 22
    KW_IF = 23
    KW_INT = 24
    KW_RETURN = 25
    KW_VOID = 26
    KW_WHILE = 27

    KW_END = 28

    KW_INNER_FUNC_BEGIN = 29

    KW_INNER_FUNC_INPUT = 30
    KW_INNER_FUNC_OUTPUT = 31

    KW_INNER_FUNC_END = 32

    TK_EOF = 33

    TK_ANNOTATION = 34


# 保留字对应表
_keyword_table = {
    'else': TokenType.KW_ELSE,
    'if': TokenType.KW_IF,
    'int': TokenType.KW_INT,
    'return': TokenType.KW_RETURN,
    'void': TokenType.KW_VOID,
    'while': TokenType.KW_WHILE,
    'input': TokenType.KW_INNER_FUNC_INPUT,
    'output': TokenType.KW_INNER_FUNC_OUTPUT
}


# Token类
class Token(object):
    def __init__(self):
        self._token_type = None
        self._value = None
        self._source_str = ''

    def get_token_type(self):
        return self._token_type

    def set_token_type(self, _token_type):
        self._token_type = _token_type

    def get_value(self):
        return self._value

    def set_value(self, _value):
        self._value = _value

    def set_source_str(self, _str):
        self._source_str = _str

    def get_source_str(self):
        return self._source_str

    def append_ch(self, _ch):
        self._source_str += _ch

    def check_reserved(self):
            if _keyword_table.get(self._source_str):
                self._token_type = _keyword_table[self._source_str]
            else:
                self._token_type = TokenType.TK_IDENTIFIER

    def parse_int(self):
        self._token_type = TokenType.TK_INTEGER
        self._value = int(self._source_str)

