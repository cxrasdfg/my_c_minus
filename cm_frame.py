# -*-coding='UTF-8' -*-
# Created by theppsh on 17-4-9.


from cm_ast import ASTNode
from cm_ast import ASTType
from cm_ast import VarType
from cm_util import MsgType
from cm_util import run_time_error


class Frame(object):
    def __init__(self):
        self.protected_variable = []  # 保存上次的变量， 用于恢复环境, 每个元素是类似(_var,value)的东西
        self.return_type = VarType.VT_DEFAULT  # 保存函数的返回值类型 在这里只有整形和void
        self.return_value = 0  # 保存函数的返回值（只有整数）， 如果有的话
        self.func = ASTNode()  # 指向当前帧对应函数
        self.func_body = ASTNode()  # 指向当前的函数体
        self.func_parameters = []  # 指向当前的函数参数
        self.input_arguments = []  # 对应函数传入的参数
        self.return_flag = False  # 用于标识退出的信息。。。

    @staticmethod
    def create_frame(_new_func: ASTNode, _input_arguments: list):
        _frame = Frame()
        _frame.func = _new_func
        _frame.return_type = _new_func.func_return_type
        _frame.func_body = _new_func.func_body
        _frame.func_parameters = _new_func.func_parameters
        _frame.input_arguments = _input_arguments
        return _frame

    def run_frame(self):
        for _param in self.func_parameters:  # 将所有的参数入栈
            self._push_protected_var(_param)
            self._assign_arguments()  # 对形参赋值
        self._run_compound_statement(self.func_body)

        self._pop_all_protected_var()  # 恢复运行的现场

    #  运行符合语句
    def _run_compound_statement(self, _compound_statement):
        if self.return_flag:  # 如果已经确定退出了
            return

        for _local_dec in _compound_statement.sub_local_dec:  # 保护局部变量
            self._push_protected_var(_compound_statement.sub_local_dec[_local_dec])
            self._init_array_var(_compound_statement.sub_local_dec[_local_dec])  # 对数组进行初始化

        for _sub_statement in _compound_statement.sub_statement:
            if self.return_flag:  # 如果已经确定退出了
                return
            self._run_statement(_sub_statement)

    #  运行语句
    def _run_statement(self, _statement: ASTNode):
        if self.return_flag:  # 如果已经确定退出了
            return

        _type = _statement.type
        if _type == ASTType.AST_COMPOUND_STATEMENT:
            self._run_compound_statement(_statement)
        elif _type == ASTType.AST_EXPRESSION or \
            _type == ASTType.AST_ASSIGN_EXP or \
            _type == ASTType.AST_EQUAL_EXP or \
            _type == ASTType.AST_NOT_EQUAL_EXP or \
            _type == ASTType.AST_LESS_EXP or \
            _type == ASTType.AST_NOT_LARGER_EXP or \
            _type == ASTType.AST_LARGER_EXP or \
            _type == ASTType.AST_NOT_LESS_EXP or \
            _type == ASTType.AST_ADD_EXP or \
            _type == ASTType.AST_MINUS_EXP or \
            _type == ASTType.AST_MUL_EXP or \
            _type == ASTType.AST_DIV_EXP or \
            _type == ASTType.AST_ARRAY_INDEX or \
            _type == ASTType.AST_CONST_INT or \
            _type == ASTType.AST_SYMBOL_EXP or \
                _type == ASTType.AST_FUNC_CALL:
            self._run_expression(_statement)
        elif _type == ASTType.AST_IF_STATEMENT:
            _judge = _statement.judge_exp
            _if_body = _statement.if_body
            _else_body = _statement.if_else
            if self._run_expression(_judge)[1] != 0:
                self._run_statement(_if_body)
            else:
                if _else_body is not None:
                    self._run_statement(_else_body)
        elif _type == ASTType.AST_WHILE_STATEMENT:
            _judge = _statement.judge_exp
            _while_body = _statement.while_body
            while self._run_expression(_judge)[1] != 0:
                if self.return_flag:  # 如果已经确定退出了
                    return
                self._run_statement(_while_body)

        elif _type == ASTType.AST_RETURN_EXP:
            _return_exp = _statement.return_exp
            if self.return_type != VarType.VT_VOID:  # 表示有返回值
                self.return_value = self._run_expression(_return_exp)[1]
            self.return_flag = True

    def _run_expression(self, _exp: ASTNode):
        if self.return_flag:  # 如果已经确定退出了
            return
        _type = _exp.type
        _l_child = _exp.l_child
        _r_child = _exp.r_child
        if _type == ASTType.AST_EXPRESSION:
            self._run_expression(_r_child)
            _l_value = self._run_expression(_l_child)
            return _l_value
        elif _type == ASTType.AST_ASSIGN_EXP:  # assign exp只能是整形的， 由语义分析保证
            _l_type = _l_child.type
            _r_value = self._run_expression(_r_child)
            if _l_type == ASTType.AST_SYMBOL_EXP:  # symbol_exp 只能是整形的，由语义分析保证
                _l_child.var.var_int_value = _r_value[1]  # 返回的是个动态的tuple
            elif _l_type == ASTType.AST_ARRAY_INDEX:
                _index_value = self._run_expression(_l_child.r_child)[1]  # 计算索引的值
                _array_var = _l_child.l_child.var
                self._check_array_index(_array_var, _index_value)  # 数组越界检查

                _offset = _array_var.var_array_offset
                _pointer = _array_var.var_array_pointer
                _pointer[_index_value + _offset] = _r_value[1]

            return _r_value
        elif _type == ASTType.AST_EQUAL_EXP:
            _l_int_value = self._run_expression(_l_child)[1]
            _r_int_value = self._run_expression(_r_child)[1]

            if _l_int_value == _r_int_value:
                return VarType.VT_INT, 1
            else:
                return VarType.VT_INT, 0
        elif _type == ASTType.AST_NOT_EQUAL_EXP:
            _l_int_value = self._run_expression(_l_child)[1]
            _r_int_value = self._run_expression(_r_child)[1]

            if _l_int_value != _r_int_value:
                return VarType.VT_INT, 1
            else:
                return VarType.VT_INT, 0
        elif _type == ASTType.AST_LESS_EXP:
            _l_int_value = self._run_expression(_l_child)[1]
            _r_int_value = self._run_expression(_r_child)[1]

            if _l_int_value < _r_int_value:
                return VarType.VT_INT, 1
            else:
                return VarType.VT_INT, 0
        elif _type == ASTType.AST_NOT_LARGER_EXP:
            _l_int_value = self._run_expression(_l_child)[1]
            _r_int_value = self._run_expression(_r_child)[1]

            if _l_int_value <= _r_int_value:
                return VarType.VT_INT, 1
            else:
                return VarType.VT_INT, 0
        elif _type == ASTType.AST_LARGER_EXP:
            _l_int_value = self._run_expression(_l_child)[1]
            _r_int_value = self._run_expression(_r_child)[1]

            if _l_int_value > _r_int_value:
                return VarType.VT_INT, 1
            else:
                return VarType.VT_INT, 0
        elif _type == ASTType.AST_NOT_LESS_EXP:
            _l_int_value = self._run_expression(_l_child)[1]
            _r_int_value = self._run_expression(_r_child)[1]

            if _l_int_value >= _r_int_value:
                return VarType.VT_INT, 1
            else:
                return VarType.VT_INT, 0
        elif _type == ASTType.AST_ADD_EXP:
            _l_value = self._run_expression(_l_child)
            _r_value = self._run_expression(_r_child)
            _l_type = _l_value[0]
            _r_type = _r_value[0]
            if _l_type == VarType.VT_ARRAY:
                if _r_type == VarType.VT_INT:  # 肯定必须是int 不然语义分析就会报错
                    _size = _l_value[1]
                    _offset = _l_value[2]
                    _pointer = _l_value[3]
                    return VarType.VT_ARRAY, _size, _offset + _r_value[1], _pointer
            elif _l_type == VarType.VT_INT:
                if _l_type == VarType.VT_ARRAY:
                    _size = _r_value[1]
                    _offset = _r_value[2]
                    _pointer = _r_value[3]
                    return VarType.VT_ARRAY, _size, _offset + _l_value[1], _pointer
                elif _l_type == VarType.VT_INT:
                    return VarType.VT_INT, _l_value[1] + _r_value[1]
        elif _type == ASTType.AST_MINUS_EXP:
            _l_value = self._run_expression(_l_child)
            _r_value = self._run_expression(_r_child)
            _l_type = _l_value[0]
            _r_type = _r_value[0]
            if _l_type == VarType.VT_ARRAY:
                if _r_type == VarType.VT_INT:  # 肯定必须是int 不然语义分析就会报错
                    _size = _l_value[1]
                    _offset = _l_value[2]
                    _pointer = _l_value[3]
                    return VarType.VT_ARRAY, _size, _offset - _r_value[1], _pointer
            elif _l_type == VarType.VT_INT:  # 左边是int 对于减法 右边一定是int 否则语法分析的时候一定会报错
                    return VarType.VT_INT, _l_value[1] - _r_value[1]
        elif _type == ASTType.AST_MUL_EXP:  # 乘法只能是int相乘
            _l_value = self._run_expression(_l_child)
            _r_value = self._run_expression(_r_child)

            _l_int_value = _l_value[1]
            _r_int_value = _r_value[1]

            return VarType.VT_INT, _l_int_value * _r_int_value
        elif _type == ASTType.AST_DIV_EXP:
            _l_value = self._run_expression(_l_child)
            _r_value = self._run_expression(_r_child)

            _l_int_value = _l_value[1]
            _r_int_value = _r_value[1]

            if _r_int_value == 0.0 or _r_int_value == 0:
                run_time_error(MsgType.RUNTIME_ER_DIVIDE_ZERO)
            return VarType.VT_INT, int(_l_int_value / _r_int_value)
        elif _type == ASTType.AST_ARRAY_INDEX:
            _array_size = _l_child.var.var_array_size
            _array_offset = _l_child.var.var_array_offset
            _array_pointer = _l_child.var.var_array_pointer

            _array_index = self._run_expression(_r_child)[1]
            self._check_array_index_3(_array_size, _array_offset, _array_index)

            return VarType.VT_INT, _array_pointer[_array_index + _array_offset]
        elif _type == ASTType.AST_CONST_INT:
            return VarType.VT_INT, _exp.int_value
        elif _type == ASTType.AST_SYMBOL_EXP:
            _var = _exp.var
            if _var.var_type == VarType.VT_INT:
                return VarType.VT_INT, _var.var_int_value
            elif _var.var_type == VarType.VT_ARRAY:
                return VarType.VT_ARRAY, _var.var_array_size, _var.var_array_offset, _var.var_array_pointer
        elif _type == ASTType.AST_FUNC_CALL:
            _arguments = list()
            _args = self._expression_to_list(_r_child)
            for _arg in _args:
                _arguments.append(self._run_expression(_arg))
            _func = _l_child.var
            if _func.name == 'input':  # 内置函数
                _int_input = self._inner_func_input()
                return VarType.VT_INT, _int_input
            elif _func.name == 'output':  # 内置函数
                self._inner_func_output(_arguments)
                return  # 直接返回，不可能有哪个表达式需要output的返回值，这样语义分析阶段是会报错的。。。
            _sub_frame = Frame.create_frame(_func, _arguments)
            _sub_frame.run_frame()
            return _sub_frame.return_type, _sub_frame.return_value

        return None

    # 获取expression中的逗号表达式为一个链表
    @staticmethod
    def _expression_to_list(_args_list: list):
        if len(_args_list) == 0:
            return []
        _result = list()
        _temp = _args_list[0]
        while _temp is not None and _temp.type == ASTType.AST_EXPRESSION:
            _result.insert(0, _temp.r_child)
            _temp = _temp.l_child
        _result.insert(0, _temp)
        return _result

    # 表示内置的输出函数
    @staticmethod
    def _inner_func_output(_arguments):
        try:
            print(_arguments[0][1], end='\n')
        except IndexError:
            run_time_error(MsgType.RUNTIME_ER_OUTPUT_ERROR_NO_OUTPUT)

    # 表示内置的输入函数。。。
    @staticmethod
    def _inner_func_input():
        _int_input = input()
        if str.isdigit(_int_input):
            return int(_int_input)
        else:
            run_time_error(MsgType.RUNTIME_ER_INPUT_ERROR_NO_INTEGER)

    # 检查数组是否越界
    @staticmethod
    def _check_array_index_3(_size, _offset, _array_index):
        if _array_index + _offset >= _size or _array_index + _offset < 0:
            run_time_error(MsgType.RUNTIME_ER_ARRAY_OUT_OF_INDEX)

    #  检查数组是否越界
    @staticmethod
    def _check_array_index(_array: ASTNode, _index):
        _size = _array.var_array_size
        _offset = _array.var_array_offset
        Frame._check_array_index_3(_size, _offset, _index)

    # 初始化数组变量
    @staticmethod
    def _init_array_var(_var: ASTNode):
        if _var.var_type == VarType.VT_ARRAY:
            _var.var_array_pointer = []
            for i in range(0, _var.var_array_size):
                _var.var_array_pointer.append(0)

    # 对形参赋值
    def _assign_arguments(self):
        _arguments = self.input_arguments
        _func_parameters = self.func_parameters
        for i in range(0, len(_arguments)):
            _arg = _arguments[i]  # _arg 是形式为(type,value)的tuple
            _func_single_param = _func_parameters[i]
            if _arg[0] == VarType.VT_INT:
                _func_single_param.var_int_value = _arg[1]
            elif _arg[0] == VarType.VT_ARRAY:
                _func_single_param.var_array_size = _arg[1]
                _func_single_param.var_array_offset = _arg[2]
                _func_single_param.var_array_pointer = _arg[3]

    # 将局部变量入栈
    def _push_protected_var(self, _var: ASTNode):
        if _var.type == ASTType.AST_LOCAL_DECLARATION:
            if _var.var_type == VarType.VT_INT:  # 整形的变量直接保存它的整形的值
                self.protected_variable.append((_var, _var.var_int_value))
            elif _var.var_type == VarType.VT_ARRAY:  # 数组需要保存的就比较多
                self.protected_variable.append((_var, _var.var_array_size, _var.var_array_offset,
                                                _var.var_array_pointer))
        else:
            run_time_error(MsgType.RUNTIME_ER_PUSH_VAR)

    # 将被保护的变量还原 注意：frame结束销毁后才能还原,
    def _pop_all_protected_var(self):
        # 遍历每一个变量，还原之前的值
        for _var_tuple in self.protected_variable:
            _var = _var_tuple[0]
            _var_type = _var.var_type
            if _var_type == VarType.VT_INT:  # 假如变量是整形
                _int_value = _var_tuple[1]
                _var.var_int_value = _int_value
            elif _var_type == VarType.VT_ARRAY:  # 假如变量是整形数组
                _var_array_size = _var_tuple[1]
                _var_array_offset = _var_tuple[2]
                _var_array_pointer = _var_tuple[3]
                _var.var_array_size = _var_array_size
                _var.var_array_offset = _var_array_offset
                _var.var_array_pointer = _var_array_pointer
        self.protected_variable.clear()  # 清空。。。
