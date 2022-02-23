from functions.calcolatrice.calcutils import exp, check, replace, SimboloNonValido

from ..utils import send_up


__all__ = [
    'calc'
]


def calc(update, ctx):
    text = ''.join(ctx.args)

    if not check(text):
        send_up(update, 'Controlla che tutte le parentesi e i moduli si chiudano correttamente\.')
        return

    text = replace(text, [(' ', ''), ('{[', '('), ('}]', ')')])

    if not text:
        return

    try:
        res = exp(text)
    except SimboloNonValido:
        send_up(update, 'Espressione non valida\.')
        return
    except ValueError:
        send_up(update, 'Errore di dominio\.')
        return
    except ZeroDivisionError:
        send_up(update, 'Incontrata divisione per 0\.')
        return


    digits = 5
    res = round(res, digits)

    if int(res) == res:
        res = int(res)

    send_up(update, f'```{res}```', markdown = 1)
