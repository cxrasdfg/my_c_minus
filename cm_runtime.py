# -*-coding='UTF-8' -*-


from cm_parser import Parser
from cm_ast import ASTNode
from datetime import datetime
from cm_util import run_time_error
from cm_util import MsgType
from cm_frame import Frame


class RunTime(object):
    def __init__(self, _parser: Parser):
        self._parser = _parser
        assert _parser is not None
        self._symbol_table = _parser.get_symbol_table()
        self._start_time = None
        self._main_entry = ASTNode()

    def print_symbol_table(self):
        print(self._symbol_table)

    # 外部调用接口运行程序。。。
    def run(self):
        self._init()
        self._process()
        self._shutdown()

    # 运行的实现
    def _process(self):
        _main_frame = Frame.create_frame(self._main_entry, [])
        _main_frame.run_frame()

    # 初始化运行环境
    def _init(self):
        self._start_time = datetime.now()
        self._main_entry = self._symbol_table.get('main')
        if self._main_entry is None:
            run_time_error(MsgType.RUNTIME_ER_NO_ENTRY)
        print('\n*******************程序运行结果为：*************************\n')

    # 运行结束的相关操作
    def _shutdown(self):
        print('\n\n*******************程序运行结束：*************************\n')
        print('\n运行时间：{} ms\n'.format((datetime.now() - self._start_time).microseconds / 1000))
