from functions.calcolatrice.calcutils import exp, check, replace, EspressioneNonValida, ComplexError

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
    except EspressioneNonValida:
        send_up(update, 'Espressione non valida')
        return
    except ComplexError:
        send_up(update, 'Il calcolo comprende operazioni con i complessi')
        return
    except ValueError:
        send_up(update, 'Errore di dominio')
        return
    except ZeroDivisionError:
        send_up(update, 'Incontrata divisione per 0')
        return

    send_up(update, f'`{res[1]}`\n`≈ {round(res[0], 10)}`', markdown = 1)
