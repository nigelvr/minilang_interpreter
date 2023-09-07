import ply.yacc as yacc
from pprint import pprint
from minilex import tokens
from miniast import (
    AST,
    FuncCallAST,
    FuncdefAST,
    IdentAST,
    NumberAST,
    BinopAST,
    UnaryAST,
    AssignmentAST
)

precedence = (
    ('nonassoc', 'LT'),  # Nonassociative operators
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS')
)

BasicEnvironment = {
    '+' : lambda x,y: x+y,
    '-' : lambda x,y: x-y,
    '*' : lambda x,y: x*y,
    '/' : lambda x,y: x/y,
    '<' : lambda x,y: x<y,
}

def printenv():
    print('---Global Environment---')
    pprint(BasicEnvironment)
    print('------------------------')

def flatten(L, class_instance, cond = lambda x : True):
    flat = []
    for x in L:
        if isinstance(x, class_instance) and cond(x):
            flat.append(x)
        elif isinstance(x, list):
            flat += flatten(x, class_instance)
    return flat

def p_program(p):
    '''program : expression
               | assignment_list expression
               | assignment_list funcdef_list expression
               | funcdef_list expression'''
    
    for k in range(1, len(p)-1):
        block_list = p[k]
        for block in block_list:
            block.emit(BasicEnvironment)
    
    p[0] = p[len(p)-1]

def p_funcdef_list(p):
    '''funcdef_list : funcdef
                    | funcdef_list funcdef'''
    p[0] = flatten(p[1:], FuncdefAST)
    

def p_assignment_list(p):
    '''assignment_list : assignment
                       | assignment_list assignment'''
    p[0] = flatten(p[1:], AssignmentAST)

def p_funcdef(p):
    '''funcdef : FUNC ID LPAREN arglist RPAREN LSQB funcpart RSQB
               | FUNC ID LPAREN arglist RPAREN LSQB RSQB'''

    funcname = p[2]
    expr = None

    arglist = p[4]

    if len(p) == 9: # has a function body
        expr = p[7]

    p[0] = FuncdefAST(funcname, arglist, expr)

def p_arglist(p):
    '''arglist : ID
               | arglist COMMA ID'''
    p[0] = flatten(p[1:], str, lambda x : x != ',')

def p_funcpart(p):
    'funcpart : RET expression SEMICOL'
    p[0] = p[2]

def p_assignment(p):
    'assignment : ID ASSIGN expression SEMICOL'
    ident = p[1]
    expr = p[3]
    p[0] = AssignmentAST(ident, expr)

def p_expression_funccall(p):
    'expression : ID LPAREN exprlist RPAREN'
    funcname = p[1]
    exprlist = p[3]
    p[0] = FuncCallAST(funcname, exprlist)

def p_exprlist(p):
    '''exprlist : expression
                | exprlist COMMA expression'''
    p[0] = flatten(p[1:], AST)

def p_expression_lookup(p):
    'expression : ID'
    p[0] = IdentAST(p[1])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression LT expression'''
    p[0] = BinopAST(p[2], p[1], p[3])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expr_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = UnaryAST('-', p[2])

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = NumberAST(p[1])

# Error rule for syntax errors
def p_error(p):
    raise Exception("Syntax error in input!")

# Build the parser
parser = yacc.yacc(start='program')

with open('./example/ex0.mini', 'r') as fd:
    result = parser.parse(fd.read())
    print(result.emit(BasicEnvironment))