# -*-coding="UTF-8" -*-


from enum import Enum


class VarType(Enum):
    VT_DEFAULT = 'default'  # 缺省类型 当然，也可以当做错误类型来看待。。。懒得再加个VT_ERROR了
    VT_INT = 'int'  # 整形
    VT_VOID = 'void'  # void 空
    VT_ARRAY = 'array'  # 数组类型 注意，这里的数组就是指的整形数组，没有什么结构数组，void数组。。。那些乱七八糟的


class ASTType(Enum):
    AST_DEFAULT = 'default'
    AST_LOCAL_DECLARATION = 'local_dec'  # 本地声明， 函数的形参也看作局部的本地声明。。
    AST_GLOBAL_DECLARATION = 'global_dec'
    AST_FUNC_DECLARATION = 'func_dec'
    AST_INNER_DECLARATION = 'inner declaration'  # 内部声明 such as output input
    AST_STATEMENT = 'statement'
    AST_IF_STATEMENT = 'if'
    AST_WHILE_STATEMENT = 'while'
    AST_COMPOUND_STATEMENT = 'compound'
    AST_EXPRESSION = 'expression'  # x+y,x+z 可以理解为逗号表达式```
    AST_ASSIGN_EXP = 'assign_exp'
    AST_SUFFIX_EXP = 'suffix_exp'
    AST_EQUAL_EXP = '=='
    AST_NOT_EQUAL_EXP = '!='
    AST_LARGER_EXP = '>'
    AST_LESS_EXP = '<'
    AST_NOT_LARGER_EXP = '<='
    AST_NOT_LESS_EXP = '>='
    AST_ADD_EXP = '+'
    AST_MINUS_EXP = '-'
    AST_MUL_EXP = '*'
    AST_DIV_EXP = '/'
    AST_ARRAY_INDEX = '[]'
    AST_FUNC_CALL = 'func_call'
    AST_PRIMARY_EXP = 'primary_exp'
    AST_CONST_INT = 'const integer'
    AST_SYMBOL_EXP = 'symbol_exp'
    AST_RETURN_EXP = 'return_exp'
    AST_BREAK_EXP = 'break_exp'


