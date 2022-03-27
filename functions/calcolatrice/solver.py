from mpmath.libmp.libhyper              import NoConvergence
from mpmath                             import polyroots
from time                               import time

from functions.calcolatrice.calcutils   import EspressioneNonValida, exp, replace, fcmplx, fnum, check_known

from ..utils                            import send_up, escape_md


__all__ = [
    'zeri',
    'solve'
]


apici = ('²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹', '¹⁰')


def solve(update, ctx):
    args = ctx.args
    maxtime = 5

    try:
        xmin, xmax, eq = exp(args[0]), exp(args[1]), ' '.join([i.strip() for i in args[2:]])
    except EspressioneNonValida:
        send_up(update, f'La scrittura corretta è: /risolvi min max membro1=membro2', markdown = 0)
        return
    except ValueError:
        send_up(update, 'Errore di dominio\.')
        return
    except ZeroDivisionError:
        send_up(update, 'Incontrata divisione per 0\.')
        return


    if eq.count('=') != 1:
        send_up(update, 'Scrittura non valida\.')
        return


    mem1, mem2 = eq.split('=')
    mem1 = replace(mem1, [(' ', ''), ('{[', '('), ('}]', ')')])
    mem2 = replace(mem2, [(' ', ''), ('{[', '('), ('}]', ')')])

    inter = str((xmin[1], xmax[1])).replace(',', ';').replace('\'', '')
    xmin, xmax = xmin[0], xmax[0]

    def f(x):
        try:
            return exp(mem1.replace('x', str(x)))[0] - exp(mem2.replace('x', str(x)))[0]
        except EspressioneNonValida:
            send_up(update, f'Equazione non valida\.')
            raise ZeroDivisionError
        except ValueError:
            send_up(update, 'Errore di dominio\.')
            raise ZeroDivisionError
        except ZeroDivisionError:
            send_up(update, 'Incontrata divisione per 0\.')
            raise ZeroDivisionError

    s = time()

    try:
        if (lower := f(xmin)) > (upper := f(xmax)):
            xmin, xmax = xmax, xmin
            lower, upper = upper, lower

        while 1:
            if time() - s > maxtime:
                send_up(update, f'`{eq}`\n`x ∈ {inter}`\n\nsoluzione non trovata')
                return

            c = (xmin + xmax) / 2

            if abs(y_c := f(c)) < 1e-6:
                res = check_known(c, 5)

                if res == str((c := round(c, 5))):
                    send_up(
                        update,
                        f'`{eq}`\n`x ∈ {inter}`\n\n`x ≈ {res}`',
                        markdown = 1
                    )
                else:
                    send_up(
                        update,
                        f'`{eq}`\n`x ∈ {inter}`\n\n`x = {res}`\n`  ≈ {c}`',
                        markdown = 1
                    )

                return c
            elif 0 < y_c:
                xmax, upper = c, y_c
            else:
                xmin, lower = c, y_c
    except ZeroDivisionError:
        return


def zeri(update, ctx):
    try:
        coeffs = [exp(i) for i in ctx.args][::-1]

        polinomio = []

        for i in range(len(coeffs)):
            numres, res = coeffs[i]

            if i == 0:
                polinomio.append(res)
            elif i == 1:
                if numres in (-1, 1):
                    polinomio.append(['-x', 'x'][numres == 1])
                else:
                    polinomio.append(res + 'x')
            else:
                if numres in (-1, 1):
                    polinomio.append(['-x', 'x'][numres == 1] + apici[i - 2])
                else:
                    polinomio.append(res + 'x' + apici[i - 2])

        polinomio = 'y = ' + '+'.join(polinomio[::-1]).replace('+-', '-')

        results = polyroots([i[0] for i in coeffs][::-1], maxsteps = 1000)

        if len(results) == 0:
            send_up(update, f'`{polinomio}`\n\nNessuno zero trovato.', markdown = 1)
            return

        results = [fcmplx(i, 5) if round(i.imag, 10) != 0 else fnum(i.real, 10, False) for i in results]
        results = ['`' + escape_md(i) + '`' for i in results]

        noncmplx = 0

        for i in results:
            if 'i' not in i:
                noncmplx += 1

        real, cmplx = results[:noncmplx], results[noncmplx:]
        real  = '*Zeri Reali*\n\n'     + '\n'.join(real) + '\n\n'  if len(real)  > 0 else ''
        cmplx = '*Zeri Complessi*\n\n' + '\n'.join(cmplx)          if len(cmplx) > 0 else ''

        send_up(update, f'`{escape_md(polinomio)}`\n\n{real}{cmplx}')
    except ValueError:
        pass
    except IndexError:
        send_up(update, f'Polinomio di grado superiore al 10, hai mpo\' sgravato non credi?', markdown = 0)
    except NoConvergence:
        send_up(update, f'Non sono riuscito a trovare gli zeri di\n`{polinomio}`\n', markdown = 0)
        send_up(update, f'😔', markdown = 0)

#print(solve(0, ['0', '2pi', 'sinx = cosx']))
#print(zeri(0, ['1', '-sqrt3']))
