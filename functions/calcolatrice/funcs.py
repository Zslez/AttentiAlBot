import mpmath


mpmath.mp.dps = 500


funcs = {
    'arcsin': mpmath.asin,
    'arccos': mpmath.acos,
    'arctan': mpmath.atan,
    'asin'  : mpmath.asin,
    'acos'  : mpmath.acos,
    'atan'  : mpmath.atan,
    'sin'   : mpmath.sin,
    'sen'   : mpmath.sin,
    'cos'   : mpmath.cos,
    'tan'   : mpmath.tan,
    'tg'    : mpmath.tan,
    'csc'   : mpmath.csc,
    'sec'   : mpmath.sec,
    'cot'   : mpmath.cot,
    'exp'   : mpmath.exp,
    'ln'    : mpmath.log,
    'log'   : mpmath.log10,
    'Log'   : mpmath.log10,
    'sqrt'  : mpmath.sqrt,
    'cbrt'  : mpmath.cbrt,
    'abs'   : mpmath.absmax
}


constants = {
    'pi': mpmath.pi,
    'e' : mpmath.e
}