class ASTNode(object):
    node_count = 0

    def __init__(self):
        self.name = ''  # 名字 一般全局声明或局部声明才会有名字
        self.type = ASTType.AST_DEFAULT  # 表明节点的类型
        self.int_value = 0  # 表常数整数
        self.l_child = None  # 指代表达式节点的右子节点
        self.r_child = None  # 指代表达式节点的左子节点
        self.sub_statement = []  # 指代复合语句中的子语句
        self.sub_local_dec = {}  # 指代符合语句中的局部变量
        self.var = None  # 主要指代引用的符号, 如全局变量，局部变量(这里的变量是包括函数的)
        self.func_parameters = []  # 指代 int func(int x, int y) 中的 int x, int y...
        self.func_body = None  # 函数的函数体
        self.func_return_type = VarType.VT_DEFAULT  # 函数返回的类型
        self.arguments = []  # func(1+2,x+y*2) 指代的是表达式 1+2, x+y*2
        self.judge_exp = None  # 用与while 与 if 的条件判定
        self.if_body = None  # if 语句的主体
        self.if_else = None  # 跟在if语句后面的else语句
        self.while_body = None  # while 语句的主体

        self.var_type = VarType.VT_DEFAULT  # 变量的类型
        self.var_int_value = 0  # 整数变量的值
        self.var_array_size = 0  # 数组大小
        self.var_array_offset = 0  # 相对数组的偏移量 如 int x[10] 讲x+2 传入到函数参数中
        self.var_array_pointer = []  # 作为一个数组..

        self.return_exp = None  # 主要指向返回表达式的对应的返回表达式， 空的话就表示没有返回的值
        self.break_while = None  # 主要用于指向break语句break的while... 需要 ？ 不需要？ 好像没有break啊。。。 算了 就这样吧``
        self.draw_node_name = ''  # 用于绘制到dot语言的图形时指定的名字。。

        # 经过运算后的语义,主要是针对各种运算符，表达式的。如1+2是int,对于整数变量a,b, a+1是int, a+b仍然是int
        # 对于整数的关系运算符来说，a!=b,a!=1,a<=b...返回值都为整数，用整数0表示false，整数1表示true
        # 对于数组a,b来说,a可以作为参数传入函数中,表示其为数组,a+2表示从数组单元第3个开始数,结果也是数组
        # a+b是没有意义的,至于a>b 也许可以用id(a)>id(b)来替换，但是没有意义吧，索性不支持数组之间的比较运算，关系运算，应当提示报错
        # a[1]或者a[2]的结果为int。。或者说a[int_expression]的结果为int,a[b]自然是应该报错的
        # 函数的话，不能返回数组,或者没有返回值，，只能返回int，返回其他的或者在没有返回值的时候返回任何东西都应该报错。。
        self.exp_semantic_type = VarType.VT_DEFAULT

        # 运行时产生的值。。。
        self.exp_run_time_value = 0  # 运行时的赋予的值

    def draw(self, _gg):
        ASTNode.node_count += 1
        _node_name = '_node' + str(ASTNode.node_count)
        if self.draw_node_name == '':
            self.draw_node_name = _node_name
        else:
            _node_name = self.draw_node_name  # 防止对于同一个变量， 不同的调用形成多个节点
        if self.type == ASTType.AST_LOCAL_DECLARATION:
            _gg.add_node(_node_name, ASTType.AST_LOCAL_DECLARATION.value + ' ' + self.name + ':' + str(self.type.value))
        elif self.type == ASTType.AST_GLOBAL_DECLARATION:
            _gg.add_node(_node_name, ASTType.AST_GLOBAL_DECLARATION.value + ' ' + self.name + ':' + str(self.type.value)
                         )
        elif self.type == ASTType.AST_FUNC_DECLARATION:
            _gg.add_node(_node_name, ASTType.AST_FUNC_DECLARATION.value + ' ' + self.name + ' , return:' + str(
                self.func_return_type.value))
            _func_body = self.func_body.draw(_gg)  # 对函数体进行写入
            _gg.add_relation(_node_name, _func_body)
            _param_container_name = _node_name + '_parameters'
            _gg.add_node(_param_container_name, 'parameters')
            _gg.add_relation(_node_name, _param_container_name)
            for _param in self.func_parameters:
                _param_name = _param.draw(_gg)
                _gg.add_relation(_param_container_name, _param_name)
        elif self.type == ASTType.AST_INNER_DECLARATION:
            _gg.add_node(_node_name,
                         ASTType.AST_INNER_DECLARATION.value + ' ' + self.name + ' , return:'
                         + str(self.func_return_type.value))
            # _func_body = self.func_body.draw(_gg)  # 对函数体进行汇至
            # _gg.add_relation(_node_name, _func_body)
            _param_container_name = _node_name + 'parameters'
            _gg.add_node(_param_container_name, 'parameters')
            _gg.add_relation(_node_name, _param_container_name)
            for _param in self.func_parameters:
                _param_name = _param.draw(_gg)
                _gg.add_relation(_param_container_name, _param_name)
        # elif self.type == ASTType.AST_STATEMENT:
        #     self  # 打酱油的 不用管。。。
        elif self.type == ASTType.AST_IF_STATEMENT:
            _gg.add_node(_node_name, ASTType.AST_IF_STATEMENT.value)

            _judge_name = self.judge_exp.draw(_gg)
            _body_name = self.if_body.draw(_gg)
            _else_it = _node_name + '_else'
            _gg.add_node(_else_it, 'else')
            _gg.add_relation(_node_name, _else_it)
            if self.if_else is not None:
                _else_name = self.if_else.draw(_gg)
                _gg.add_relation(_else_it, _else_name)
            _gg.add_relation(_node_name, _judge_name)
            _gg.add_relation(_node_name, _body_name)
        elif self.type == ASTType.AST_WHILE_STATEMENT:
            _gg.add_node(_node_name, ASTType.AST_WHILE_STATEMENT.value)

            _judge_name = self.judge_exp.draw(_gg)
            _body_name = self.while_body.draw(_gg)

            _gg.add_relation(_node_name, _judge_name)
            _gg.add_relation(_node_name, _body_name)
        elif self.type == ASTType.AST_COMPOUND_STATEMENT:
            _gg.add_node(_node_name, ASTType.AST_COMPOUND_STATEMENT.value)
            _local_dec_container_name = _node_name + 'local_declaration'
            _sub_state_container_name = _node_name + 'sub_statements'
            _gg.add_node(_local_dec_container_name, 'local_declaration')
            _gg.add_node(_sub_state_container_name, 'sub statements')
            _gg.add_relation(_node_name, _local_dec_container_name)
            _gg.add_relation(_node_name, _sub_state_container_name)

            for _dec in self.sub_local_dec:
                _dec_name = self.sub_local_dec[_dec].draw(_gg)
                _gg.add_relation(_local_dec_container_name, _dec_name)

            for _state in self.sub_statement:
                _state_name = _state.draw(_gg)
                _gg.add_relation(_sub_state_container_name, _state_name)

        elif self.type == ASTType.AST_EXPRESSION:
            _gg.add_node(_node_name, ',')
            _l_name = self.l_child.draw(_gg)
            _r_name = self.r_child.draw(_gg)
            _gg.add_relation(_node_name, _l_name)
            _gg.add_relation(_node_name, _r_name)
        elif self.type == ASTType.AST_ASSIGN_EXP or \
            self.type == ASTType.AST_SUFFIX_EXP or \
            self.type == ASTType.AST_EQUAL_EXP or \
            self.type == ASTType.AST_NOT_EQUAL_EXP or \
            self.type == ASTType.AST_LARGER_EXP or \
            self.type == ASTType.AST_LESS_EXP or \
            self.type == ASTType.AST_NOT_LARGER_EXP or \
            self.type == ASTType.AST_NOT_LESS_EXP or \
            self.type == ASTType.AST_ADD_EXP or \
            self.type == ASTType.AST_MINUS_EXP or \
            self.type == ASTType.AST_MUL_EXP or \
            self.type == ASTType.AST_MUL_EXP or \
            self.type == ASTType.AST_DIV_EXP or \
                self.type == ASTType.AST_ARRAY_INDEX:
            _gg.add_node(_node_name, self.type.value)
            _l_name = self.l_child.draw(_gg)
            _r_name = self.r_child.draw(_gg)
            _gg.add_relation(_node_name, _l_name)
            _gg.add_relation(_node_name, _r_name)
        elif self.type == ASTType.AST_FUNC_CALL:
            _gg.add_node(_node_name, self.type.value)
            _l_child = self.l_child.draw(_gg)  # 左边应该是函数
            _gg.add_relation(_node_name, _l_child)
            _arguments_container_name = _node_name + '_arguments'
            _gg.add_node(_arguments_container_name, 'arguments')
            _gg.add_relation(_node_name, _arguments_container_name)
            for _param in self.r_child:
                _r_name = _param.draw(_gg)
                _gg.add_relation(_arguments_container_name, _r_name)
        # elif self.type == ASTType.AST_PRIMARY_EXP:
        #     self
        elif self.type == ASTType.AST_CONST_INT:
            _gg.add_node(_node_name, str(self.int_value) + ':const_int')
        elif self.type == ASTType.AST_SYMBOL_EXP:
            _gg.add_node(_node_name, self.type.value)
            if self.var.draw_node_name == '':
                _ref = self.var.draw(_gg)
            else:
                _ref = self.var.draw_node_name
            _gg.add_relation(_node_name, _ref)
        elif self.type == ASTType.AST_RETURN_EXP:
            _gg.add_node(_node_name, self.type.value)
            if self.return_exp is not None:
                _return = self.return_exp.draw(_gg)
                _gg.add_relation(_node_name, _return)
        elif self.type == ASTType.AST_BREAK_EXP:
            _gg.add_node(_node_name, ASTType.AST_BREAK_EXP.value)
        # elif self.type == ASTType.AST_DEFAULT:
        #     self
        return _node_name

