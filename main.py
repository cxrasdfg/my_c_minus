# -*-coding ="UTF-8"-*-


import sys
from cm_kid import test_entry
from cm_parser import Parser
from cm_runtime import RunTime
from cm_lexer import Lexer

TOKEN_TEST = False  # 启动lexer 测试

if len(sys.argv) < 2:
    print('需要输入文件名!')
    exit(0)

_script_path = sys.argv[0]
_target_path = sys.argv[1]
print('脚本路径：', _script_path)
print('目标文件路径:', _target_path)
test_entry()

if TOKEN_TEST:
    Lexer.test(_target_path)
    print('\n')

_parser = Parser(_target_path)
_run_time = RunTime(_parser)
_parser.parse()
_parser.write_graph()
_run_time.run()

# _test = {'output': 1, 'input': 2, 'main': 3, 'gcd': 4}
#
# for elem in _test:
#     print(elem)
#


_test = {'1': {'1': 1},
         '2': {'2': 2},
         '3': {'3': 3},
         '4': {'4': 4},
         }
