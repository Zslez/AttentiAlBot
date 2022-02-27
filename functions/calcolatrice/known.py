import mpmath

mpmath.mp.dps = 50

known = {
    '√2'        : mpmath.sqrt(2),
    '√3'        : mpmath.sqrt(3),
    '√5'        : mpmath.sqrt(5),
    '√7'        : mpmath.sqrt(7),
    '√11'       : mpmath.sqrt(11),
    '√13'       : mpmath.sqrt(13),
    '∛2'        : mpmath.cbrt(2),
    '∛3'        : mpmath.cbrt(3),
    '∛5'        : mpmath.cbrt(5),
    '∛7'        : mpmath.cbrt(7),
    'π'         : mpmath.pi,
    'π/2'       : mpmath.pi / 2,
    'π/3'       : mpmath.pi / 3,
    'π/4'       : mpmath.pi / 4,
    'π/6'       : mpmath.pi / 6,
    'π/8'       : mpmath.pi / 8,
    'π/12'      : mpmath.pi / 12,
    'e'         : mpmath.e,
    'e/2'       : mpmath.e  / 2,
    'e/3'       : mpmath.e  / 3,
    'e/4'       : mpmath.e  / 4
}