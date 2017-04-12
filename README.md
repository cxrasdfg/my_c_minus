C- -- 编译原理的作业
=============


C- 是C语言的一个子集

采用递归子程序(LL(1))的方式进行的语法、语义分析，通过遍历生成的AST实现运行环境

目前还没有完全经过测试，等有空了继续填坑

用法:
---
1. 需要安装python3.5
2. 进入代码主目录,在终端运行 python3.5 main.py [C-源文件路径]\
   如 python3.5 main.py resources/target.c

代码结构:
--------

代码分为两个主要的部分,一个是parser， 用于生成AST，另一个是runtime,用于生成ast后的运行

### <h2 id='1'>Parser:</h2>
1. cm_parser.py 对传入的c-源码文件进行编译，通过调用parse生成AST在
2. cm_ast.py AST的节点的实现
3. cm_lexer.py 主要用于parser获取token(单词)
4. cm_parser.py parser的主要实现部分，包括了语法分析，语义分析，AST生成
5. cm_token.py 单词的基本数据结构

### <h2 id='2'>RunTime:</h2>
1. cm_runtime.py 运行环境，用于执行AST
2. cm_frame.py 帧的生成与执行

### <h2 id='3'>其他:</h2>
1. cm_util.py 常用的函数，如出错提示，以及一个生成基于dot语言的AST图形
2. cm_kid.py 第一次用python，主要用于测试python的某些语法。。。
3. main.py 程序运行的入口
4. resources: <p>resources/ast.puml 与 ast.puml均表示生成的ast的图形化表示</p>
              <p>resources/target.c 为要编译的C-语言的源文件</p>
              <p>resources/operator.puml 表示类型运算的结果图例</p>
5. C-Minus 定义:
   <p> 1.1 基本的关键字:else  if  int  return  void  while</p>
   <p> 1.2 专用符号： +  -  *  /  <  <=  >  >=  ==  !=  =  ;  ,  (  )  [  ]  {  }  /*  */ </p>
   <p> 1.3 ID和NUM :<br/>
      &nbsp;&nbsp;&nbsp;&nbsp;  ID = letter letter*<br/>
      &nbsp;&nbsp;&nbsp;&nbsp;  NUM = digit digit*<br/>
      &nbsp;&nbsp;&nbsp;&nbsp;  letter = a|…|z|A|...|Z<br/>
      &nbsp;&nbsp;&nbsp;&nbsp;   digit = 0|…|9
   </p>
   <p>
      1.4 空格由空白、换行符和制表符组成。除了在必须分割ID、NUM关键字之外，其他情况下空格常被忽略。
   </p>
   <p>1.5 注释由/*...*/表示，它可以被放在任何空白位置，且可以超过一行，但是不能嵌套。</p>
   <p>1.6 语法定义：
   只支持整型与整形数组,支持作用于空间， 运算支持+ - × / </p>





