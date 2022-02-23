from math import sin, cos, tan, log, log10, pi, e, asin, acos, atan


class SimboloNonValido(Exception):
    pass


def sec(x):
    return 1 / round(cos(x), 10)

def csc(x):
    return 1 / round(sin(x), 10)

def cot(x):
    return 1 / round(tan(x), 10)

def sqrt(x):
    return x ** 0.5

def cbrt(x):
    return x ** (1 / 3)


funcs = {
    'arcsin': asin,
    'arccos': acos,
    'arctan': atan,
    'asin'  : asin,
    'acos'  : acos,
    'atan'  : atan,
    'sin'   : sin,
    'sen'   : sin,
    'cos'   : cos,
    'tan'   : tan,
    'tg'    : tan,
    'csc'   : csc,
    'sec'   : sec,
    'cot'   : cot,
    'ln'    : log,
    'log'   : log10,
    'Log'   : log10,
    'sqrt'  : sqrt,
    'cbrt'  : cbrt,
    'abs'   : abs
}

constants = {
    'pi': pi,
    'e' : e
}

vars = {}

signs = '+-*/^'
letters = 'abcdfghklmnoqrstuvwzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def check_double(expr):
    for i in ('+-', '--', '*-', '/-', '^-'):
        if i in expr:
            return False

    return True


def is_num(text):
    if text == '':
        return False

    try:
        for i in funcs:
            if text.endswith(i):
                return False

        allvars = {**constants, **vars}

        for i in allvars:
            if text.endswith(i) and text.count(i) == 1:
                factor = allvars[i]
                text = text.replace(i, '')

                if text == '':
                    return factor

                if not (text := is_num(text)) is False:
                    return ('*' + i,)

                return False

        res = float(text)

        if int(res) == res:
            res = int(res)

        return res
    except ValueError:
        return False


def exp(text, show = False):
    if not (res := is_num(text)) is False:
        return res

    if '(' in text:
        expression = text.split(')')[0].split('(')[-1]
        vars[letters[len(vars)]] = evaluate(expression, show)

        return exp(text.replace(f'({expression})', list(vars)[len(vars) - 1]), show)
    else:
        if '|' in text:
            expression = text.split('|')[1].split('|')[0]
            vars[letters[len(vars)]] = abs(evaluate(expression, show))

            return exp(text.replace(f'|{expression}|', list(vars)[len(vars) - 1]), show)

        for c, i in enumerate(text):
            if i in vars and c > 0 and not is_num(text[c - 1]) is False:
                text = text[:c] + '*' + text[c:]

        return (evaluate(text, show), vars.clear())[0]


def evaluate(expr, show = False):
    if show:
        print(expr.ljust(30), vars)

    if not (res := is_num(expr)) is False:
        if isinstance(res, tuple):
            return evaluate(expr[:-1] + res[0])

        return res

    if expr[0] == '+':
        expr = expr[1:]

    if expr[0] == '-':
        term2 = expr[1:]
        c, temp = 0, term2[0]

        while c < len(term2) - 1 and term2[(c := c + 1)] not in signs:
            temp += term2[c]

        term2 = term2.replace(temp, '', 1)

        if term2 == '':
            return -evaluate(expr[1:])

        sign = term2[0]

        if sign in '+-':
            return evaluate(term2, show) - evaluate(temp, show)

        return -evaluate(temp + term2, show)

    if '-' in expr and check_double(expr):
        return minus(expr)
    elif '+' in expr:
        term1, term2 = expr.split('+', 1)

        if '-' in term1 and '^-' not in expr:
            term1 = str(minus(term1))

        return add(term1, term2)
    elif '*-' in expr:
        return mul(*expr.split('*-', 1), -1)
    elif '/-' in expr:
        return div(*expr.split('/-', 1), -1)
    elif '*' in expr:
        term1, term2 = expr.split('*', 1)

        if '/' in term1:
            term1 = div(*term1.split('/', 1))

        return mul(term1, term2)
    elif '/' in expr:
        term1, term2 = expr.split('/', 1)

        if '*' in term1:
            term1 = mul(*term1.split('*', 1))

        return div(term1, term2)
    elif '^-' in expr:
        return pow(*expr.split('^-', 1), -1)
    elif '^' in expr:
        return pow(*expr.split('^', 1))
    else:
        for i in funcs:
            if i in expr:
                coeff, arg = expr.split(i, 1)

                if coeff == '' or (res := is_num(coeff[-1])) is False:
                    return funcs[i](evaluate(arg, show))

                return mul(str(coeff), '%.10f' % funcs[i](evaluate(arg, show)))

    raise SimboloNonValido


def minus(expr):
    term1, term2 = expr.split('-', 1)

    for i in funcs:
        if term1.endswith(i):
            c, temp = 0, term2[0]

            while c < len(term2) - 1 and term2[(c := c + 1)] not in '+-':
                temp += term2[c]

            res = '%.10f' % funcs[i](-evaluate(temp))

            return evaluate(term1.replace(i, res) + term2.replace(temp, ''))

    if '+' in term2:
        c, temp = 0, term2[0]

        while c < len(term2) - 1 and term2[(c := c + 1)] != '+':
            temp += term2[c]

        return evaluate(str(sub(term1, temp)) + term2.replace(temp, ''))
    else:
        return sub(term1, term2)


def add(exp1, exp2):
    return evaluate(exp1) + evaluate(exp2)

def sub(exp1, exp2):
    return evaluate(exp1) - evaluate(exp2)

def mul(exp1, exp2, sign = 1):
    return evaluate(exp1) * (sign * evaluate(exp2))

def div(exp1, exp2, sign = 1):
    return evaluate(exp1) / (sign * evaluate(exp2))

def pow(exp1, exp2, sign = 1):
    return evaluate(exp1) ** (sign * evaluate(exp2))



## ====================================== ##



def replace(text, lst):
    for i in lst:
        for j in i[0]:
            text = text.replace(j, i[1])

    return text


def count(text, char1, char2):
    if text.count('|') % 2 == 1:
        return False

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


if __name__ == '__main__':
    with open('functions/calcolatrice/test.txt') as f:
        cc, cr, ctotc, ctotr = 0, 0, 0, 0
        start = True

        for i in f.read().split('\n'):
            if i == '':
                continue

            if ';' in i:
                text, result = i.split(';')
                cr += 1
                ctotr += 1
                pr = False

                try:
                    res = exp(text)
                except:
                    pr = True
                    vars = {}

                if not str(round(res, 5)) == result or pr:
                    print('\n' + text.ljust(30) + 'NOT OK')
                    print(str(round(exp(text, True), 5)), result)
                    print()
                else:
                    cc += 1
                    ctotc += 1
                    #print('ok')
            else:
                if not start:
                    print('Passed:'.ljust(30) + str(cc).rjust(2) + '/' + str(cr).rjust(2))
                    print()

                cc = 0
                cr = 0
                print('Checking... ' + i.upper())
                start = False

        print('Passed:'.ljust(30) + str(cc).rjust(2) + '/' + str(cr).rjust(2))
        print('\n')
        print('Total Passed:'.ljust(30) + str(ctotc).rjust(2) + '/' + str(ctotr).rjust(2))
