if __name__ == '__main__':
    from known import known
    from funcs import *
else:
    from functions.calcolatrice.known import known
    from functions.calcolatrice.funcs import *

import mpmath

mpmath.mp.dps = 500


# CLASSI PER GLI ERRORI

class EspressioneNonValida(Exception):
    pass

class ComplexError(Exception):
    pass


# VARIABILI

vars = {}

signs = '+-*/^'
apici = '²³⁴⁵⁶⁷⁸⁹'
letters = 'abcdfghklmnoqrstuvwzABCDEFGHIJKLMNOPQRSTUVWXYZ'



# FUNZIONI

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
                    return evaluate(str(text) + '*' + i,)

                return False

        res = float(text)

        if int(res) == res:
            res = int(res)

        return res
    except ValueError:
        return False


def exp(text):
    if not (res := is_num(text)) is False:
        return (res, check_known(res, 10))

    if '(' in text:
        expression = text.split(')')[0].split('(')[-1]
        vars[letters[len(vars)]] = evaluate(expression)

        return exp(text.replace(f'({expression})', list(vars)[len(vars) - 1]))
    else:
        if '|' in text:
            expression = text.split('|')[1].split('|')[0]
            vars[letters[len(vars)]] = abs(evaluate(expression))

            return exp(text.replace(f'|{expression}|', list(vars)[len(vars) - 1]))

        oldtext = ''

        while oldtext != text:
            oldtext = text

            for c, i in enumerate(text):
                if i in vars and c > 0 and not is_num(text[c - 1]) is False:
                    text = text[:c] + '*' + text[c:]
                    break

        numres = evaluate(text)

        result = fcmplx(numres, 5) if round(numres.imag, 50) != 0 else fnum(numres.real, 20, False)

        if float(numres.real) == float('inf'):
            numres = float('inf')

        return (numres, result, vars.clear())[:-1]


def evaluate(expr):
    if 'i' in expr or 'j' in expr:
        raise ComplexError

    # se inizia per +, lo toglie

    if expr[0] == '+':
        expr = expr[1:]

    if not (res := is_num(expr)) is False:
        if isinstance(res, tuple):
            return evaluate(str(expr[:-1] + res[0]))

        return res

    # se inizia per -

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
            return evaluate(term2) - evaluate(temp)

        return -evaluate(temp + term2)

    if '-' in expr and check_double(expr):
        return minus(expr)
    elif '+' in expr:
        term1, term2 = expr.split('+', 1)

        if '-' in term1 and check_double(expr):
            term1 = str(minus(term1))

        return add(term1, term2)
    elif '*-' in expr:
        return mul(*expr.split('*-', 1), -1)
    elif '/-' in expr:
        return div(*expr.split('/-', 1), -1)
    elif '*' in expr:
        term1, term2 = expr.split('*', 1)

        if '/' in term1:
            term1 = str(div(*term1.split('/', 1)))

        return mul(term1, term2)
    elif '/' in expr:
        term1, term2 = expr.split('/', 1)

        if '*' in term1:
            term1 = str(mul(*term1.split('*', 1)))

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
                    return funcs[i](evaluate(arg))

                return mul(str(coeff), '%.50f' % funcs[i](evaluate(arg)))

    # se l'espressione non incontra nessuno dei casi precedenti ritorna l'errore

    raise EspressioneNonValida(expr)


# FUNZIONE PER GESTIRE LE ESPRESSIONI CON IL SEGNO -

def minus(expr):
    term1, term2 = expr.split('-', 1)

    # controlla se la parte prima del - è una funzione
    # se si, ne trova l'argomento e la chiama

    for i in funcs:
        if term1.endswith(i):
            c, temp = 0, term2[0]

            # l'argomento è tutta la parte dopo la funzione fino ad un'eventuale somma

            while c < len(term2) - 1 and term2[(c := c + 1)] not in '+-':
                temp += term2[c]

            # chiama la funzione usando come argomento 'temp' cambiato di segno

            res = funcs[i](-evaluate(temp))

            if res.imag != 0:
                raise ComplexError

            res = '%.50f' % funcs[i](-evaluate(temp))

            return evaluate(term1.replace(i, res) + term2.replace(temp, ''))

    # se c'è un + dopo il -, fa la somma a parte per mantenere il segno

    if '+' in term2:
        c, temp = 0, term2[0]

        while c < len(term2) - 1 and term2[(c := c + 1)] != '+':
            temp += term2[c]

        return evaluate(str(sub(term1, temp)) + term2.replace(temp, ''))

    return sub(term1, term2)



