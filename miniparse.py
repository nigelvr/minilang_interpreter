import ply.yacc as yacc
from minilex import tokens

GlobalEnv = {}

precedence = (
    ('nonassoc', 'LT'),  # Nonassociative operators
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),            # Unary minus operator
)

BuiltinBinaryOperators = {
    '+' : lambda x,y: x+y,
    '-' : lambda x,y: x-y,
    '*' : lambda x,y: x*y,
    '/' : lambda x,y: x/y,
    '<' : lambda x,y: x<y,
}

def p_program(p):
    '''program : expression
               | statement'''
    p[0] = p[1]

def p_statement(p):
    '''statement : assignment
                 | funcdef'''
    p[0] = p[1]

def p_assignment(p):
    '''assignment : ID ASSIGN expression'''
    GlobalEnv[p[1]] = p[3]

def p_funcdef(p):
    'funcdef : FUNC ID LPAREN RPAREN LSQB RET expression RSQB'
    x = p[7]
    GlobalEnv[p[2]] = lambda : x

def p_expression_func_call(p):
    'expression : ID LPAREN RPAREN'
    p[0] = GlobalEnv[p[1]]()

def p_expression_lookup(p):
    'expression : ID'
    p[0] = GlobalEnv.get(p[1])
    if p[0] is None:
        raise Exception(f'Undefined reference {p[1]}')

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression LT expression'''
    p[0] = BuiltinBinaryOperators[p[2]](p[1], p[3])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expr_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = -p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

# Error rule for syntax errors
def p_error(p):
    raise Exception("Syntax error in input!")

# Build the parser
parser = yacc.yacc(start='program')

while True:
   try:
       s = input('calc > ')
   except EOFError:
       break
   if not s: continue
   result = parser.parse(s)
   print(result)