# 反应表达式经过运算符运算后的结果的一张表，索引是三维的，数组索引是枚举类型VarType与ASTType
# 运算符只包括==,!=,<,<=,>,>=,+,-,*,/这10个...
# 详情参考 'resources/operator.puml'
exp_operator_table = {
    VarType.VT_INT: {
        VarType.VT_INT: {
            ASTType.AST_EQUAL_EXP: VarType.VT_INT,
            ASTType.AST_NOT_EQUAL_EXP: VarType.VT_INT,
            ASTType.AST_LESS_EXP: VarType.VT_INT,
            ASTType.AST_NOT_LARGER_EXP: VarType.VT_INT,
            ASTType.AST_LARGER_EXP: VarType.VT_INT,
            ASTType.AST_NOT_LESS_EXP: VarType.VT_INT,
            ASTType.AST_ADD_EXP: VarType.VT_INT,
            ASTType.AST_MINUS_EXP: VarType.VT_INT,
            ASTType.AST_MUL_EXP: VarType.VT_INT,
            ASTType.AST_DIV_EXP: VarType.VT_INT,
        },
        VarType.VT_ARRAY: {
            ASTType.AST_EQUAL_EXP: VarType.VT_DEFAULT,  # 这里的VT_DEFAULT和下文的VT_DEFAULT均表示错误类型，也就是非法的运算
            ASTType.AST_NOT_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_ADD_EXP: VarType.VT_ARRAY,
            ASTType.AST_MINUS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MUL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_DIV_EXP: VarType.VT_DEFAULT,
        },
        VarType.VT_VOID: {
            ASTType.AST_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_ADD_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MINUS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MUL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_DIV_EXP: VarType.VT_DEFAULT,
        },
    },

    VarType.VT_ARRAY: {
        VarType.VT_INT: {
            ASTType.AST_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_ADD_EXP: VarType.VT_ARRAY,
            ASTType.AST_MINUS_EXP: VarType.VT_ARRAY,
            ASTType.AST_MUL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_DIV_EXP: VarType.VT_DEFAULT,
        },
        VarType.VT_ARRAY: {
            ASTType.AST_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_ADD_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MINUS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MUL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_DIV_EXP: VarType.VT_DEFAULT,
        },
        VarType.VT_VOID: {
            ASTType.AST_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_ADD_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MINUS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MUL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_DIV_EXP: VarType.VT_DEFAULT,
        },
    },

    VarType.VT_VOID: {
        VarType.VT_INT: {
            ASTType.AST_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_ADD_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MINUS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MUL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_DIV_EXP: VarType.VT_DEFAULT,
        },
        VarType.VT_ARRAY: {
            ASTType.AST_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_ADD_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MINUS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MUL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_DIV_EXP: VarType.VT_DEFAULT,
        },
        VarType.VT_VOID: {
            ASTType.AST_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_EQUAL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_LARGER_EXP: VarType.VT_DEFAULT,
            ASTType.AST_NOT_LESS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_ADD_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MINUS_EXP: VarType.VT_DEFAULT,
            ASTType.AST_MUL_EXP: VarType.VT_DEFAULT,
            ASTType.AST_DIV_EXP: VarType.VT_DEFAULT,
        },
    },
}
