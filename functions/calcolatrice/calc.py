from functions.calcolatrice.utils import exp, check, replace, SimboloNonValido

from ..utils import send_up


__all__ = [
    'calc'
]


def calc(update, ctx):
    text = ''.join(ctx.args)

    if not check(text):
        send_up(update, 'Testo non valido\. Controlla che tutte le parentesi si chiudano\.')
        return

    text = replace(text, [(' ', ''), ('{[', '('), ('}]', ')')])

    try:
        res = exp(text)
    except SimboloNonValido:
        send_up(update, 'Hai usato un simbolo non valido\.')
        return
    except ValueError:
        send_up(update, 'Errore di dominio\.')
        return


    if int(res) == res:
        res = int(res)

    send_up(update, '```' + str(res) + '```', markdown = 1)