# OPERAZIONI DI BASE

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


def check_known_simple(num, digits = 50):
    max_check = 101

    if abs(num) == float('inf'):
        return str(num).replace('inf', '∞')

    if int(num) == num:
        return str(int(num))

    if round(num, digits) == 0:
        return '0'

    sign = round(abs(num) / num)
    signstr = str(sign)[:-1]
    ornum = abs(num)
    num = round(ornum, digits)

    for i in range(2, max_check):
        temp = num * i

        if int(temp) == temp:
            return f'{sign * int(temp)}/{i}'

    for i in known:
        if round(n := known[i], digits) == num:
            return signstr + i

        for j in range(2, max_check):
            if round(j * n, digits) == num:
                return str(sign * j) + i

        for j in range(-max_check, max_check):
            if round(j + n, digits) == num:
                return str(sign * j) + signstr + i

    return sign * ornum


def check_known(num, digits = 50):
    max_check = 101

    num = check_known_simple(num, digits)

    if isinstance(num, str):
        return num

    sign = int(abs(num) / num)
    signstr = str(sign)[:-1]
    num = round(abs(num), digits)

    for i in known:
        if round(n := known[i], digits) == num:
            return signstr + i

        for j in range(2, max_check):
            if round(j * n, digits) == num:
                return str(sign * j) + i

        for j in range(-max_check, max_check):
            if round(j + n, digits) == num:
                return str(sign * j) + signstr + i

        for j in known:
            if round(known[j] * n, digits) == num:
                if j == i:
                    if len(i) > 1:
                        return f'({i}){apici[0]}'

                    return i + apici[0]

                if len(i) > 1 or len(j) > 1:
                    return signstr + i + '*' + j

                return signstr + i + j

        for j in known:
            if round(known[j] + n, digits) == num:
                return i + ['-', '+'][not signstr] + j

    return str(sign * round(num, digits))


def fnum(num, digits, imag):
    num = check_known(float(num), digits)
    return [num, num + ' i'][imag]


def fcmplx(num, digits):
    return fnum(num.real, digits, False) + [' + ', ' - '][num.imag < 0] + fnum(abs(num.imag), digits, True)


# controlla se ci sono o meno operazioni doppie nell'espressione

def check_double(expr):
    for i in ('+-', '*-', '/-', '^-'):
        if i in expr:
            return False

    return True


# funzione per fare il .replace di più caratteri in una volta sola per compattare

def replace(text, lst):
    for i in lst:
        for j in i[0]:
            text = text.replace(j, i[1])

    return text



# controlla che nel testo tutte le parentesi e i moduli si chiudano

def check(text):
    char1, char2 = '{[(', '}])'

    # se i "|" sono dispari

    if text.count('|') % 2 == 1:
        return False

    # o se il numero di parentesi che si aprono non sono lo stesso di quelle che si chiudono

    for i in range(len(char1)):
        if text.count(char1[i]) != text.count(char2[i]):
            return False

    return True



# parte di codice che non viene eseguita e serve solo
# per testare che la calcolatrice dia i risultati giusti

if __name__ == '__main__':
    with open('functions/calcolatrice/tests.txt', encoding = 'utf-8') as f:
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
                    res = exp(text)[1]
                except:
                    pr = True
                    vars = {}

                if pr or not res == result:
                    print('\n' + text.ljust(30) + 'NOT OK')
                    print(exp(text), result)
                    print()
                    input()
                else:
                    cc += 1
                    ctotc += 1
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
