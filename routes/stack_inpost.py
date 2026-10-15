import re

PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2, '^': 3}

def is_operand(token):
    return token not in PRECEDENCE and token not in '()'

def tokenize(expression):
    tokens = re.findall(r'\d+\.?\d*|\.\d+|[A-Za-z_]\w*|[-+*/^%()]', expression)
    if ''.join(tokens) != re.sub(r'\s', '', expression):
        raise ValueError('Use only numbers, letters, + - * / % ^ and parentheses.')
    return tokens

def check_expression(tokens):
    if not tokens:
        raise ValueError('Type an expression first, for example (A + B) * C.')
    depth, expect_operand = 0, True
    for t in tokens:
        if expect_operand:
            if is_operand(t):
                expect_operand = False
            elif t == '(':
                depth += 1
            elif t == ')':
                raise ValueError('There is nothing between the parentheses "( )".'
                                 if depth else 'A ")" has no matching "(".')
            else:
                raise ValueError(f'"{t}" needs a number or letter before it.')
        else:
            if t in PRECEDENCE:
                expect_operand = True
            elif t == ')':
                depth -= 1
                if depth < 0:
                    raise ValueError('A ")" has no matching "(".')
            elif t == '(':
                raise ValueError('Put an operator (like +) before "(".')
            else:
                raise ValueError(f'Put an operator between "{t}" and the item before it.')
    if expect_operand:
        raise ValueError('The expression cannot end with an operator.')
    if depth > 0:
        raise ValueError('A "(" is never closed.')


def infix_to_postfix(tokens, Stack, to_list):
    operators = Stack()
    output, steps = [], []

    def snap(token, action):
        steps.append({'token': token, 'action': action,
                      'stack': to_list(operators), 'output': ' '.join(output)})

    for t in tokens:
        if is_operand(t):
            output.append(t)
            snap(t, 'Operand: send it straight to the output.')

        elif t == '(':
            operators.push(t)
            snap(t, 'Open parenthesis: push it.')

        elif t == ')':
            while operators.peek() != '(':
                output.append(operators.pop())
            operators.pop()   
            snap(t, 'Close parenthesis: pop operators to the output until "(", then discard "(".')

        else:  
            popped = []
            while operators.peek() not in (None, '('):
                top = operators.peek()
                if PRECEDENCE[top] > PRECEDENCE[t] or (PRECEDENCE[top] == PRECEDENCE[t] and t != '^'):
                    popped.append(operators.pop())
                    output.append(popped[-1])
                else:
                    break
            operators.push(t)
            if popped:
                snap(t, f'Operator: {", ".join(popped)} on the stack ranks the same or higher, '
                        f'so pop it to the output, then push {t}.')
            else:
                snap(t, 'Operator: push it (nothing on the stack outranks it).')

    if operators.peek() is not None:
        while operators.peek() is not None:
            output.append(operators.pop())
        snap('end', 'End of input: pop everything left on the stack to the output.')

    return ' '.join(output), steps