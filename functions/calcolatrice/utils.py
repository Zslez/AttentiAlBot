from math import sin, cos, tan, log, pi, e, asin, acos, atan



class SimboloNonValido(Exception):
    pass



def sec(x):
    return 1 / cos(x)

def csc(x):
    return 1 / sin(x)

def cot(x):
    return 1 / tan(x)


funcs = {
    'arcsin': asin,
    'asin'  : asin,
    'arccos': acos,
    'acos'  : acos,
    'arctan': atan,
    'atan'  : atan,
    'sin'   : sin,
    'sen'   : sin,
    'cos'   : cos,
    'tan'   : tan,
    'tg'    : tan,
    'tn'    : tan,
    'csc'   : csc,
    'sec'   : sec,
    'cot'   : cot,
    'ln'    : log
}


def is_num(text):
    try:
        if text == 'pi':
            return pi

        if text == 'e':
            return e

        res = float(text)

        if int(res) == res:
            res = int(res)

        return res
    except:
        return False


def exp(text):
    if (res := is_num(text)) != False:
        return res

    if '(' in text:
        expression = text.split(')')[0].split('(')[-1]

        return exp(text.replace(f'({expression})', str(evaluate(expression))))
    else:
        return evaluate(text)


def evaluate(expr):
    if (res := is_num(expr)) != False:
        return res

    elif '+' in expr:
        term1, term2 = expr.split('+', 1)

        if '-' in term1 and term1[0] != '-':
            term1 = sub(*term1.split('-', 1))

        return add(term1, term2)
    elif '-' in expr:
        term1, term2 = expr.split('-', 1)

        if '+' in term1:
            term1 = add(*term1.split('+', 1))

        return sub(term1, term2)
    if '*' in expr:
        term1, term2 = expr.split('*', 1)

        if '/' in term1:
            term1 = div(*term1.split('/', 1))

        return mul(term1, term2)
    elif '/' in expr:
        term1, term2 = expr.split('/', 1)

        if '*' in term1:
            term1 = mul(*term1.split('*', 1))

        return div(term1, term2)
    elif '^' in expr:
        return pow(*expr.split('^', 1))
    elif 'sqrt' in expr:
        return evaluate(expr.split('sqrt', 1)[-1]) ** 0.5
    else:
        for i in funcs:
            if i in expr:
                return funcs[i](evaluate(expr.split(i, 1)[-1]))

    raise SimboloNonValido


def add(exp1, exp2):
    return evaluate(exp1) + evaluate(exp2)

def sub(exp1, exp2):
    return evaluate(exp1) - evaluate(exp2)

def mul(exp1, exp2):
    return evaluate(exp1) * evaluate(exp2)

def div(exp1, exp2):
    return evaluate(exp1) / evaluate(exp2)

def pow(exp1, exp2):
    return evaluate(exp1) ** evaluate(exp2)



## ====================================== ##

def replace(text, lst):
    for i in lst:
        for j in i[0]:
            text = text.replace(j, i[1])

    return text


def count(text, char1, char2):
    for i in range(len(char1)):
        if text.count(char1[i]) != text.count(char2[i]):
            return False

    return True


def check(text):
    if  is_invalid(text) or \
        is_invalid(text.split('}')[0].split('{')[-1]) or \
        is_invalid(text.split(']')[0].split('[')[-1]):
        return False

    return True


def is_invalid(text):
    return not count(text, '{[(', '}])')
