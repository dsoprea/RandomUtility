"""Dijkstra's shunting yard algorithm for converting infix expressions to 
postfix.

This implementation omits support for function calls and arguments. We're only 
concerned with operators, parenthesis, and operands.
"""

OP_LPAREN = '('
OP_RPAREN = ')'
OP_MULTIPLY = '*'
OP_DIVIDE = '/'
OP_ADD = '+'
OP_SUBTRACT = '-'

OPERATORS_S = set([
    OP_MULTIPLY, 
    OP_DIVIDE, 
    OP_ADD, 
    OP_SUBTRACT, 
    OP_LPAREN, 
    OP_RPAREN,
])

PRECEDENCE = {
    OP_MULTIPLY: 7,
    OP_DIVIDE: 7,
    OP_ADD: 5,
    OP_SUBTRACT: 5,
    OP_LPAREN: 1,
    OP_RPAREN: 1,
}

LEFT_ASSOCIATIVE_S = set([
    OP_MULTIPLY,
    OP_DIVIDE,
    OP_ADD, 
    OP_SUBTRACT, 
    OP_LPAREN, 
    OP_RPAREN,
])

def _convert(expression_phrase):
    expression_phrase = expression_phrase.replace(' ', '')

    stack = []
    output = []
    for c in expression_phrase:
        if c not in OPERATORS_S:
            # It's an operand.
            output += [c]
        elif c not in (OP_LPAREN, OP_RPAREN):
            # It's an operator. Pop-and-add all recent operators that win over 
            # the current operator via precendence/associativity.

            current_prec = PRECEDENCE[c]
            is_left_assoc = c in LEFT_ASSOCIATIVE_S
            while len(stack):
                top_value = stack[-1]
                top_prec = PRECEDENCE[top_value]

                if is_left_assoc is True and current_prec <= top_prec or \
                   is_left_assoc is False and current_prec < top_prec:
                    stack.pop()
                    output += [top_value]
                else:
                    break

            stack.append(c)
        
        elif c == OP_LPAREN:
            # It's a left paren.

            stack.append(c)
        else: #if c == OP_RPAREN:
            # It's a right paren. Pop-and-add everything since the last left 
            # paren.

            found = False
            while len(stack):
                top_value = stack.pop()
                if top_value == OP_LPAREN:
                    found = True
                    break

                output += [top_value]

            if found is False:
                raise ValueError("Mismatched parenthesis (1).")

    if stack and stack[-1] in (OP_LPAREN, OP_RPAREN):
        raise ValueError("Mismatched parenthesis (2).")

    # Flush everything left on the stack.
    while stack:
        c = stack.pop()
        output += [c]

    return ' '.join(output)

def _main():
    infix_phrase = 'a * (b * c) / d * (e + f + g) * h - i'
    print(infix_phrase)

    postfix_phrase = _convert(infix_phrase)
    print(postfix_phrase)

if __name__ == '__main__':
    _main()
