# -*-coding="UTF-8"-*-


from codecs import decode
from enum import Enum
import cm_token
import cm_util


# Lexer status
class LexStatus(Enum):
    LS_INIT = 0
    LS_EOF = 1
    LS_RECEIVE = 2
    LS_IN_INT = 3
    LS_IN_IDENTIFIER = 4
    LS_IN_ANNOTATION = 5


class Annotation(Enum):
    AN_2 = 0  # annotation 1
    AN_3 = 1  # annotation 2


class Lexer(object):

    def __init__(self, file_path):
        try:
            self._file = open(file_path, 'rb+')
        except IOError:
            print('文件打开失败!')
            exit(0)
        else:
            self._file_buffer = decode(self._file.read(), "UTF-8")
            self._file.close()
            self._max_file_size = len(self._file_buffer)
            self._current_fp = 0
            self._token_buffer = []
            self._current_token = None
            self._line_num = 1
            self._col_num = 1
            self._last_col = 1
            self._current_ch = '\0'
            self._lexer_status = LexStatus.LS_INIT

    def show_error(self, msg_type, *msg):
        cm_util.show_compile_error(self._line_num, self._col_num, msg_type, msg)

    def skip(self, _token_type):
        _token = self.get_next_token()
        if _token.get_token_type() != _token_type:
            self.show_error(cm_util.MsgType.COMPILE_ER_EXPECT_TOKEN, _token_type.name)

    # 返回一个token
    def put_back_token(self, _token):
        self._token_buffer.insert(0, _token)

    # 获取下一个token
    def get_next_token(self):
        if len(self._token_buffer) > 0:
            self._current_token = self._token_buffer[0]
            self._token_buffer.remove(self._current_token)
            return self._current_token
        else:
            return self._get_token_from_file()

    def _get_token_from_file(self):
        self._lexer_status = LexStatus.LS_INIT
        _token = cm_token.Token()
        while self._lexer_status != LexStatus.LS_EOF and self._lexer_status != LexStatus.LS_RECEIVE:
            if self._lexer_status == LexStatus.LS_INIT:
                _ch = self._get_ch()
                if _ch == -1:
                    self._lexer_status = LexStatus.LS_EOF
                    _token.set_token_type(cm_token.TokenType.TK_EOF)
                elif str.isdigit(_ch):
                    self._lexer_status = LexStatus.LS_IN_INT
                    _token.append_ch(_ch)
                elif str.isalpha(_ch):
                    self._lexer_status = LexStatus.LS_IN_IDENTIFIER
                    _token.append_ch(_ch)
                elif _ch == '\n':
                    self._new_line()
                elif _ch == '\t' or _ch == '\r' or _ch == ' ':
                    self._col_num += 0
                elif _ch == '+':
                    _token.append_ch(_ch)
                    _token.set_token_type(cm_token.TokenType.TK_PLUS)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == '-':
                    _token.append_ch(_ch)
                    _token.set_token_type(cm_token.TokenType.TK_MINUS)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == '*':
                    _token.append_ch(_ch)
                    _token.set_token_type(cm_token.TokenType.TK_STAR)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == '/':
                    _temp_ch = self._get_ch()
                    if _temp_ch == '*':
                        self._lexer_status = LexStatus.LS_IN_ANNOTATION
                    else:
                        self._put_back_ch()
                        _token.append_ch(_ch)
                        _token.set_token_type(cm_token.TokenType.TK_DIV)
                        self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == '<':
                    _temp_ch = self._get_ch()
                    if _temp_ch == '=':
                        _token.append_ch('<=')
                        _token.set_token_type(cm_token.TokenType.TK_NOT_LARGER)
                        self._lexer_status = LexStatus.LS_RECEIVE
                    else:
                        self._put_back_ch()
                        _token.append_ch(_ch)
                        _token.set_token_type(cm_token.TokenType.TK_LESS)
                        self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == '>':
                    _temp_ch = self._get_ch()
                    if _temp_ch == '=':
                        _token.append_ch('>=')
                        _token.set_token_type(cm_token.TokenType.TK_NOT_LESS)
                    else:
                        self._put_back_ch()
                        _token.append_ch(_ch)
                        _token.set_token_type(cm_token.TokenType.TK_LARGER)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == '=':
                    _temp_ch = self._get_ch()
                    if _temp_ch == '=':
                        _token.append_ch('==')
                        _token.set_token_type(cm_token.TokenType.TK_EQUAL)
                    else:
                        self._put_back_ch()
                        _token.append_ch('=')
                        _token.set_token_type(cm_token.TokenType.TK_ASSIGN)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == '!':
                    _temp_ch = self._get_ch()
                    if _temp_ch == '=':
                        _token.append_ch('!=')
                        _token.set_token_type(cm_token.TokenType.TK_NOT_EQUAL)
                        self._lexer_status = LexStatus.LS_RECEIVE
                    else:
                        self.show_error(cm_util.MsgType.COMPILE_ER_EXPECT_TOKEN, '\'', '=', '\'')
                elif _ch == ';':
                    _token.append_ch(_ch)
                    _token.set_token_type(cm_token.TokenType.TK_SEMICOLON)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == ',':
                    _token.append_ch(_ch)
                    _token.set_token_type(cm_token.TokenType.TK_COMMA)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == '(':
                    _token.append_ch(_ch)
                    _token.set_token_type(cm_token.TokenType.TK_LEFT_PARENT)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == ')':
                    _token.append_ch(_ch)
                    _token.set_token_type(cm_token.TokenType.TK_RIGHT_PARENT)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == '[':
                    _token.append_ch(_ch)
                    _token.set_token_type(cm_token.TokenType.TK_LEFT_BRACKET)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == ']':
                    _token.append_ch(_ch)
                    _token.set_token_type(cm_token.TokenType.TK_RIGHT_BRACKET)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == '{':
                    _token.append_ch(_ch)
                    _token.set_token_type(cm_token.TokenType.TK_LEFT_BRACE)
                    self._lexer_status = LexStatus.LS_RECEIVE
                elif _ch == '}':
                    _token.append_ch(_ch)
                    _token.set_token_type(cm_token.TokenType.TK_RIGHT_BRACE)
                    self._lexer_status = LexStatus.LS_RECEIVE
                else:
                    self.show_error(cm_util.MsgType.COMPILE_ER_EXPECT_TOKEN, '\'', _ch, '\'')
            elif self._lexer_status == LexStatus.LS_IN_INT:
                _ch = self._get_ch()
                if str.isdigit(_ch):
                    _token.append_ch(_ch)
                else:
                    self._put_back_ch()
                    _token.parse_int()
                    self._lexer_status = LexStatus.LS_RECEIVE

            elif self._lexer_status == LexStatus.LS_IN_IDENTIFIER:
                _ch = self._get_ch()
                if str.isalpha(_ch):
                    _token.append_ch(_ch)
                else:
                    self._put_back_ch()
                    _token.check_reserved()
                    self._lexer_status = LexStatus.LS_RECEIVE
            elif self._lexer_status == LexStatus.LS_IN_ANNOTATION:
                self._skip_annotation()
                self._lexer_status = LexStatus.LS_INIT
        self._current_token = _token
        return _token

    # skip annotation
    def _skip_annotation(self):

        _as = Annotation.AN_2

        while 1:
            _ch = self._get_ch()
            if _ch == '\t' or _ch == ' ':
                self._col_num += 1
            elif _ch == '\n':
                self._new_line()
            elif _ch == '\r':
                self._col_num = 1

            if _as == Annotation.AN_2:
                if _ch == '*':
                    _as = Annotation.AN_3
                elif _ch == -1:
                    self.show_error(cm_util.MsgType.COMPILE_ER_EXPECT_TOKEN, '\'', '*', '\'')
            elif _as == Annotation.AN_3:
                if _ch == '/':
                    break
                elif _ch == -1:
                    self.show_error(cm_util.MsgType.COMPILE_ER_EXPECT_TOKEN, '\'', '/', '\'')

    # 从缓冲区中获取一个字符
    def _get_ch(self):
        if self._current_fp >= self._max_file_size:
            return -1

        _ch = self._file_buffer[self._current_fp]
        self._current_fp += 1
        self._current_ch = _ch
        self._last_col = self._col_num
        self._col_num += 1
        return _ch

    # 回退一个字符到缓冲区
    def _put_back_ch(self):
        if self._current_fp > 0:
            self._current_fp -= 1

        self._col_num -= 1
        if self._col_num < 1:
            self._col_num = self._last_col
            self._line_num -= 1

    # 开始新的一行
    def _new_line(self):
        self._last_col = self._col_num
        self._col_num = 1
        self._line_num += 1

    @staticmethod
    def test(file_path):
        _lexer = Lexer(file_path)
        _count = 0
        while 1:
            _count += 1
            if _count != 0 and _count % 10 == 0:
                print('')
            _token = _lexer.get_next_token()
            _type = _token.get_token_type()
            if _token.get_token_type() == cm_token.TokenType.TK_EOF:
                break
            print(_token.get_source_str(), _type.name, sep=':', end='　')
