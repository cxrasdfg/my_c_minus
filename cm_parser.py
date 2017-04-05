# -*-coding="UTF-8" -*-


from cm_lexer import Lexer
from cm_token import TokenType
from cm_token import Token
from cm_util import MsgType
import cm_util
import ast


class Parser(object):
    def __init__(self, file_path):
        self._symbol_name = list()
        self._symbol_table = dict()
        self._scope_indices = list()
        self._current_token = Token()
        self._lexer = Lexer(file_path)
        self._current_func_params = list()  # 存储处于当前作用域的函数的参数
        self._current_func_return = ast.VarType.VT_DEFAULT  # 存储当前函数的返回值
        self._table_init()

    def write_graph(self):
        _gg = cm_util.GenGraph()
        for _key in self._symbol_name:
            self._symbol_table[_key].draw(_gg)
        _gg.write()

    # 主要用于插入系统函数 such as input and output
    def _table_init(self):
        _output = ast.ASTNode()
        _output.type = ast.ASTType.AST_INNER_DECLARATION
        _output.name = 'output'
        _output.func_return_type = ast.VarType.VT_VOID
        _output_param = ast.ASTNode()
        _output_param.type = ast.ASTType.AST_LOCAL_DECLARATION
        _output_param.name = 'N/A'
        _output_param.var_type = ast.VarType.VT_INT
        _output.func_parameters.append(_output_param)
        self._insert_table(_output.name, _output)

        _input = ast.ASTNode()
        _input.type = ast.ASTType.AST_INNER_DECLARATION
        _input.name = 'input'
        _input.func_return_type = ast.VarType.VT_INT
        self._insert_table(_input.name, _input)

    def parse(self):
        self._translate_unit()
        print('编译通过')

    # <translate_unit> -> {<outer_declaration>}
    def _translate_unit(self):
        while 1:
            if self._get_token().get_token_type() == TokenType.TK_EOF:  # 退出条件
                break
            else:
                self._putback_token()
            _out_dec = self._declaration()
            if _out_dec is not None:
                if _out_dec.type == ast.ASTType.AST_GLOBAL_DECLARATION:
                    self._insert_table(_out_dec.name, _out_dec)

    # <outer_declaration> -> <declaration>
    # <declaration> -> <type_name> <symbol> '(' [<param_list>] ')' <func_body>
    # <declaration> -> <type_name> <symbol> ';'
    # <declaration> -> <type_name> <symbol> '[' <KW_INT> ']' ';'
    def _declaration(self):
        _result = None

        _type_name = self._type_name()
        _symbol_token = self._symbol_token()
        _symbol_name = _symbol_token.get_source_str()

        if self._collision_test(_symbol_name):
            self.show_error(MsgType.ER_DUPLICATED_NAME, _symbol_name)

        _scope_len = len(self._scope_indices)
        _token = self._get_token()
        _token_type = _token.get_token_type()
        if _token_type == TokenType.TK_LEFT_PARENT:  # '(' it's the function 对函数的嵌套定义先不管。。 c99是支持函数潜逃定义的
            if _scope_len != 0:
                self.show_error(MsgType.ER_UNEXPECTED_TOKEN, _token.get_source_str())
            _params = self._param_list()
            self._current_func_params = _params
            self._skip(TokenType.TK_LEFT_BRACE)
            _result = ast.ASTNode()
            _result.type = ast.ASTType.AST_FUNC_DECLARATION
            _result.name = _symbol_name
            self._insert_table(_symbol_name, _result)  # 一定要在函数体之前调入符号表。。。不然递归的话，就找不到符号

            if _type_name == TokenType.KW_VOID:  # 没有返回值
                _return_type = ast.VarType.VT_VOID
            elif _type_name == TokenType.KW_INT:  # 返回值为int
                _return_type = ast.VarType.VT_INT
            self._current_func_return = _return_type
            _result.func_return_type = _return_type
            _result.func_parameters = _params
            _func_body = self._func_body()
            _result.func_body = _func_body
        elif _token_type == TokenType.TK_SEMICOLON:  # ';'  # 说明是变量定义
            if _type_name == TokenType.KW_VOID:
                self.show_error(MsgType.ER_VOID_VARIABLE, _symbol_name)
            _result = ast.ASTNode()
            if _scope_len > 0:  # 表明是全局变量
                _result.type = ast.ASTType.AST_LOCAL_DECLARATION
            else:  # 表明是局部变量
                _result.type = ast.ASTType.AST_GLOBAL_DECLARATION
            _result.name = _symbol_name
            _result.var_type = ast.VarType.VT_INT
        elif _token_type == TokenType.TK_LEFT_BRACKET:  # '['  表明是数组
            self._putback_token()  # 这里put back是为了适应函数 _array() ... , 因为它消耗了 '['
            _array_size = self._array()
            if _array_size is None or _array_size == -1:
                self.show_error(MsgType.ER_NEED_IDENTIFIER)
            self._skip(TokenType.TK_SEMICOLON)
            _result = ast.ASTNode()
            if _scope_len > 0:  # 表明是局部变量
                _result.type = ast.ASTType.AST_LOCAL_DECLARATION
            else:  # 表明是全局变量
                _result.type = ast.ASTType.AST_GLOBAL_DECLARATION
            _result.name = _symbol_name
            _result.var_type = ast.VarType.VT_ARRAY
            _result.var_array_size = _array_size
        else:
            self.show_error(MsgType.ER_UNEXPECTED_TOKEN, _token.get_source_str())
        return _result

    def _symbol_token(self):
        _token = self._get_token()
        if _token.get_token_type() != TokenType.TK_IDENTIFIER:
            self.show_error(MsgType.ER_NEED_IDENTIFIER)
        return _token

    # type name
    def _type_name(self):
        _token = self._get_token()
        _type = _token.get_token_type()
        if _type == TokenType.KW_INT:  # 'int'
            return TokenType.KW_INT
        elif _type == TokenType.KW_VOID:  # 'void'
            return TokenType.KW_VOID
        else:
            self.show_error(MsgType.ER_NEED_TYPE_SPECIFIER)

    # <param_list> -> <type_name> <symbol> {',' <type_name> <symbol>}
    def _param_list(self):
        _result = []
        self._current_func_params = _result
        _void_flag = False
        while 1:
            _token = self._get_token()
            _type = _token.get_token_type()
            if _type == TokenType.TK_RIGHT_PARENT:  # ')'
                break
            elif _type == TokenType.KW_VOID:  # 'void'
                if _void_flag:
                    self.show_error(MsgType.ER_VOID_ONLY_PARAMETER)
                else:
                    _void_flag = True
                if len(_result) != 0:  # 表明已经至少有一个参数了
                    self.show_error(MsgType.ER_VOID_ONLY_PARAMETER)
            elif _type == TokenType.KW_INT:  # 'int'
                _single_param = self._func_param_var()
                _result.append(_single_param)
            elif _type == TokenType.TK_COMMA:  # ','
                continue
            else:
                self._putback_token()
                self.show_error(MsgType.ER_UNEXPECTED_TOKEN, _token.get_source_str())
                break
        return _result

    # <func_param_var> -> <symbol> [ '[' ']' ] | <symbol> [ '['<TK_INT>']']
    def _func_param_var(self):
        _result = None
        _token = self._get_token()
        _type = _token.get_token_type()
        if _type == TokenType.TK_IDENTIFIER:
            _id_name = _token.get_source_str()
            _array_size = self._array()

            _param = ast.ASTNode()
            _param.type = ast.ASTType.AST_LOCAL_DECLARATION
            _param.name = _id_name
            if _array_size is not None:  # 是数组
                _param.var_type = ast.VarType.VT_ARRAY  # 类型是数组
                _param.var_array_size = _array_size
            else:  # 不是数组
                _param.var_type = ast.VarType.VT_INT  # 不是数组就是int了， 没有void类型的变量
            _result = _param

        else:  # 没有寻找到identifier
            self.show_error(MsgType.ER_NEED_IDENTIFIER)
        return _result

    def _array(self):
        _token = self._get_token()
        _type = _token.get_token_type()
        if _type == TokenType.TK_LEFT_BRACKET:
            _int = self._get_token()
            if _int.get_token_type() == TokenType.TK_INTEGER:
                return _int.get_value()
            else:
                self._skip(TokenType.TK_RIGHT_BRACKET)
                return -1  # -1 表示是 []
        else:
            self._putback_token()
            return None  # 空的表示没有数组的后缀

    # <func_body> -> <compound_statement>
    def _func_body(self):
        return self._compound_statement()

    # <statement> -> <if_statement> | <while_statement> | <compound_statement>
    # | <return_statement>| <break_statement> |<expression> ';'
    def _statement(self):
        _type = self._get_token().get_token_type()
        if _type == TokenType.KW_IF:
            _result = self._if_statement()
        elif _type == TokenType.KW_WHILE:
            _result = self._while_statement()
        elif _type == TokenType.KW_RETURN:
            _result = self._return_statement()
        elif _type == TokenType.TK_LEFT_BRACE:
            _result = self._compound_statement()
        else:
            self._putback_token()
            _result = self._expression()
            self._skip(TokenType.TK_SEMICOLON)
        return _result

    # <return_statement> -> <KW_RETURN> <expression> ';'
    # <return_statement> -> <KW_RETURN> ';'
    def _return_statement(self):
        _token = self._get_token()
        _type = _token.get_token_type()
        if _type == TokenType.TK_SEMICOLON:  # ';'
            _result = ast.ASTNode()
            _result.type = ast.ASTType.AST_RETURN_EXP
        else:  # 以为是表达式
            self._putback_token()
            _exp = self._expression()
            self._skip(TokenType.TK_SEMICOLON)
            _result = ast.ASTNode()
            _result.type = ast.ASTType.AST_RETURN_EXP
            _result.return_exp = _exp
        return _result

    # <break_statement> -> <KW_BREAk> ';'
    def _break_statement(self):
        self._skip(TokenType.TK_SEMICOLON)
        _result = ast.ASTNode()
        _result.type = ast.ASTType.AST_BREAK_EXP
        return _result

    # <if_statement> -> <KW_IF> '(' <expression> ')' <statement> [ <KW_ELSE> <statement> ]
    def _if_statement(self):
        self._skip(TokenType.TK_LEFT_PARENT)
        _judge_exp = self._expression()
        self._skip(TokenType.TK_RIGHT_PARENT)
        _if_body = self._statement()
        _else = None
        if self._get_token().get_token_type() == TokenType.KW_ELSE:
            _else = self._statement()
        else:
            self._putback_token()
        _result = ast.ASTNode()
        _result.type = ast.ASTType.AST_IF_STATEMENT
        _result.judge_exp = _judge_exp
        _result.if_body = _if_body
        _result.if_else = _else
        return _result

    # <while_statement> -> <KW_WHILE> -> '(' <expression> ')' <statement>
    def _while_statement(self):
        self._skip(TokenType.TK_LEFT_PARENT)
        _judge_exp = self._expression()
        self.show_error(TokenType.TK_RIGHT_PARENT)
        _while_body = self._statement()
        _result = ast.ASTNode()
        _result.type = ast.ASTType.AST_WHILE_STATEMENT
        _result.judge_exp = _judge_exp
        _result.while_body = _while_body
        return _result

    # <compound_statement> -> '{' {<declaration>} { <statement> } '}'
    def _compound_statement(self):
        _compound = ast.ASTNode()
        _compound.type = ast.ASTType.AST_COMPOUND_STATEMENT
        _local_dec = _compound.sub_local_dec
        _sub_statement = _compound.sub_statement
        self._enter_scope(_compound)

        while 1:
            _token = self._get_token()
            _type = _token.get_token_type()
            if _type == TokenType.TK_RIGHT_BRACE:
                break
            elif _type == TokenType.KW_INT:
                self._putback_token()
                _dec = self._declaration()
                if _dec:  # 如果存在局部声明
                    _local_dec[_dec.name] = _dec
            else:
                self._putback_token()
                _state = self._statement()
                if _state:  # 如果不是空语句
                    _sub_statement.append(_state)

        self._leave_scope()
        return _compound

    # <expression> -> <assign_exp> { ',' <assign_exp> }
    def _expression(self):
        _result = self._assign_exp()
        while 1:
            _token = self._get_token()
            _type = _token.get_token_type()
            if _type == TokenType.TK_COMMA:
                _exp = self._assign_exp()
                _temp = _result
                _result = ast.ASTNode()
                _result.type = ast.ASTType.AST_EXPRESSION
                _result.l_child = _temp
                _result.r_child = _exp
            else:
                self._putback_token()
                break

        return _result

    # <assign_exp> -> <suffix_exp> '=' <assign_exp> |  <equal_class_exp>
    # 非等价转换 <assign_exp> -> <equal_class_exp> [ '=' <assign_exp> ]
    def _assign_exp(self):
        _result = self._equal_class_exp()

        if self._get_token().get_token_type() == TokenType.TK_ASSIGN:
            _exp = self._assign_exp()
            _temp = _result
            _result = ast.ASTNode()
            _result.type = ast.ASTType.AST_ASSIGN_EXP
            _result.l_child = _temp
            _result.r_child = _exp
        else:
            self._putback_token()

        return _result

    # <equal_class_exp> -> <relation_exp> { "!=" <relation_exp>}
    # <equal_class_exp> -> <relation_exp> { "==" <relation_exp>}
    def _equal_class_exp(self):
        _result = self._relation_exp()

        while 1:
            _token = self._get_token()
            _type = _token.get_token_type()
            if _type == TokenType.TK_NOT_EQUAL:
                _exp = self._relation_exp()
                _temp = _result
                _result = ast.ASTNode()
                _result.type = ast.ASTType.AST_NOT_EQUAL_EXP
                _result.l_child = _temp
                _result.r_child = _exp
            elif _type == TokenType.TK_EQUAL:
                _exp = self._relation_exp()
                _temp = _result
                _result = ast.ASTNode()
                _result.type = ast.ASTType.AST_EQUAL_EXP
                _result.l_child = _temp
                _result.r_child = _exp
            else:
                self._putback_token()
                break
        return _result

    # <relation_exp> -> <add_class_exp> { '<' <add_class_exp> }
    # <relation_exp> -> <add_class_exp> { '<=' <add_class_exp> }
    # <relation_exp> -> <add_class_exp> { '>' <add_class_exp> }
    # <relation_exp> -> <add_class_exp> { '>=' <add_class_exp> }
    def _relation_exp(self):
        _result = self._add_exp()

        while 1:
            _token = self._get_token()
            _type = _token.get_token_type()
            if _type == TokenType.TK_LESS:
                _exp = self._add_exp()
                _temp = _result
                _result = ast.ASTNode()
                _result.type = ast.ASTType.AST_LESS_EXP
                _result.l_child = _temp
                _result.r_child = _exp
            elif _type == TokenType.TK_NOT_LARGER:
                _exp = self._add_exp()
                _temp = _result
                _result = ast.ASTNode()
                _result.type = ast.ASTType.AST_NOT_LARGER_EXP
                _result.l_child = _temp
                _result.r_child = _exp
            elif _type == TokenType.TK_LARGER:
                _exp = self._add_exp()
                _temp = _result
                _result = ast.ASTNode()
                _result.type = ast.ASTType.AST_LARGER_EXP
                _result.l_child = _temp
                _result.r_child = _exp
            elif _type == TokenType.TK_NOT_LESS:
                _exp = self._add_exp()
                _temp = _result
                _result = ast.ASTNode()
                _result.type = ast.ASTType.AST_NOT_LESS_EXP
                _result.l_child = _temp
                _result.r_child = _exp
            else:
                self._putback_token()
                break
        return _result

    # <add_class_exp> -> <mul_class_exp> { '+' <mul_class_exp> }
    # <add_class_exp> -> <mul_class_exp> { '-' <mul_class_exp> }
    def _add_exp(self):
        _mul_exp = self._mul_exp()
        _result = _mul_exp
        while 1:
            _token = self._get_token()
            _type = _token.get_token_type()
            if _type == TokenType.TK_PLUS:
                _next_node = self._mul_exp()
                _temp = _result
                _result = ast.ASTNode()
                _result.type = ast.ASTType.AST_ADD_EXP
                _result.r_child = _temp
                _result.l_child = _next_node
            elif _type == TokenType.TK_MINUS:
                _next_node = self._mul_exp()
                _temp = _result
                _result = ast.ASTNode()
                _result.type = ast.ASTType.AST_MINUS_EXP
                _result.r_child = _temp
                _result.l_child = _next_node
            else:
                self._putback_token()
                break

        return _result

    # <mul_class_exp> -> <suffix_exp> { '*' <suffix_exp> }
    # <mul_class_exp> -> <suffix_exp> { '/' <suffix_exp> }
    def _mul_exp(self):
        _suffix_exp = self._suffix_exp()
        _result = _suffix_exp
        while 1:

            _token = self._get_token()
            _type = _token.get_token_type()
            if _type == TokenType.TK_STAR:
                _next_node = self._suffix_exp()
                _temp = _result
                _result = ast.ASTNode()
                _result.type = ast.ASTType.AST_MUL_EXP
                _result.l_child = _temp
                _result.r_child = _next_node
            elif _type == TokenType.TK_DIV:
                _next_node = self._suffix_exp()
                _temp = _result
                _result = ast.ASTNode()
                _result.type = ast.ASTType.AST_DIV_EXP
                _result.l_child = _temp
                _result.r_child = _next_node
            else:
                self._putback_token()
                break

        return _result

    # <suffix_exp> -> <primary_exp>  '[' <expression> ']'
    # <suffix_exp> -> <primary_exp>
    # <suffix_exp> -> <primary_exp> '(' ')'
    # <suffix_exp> -> <primary_exp> '(' <arguments>  ')'
    def _suffix_exp(self):
        _primary_exp = self._primary_exp()
        _suffix = _primary_exp
        _token = self._get_token()
        _token_type = _token.get_token_type()
        if _token_type == TokenType.TK_LEFT_BRACKET:  # [
            _int_exp = self._expression()
            self._skip(TokenType.TK_RIGHT_BRACKET)
            _array_index = ast.ASTNode()
            _array_index.type = ast.ASTType.AST_ARRAY_INDEX
            _array_index.l_child = _primary_exp
            _array_index.r_child = _int_exp
            _suffix = _array_index
        elif _token_type == TokenType.TK_LEFT_PARENT:  # '(' 证明属于函数的调用。。。
            _args = self._arguments()
            self._skip(TokenType.TK_RIGHT_PARENT)
            _func_call = ast.ASTNode()
            _func_call.type = ast.ASTType.AST_FUNC_CALL
            _func_call.r_child = _args
            _func_call.l_child = _primary_exp
            _suffix = _func_call
        else:
            self._putback_token()
        return _suffix

    # <arguments> -> <expression> {',' <expression>}
    def _arguments(self):
        _args = list()

        if self._get_token().get_token_type() == TokenType.TK_RIGHT_PARENT:
            self._putback_token()
            return _args
        else:
            self._putback_token()
        while 1:
            _exp = self._expression()
            if _exp:
                _args.append(_exp)

            _token = self._get_token()
            if _token.get_token_type() == TokenType.TK_COMMA:
                continue
            elif _token.get_token_type() == TokenType.TK_RIGHT_PARENT:
                self._putback_token()
                break
        return _args

    # <primary_exp> -> <symbol> | <KW_INT> | '(' <expression> ')'
    def _primary_exp(self):
        _token = self._get_token()
        _type = _token.get_token_type()
        _token_str = _token.get_source_str()
        if _type == TokenType.TK_IDENTIFIER:  # 如果是符号
            _symbol = self._find_symbol(_token_str)
            if _symbol:  # 找到了指代的符号
                _s_exp = ast.ASTNode()
                _s_exp.type = ast.ASTType.AST_SYMBOL_EXP
                _s_exp.var = _symbol
                _s_exp.name = _token_str
                return _s_exp
            else:  # 没找到
                self.show_error(MsgType.ER_UNDEFINED_IDENTIFIER, _token_str, ' ')
        elif _type == TokenType.TK_INTEGER:  # 如果是个整数常量
            _int_exp = ast.ASTNode()
            _int_exp.type = ast.ASTType.AST_CONST_INT
            _int_exp.int_value = _token.get_value()
            return _int_exp
        elif _type == TokenType.TK_LEFT_PARENT:
            _exp = self._expression()
            self._skip(TokenType.TK_RIGHT_PARENT)
            return _exp
        else:  # 没有任何匹配
            self._putback_token()
            return None

    def _enter_scope(self, _compound_statement):
        self._scope_indices.append(_compound_statement)

    def _leave_scope(self):
        self._scope_indices.remove(self._scope_indices[len(self._scope_indices)-1])
        if len(self._scope_indices) == 0:  # in global scope
            self._current_func_params = []
            self._current_func_return = None

    # 命名冲突检测 冲突返回true 不冲突返回false
    def _collision_test(self, _name):
        _sLen = len(self._scope_indices)
        if _sLen > 0:  # 在函数体中
            _curr_scope = self._scope_indices[_sLen-1]
            _temp = _curr_scope.sub_local_dec.get(_name)
            if _temp:  # 如果在当前复合语句的局部变量中
                return True  # 表示冲突
            if _sLen == 1:  # 表示在当前函数体中
                if self._look_up_list(self._current_func_params, _name):  # 表示冲突变量在函数的参数中
                    return True  # 冲突
        else:  # 表示在全局中
            if self._look_up_table(_name):
                return True  # 表示冲突
        return False

    # 查找list
    @staticmethod
    def _look_up_list(_list, _name):
        for item in _list:
            if item.name == _name:
                return item
        return None

    # 通过名字查找本地符号或全局符号
    def _find_symbol(self, _name):
        for s in self._scope_indices:  # 先查询本地变量
            _temp = s.sub_local_dec.get(_name)
            if _temp:
                return _temp

        _temp = Parser._look_up_list(self._current_func_params, _name)  # 查询是不是在函数的参数当中
        if _temp:
            return _temp

        _temp = self._look_up_table(_name)  # 查询是不是在符号表中（全局变量）
        if _temp:
            return _temp

        return None

    # 插入符号表，会查重并覆盖已有的值, 会返回插入的值
    def _insert_table(self, _name, _symbol):
        if not self._look_up_table(_name):
            self._direct_insert_table(_name, _symbol)
        return self._look_up_table(_name)

    # 直接插入
    def _direct_insert_table(self, _name, _symbol):
        self._symbol_table[_name] = _symbol
        self._symbol_name.append(_name)

    # 查询并通过返回值结果
    def _look_up_table(self, _name):
        if self._symbol_table.get(_name):
            return self._symbol_table[_name]
        else:
            return None

    def _get_token(self):
        self._current_token = self._lexer.get_next_token()
        return self._current_token

    def _putback_token(self):
        self._lexer.put_back_token(self._current_token)

    def _skip(self, _token_type):
        self._lexer.skip(_token_type)

    def show_error(self, msg_type, *msg):
        self._lexer.show_error(msg_type, msg)
