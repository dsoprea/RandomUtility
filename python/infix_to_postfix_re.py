"""\
A regular-expression parser.

Examples:

    Infix: ab*c(g+h)
    Postfix: ab*.c.g+h..

Based on https://swtch.com/~rsc/regexp/nfa.c.txt
"""

def re2post(re):
    plist = []

    nalt = 0
    natom = 0

    # Copy the original string plus some buffer.
    dst = list(re) + [''] * len(re)

    dst_i = 0

    for c in re:
        if c == '(':
            if natom > 1:
                natom -= 1

                dst[dst_i] = '.'
                dst_i += 1

            # Push

            plist.append((nalt, natom))

            nalt = 0
            natom = 0

        elif c == '|':
            if natom == 0:
                raise ValueError("Alternation at front of string.")

            natom -= 1
            while natom > 0:
                dst[dst_i] = '.'
                dst_i += 1

                natom -= 1

            nalt += 1

        elif c == ')':
            if not plist:
                raise ValueError("Encountered a right-paren without a left-paren.")
            elif natom == 0:
                raise ValueError("Encountered a right-paren at the front of the string.")

            natom -= 1
            while natom > 0:
                dst[dst_i] = '.'
                dst_i += 1

                natom -= 1

            while nalt > 0:
                dst[dst_i] = '|'
                dst_i += 1

                nalt -= 1

            # Pop.

            (nalt, natom) = plist.pop()
            natom += 1

        elif c in ('*', '+', '?'):
            if natom == 0:
                raise ValueError("*+? at front of string.")

            dst[dst_i] = c
            dst_i += 1
        else:
            if natom > 1:
                natom -= 1

                dst[dst_i] = '.'
                dst_i += 1

            dst[dst_i] = c
            dst_i += 1

            natom += 1

    if plist:
        raise ValueError("Unbalanced parentheses.")

    natom -= 1
    while natom > 0:
        dst[dst_i] = '.'
        dst_i += 1

        natom -= 1

    while nalt > 0:
        dst[dst_i] = '|'
        dst_i += 1

        nalt -= 1

    return ''.join(dst)

def _main():
    re = 'ab*c(g+h)|i'
    print(re)

    postfix = re2post(re)
    print(postfix)

if __name__ == '__main__':
    _main()
