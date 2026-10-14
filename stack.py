# Stack: your original class + the web page for it.
# (Keep the Node / Stack names exactly as written.)

import math
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    def __init__(self):
        self.top = None

    def push(self, data):
        new_node = Node(data)
        if self.top:
            new_node.next = self.top
        self.top = new_node


    def pop(self):
        if self.top is None:
            return None
        else:
            popped_node = self.top
            self.top = self.top.next
            popped_node.next = None
            return popped_node.data

    def peek(self):
        if self.top:
            return self.top.data
        else:
            return None


    def print_stack(self):
        if self.top is None:
            print("Stack is empty")
        else:
            current = self.top
            print("Stack elements (top → bottom):")
            while current:
                print(current.data)
                current = current.next


# ---------- Web page for the stack ----------
# Every visitor gets their own stack (kept in their browser session),
# and every feature below is built on the Stack class above.

stack_bp = Blueprint('stack', __name__)

MAX_ITEMS = 12        # keeps the diagram tidy


def to_list(stack):
    """Stack -> Python list, top first (only used to draw the page)."""
    items = []
    node = stack.top
    while node:
        items.append(node.data)
        node = node.next
    return items


def load_stack(key):
    stack = Stack()
    for value in session.get(key, []):      # saved bottom -> top
        stack.push(value)
    return stack


def save_stack(key, stack):
    session[key] = to_list(stack)[::-1]


def parse_value(raw):
    """'5' -> 5, '2.5' -> 2.5, anything else stays text."""
    raw = raw.strip()
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        number = float(raw)
        if math.isfinite(number):
            return number
    except ValueError:
        pass
    return raw


def back(kind, message, hk=None):
    """Only errors are shown to the user; other results just redirect."""
    if kind == 'error':
        flash(message, kind)
    return redirect(url_for('stack.stack_page', hk=hk))


# ----- push / pop / peek -----

def handle_basics():
    action = request.form.get('action', '')
    raw = request.form.get('value', '').strip()
    stack = load_stack('stack_items')

    if action == 'push':
        if raw == '':
            return back('error', 'Enter a value first.')
        if len(raw) > 20:
            return back('error', 'Please keep the value to 20 characters or fewer.')
        if len(to_list(stack)) >= MAX_ITEMS:
            return back('error', f'The demo stack holds up to {MAX_ITEMS} values. Pop one first.')
        value = parse_value(raw)
        stack.push(value)
        save_stack('stack_items', stack)
        return back('success', f'Pushed {value} onto the top of the stack.', hk='new')

    if action == 'pop':
        removed = stack.pop()
        if removed is None:
            return back('error', 'The stack is empty, so there is nothing to pop.')
        save_stack('stack_items', stack)
        return back('success', f'Popped {removed} off the top of the stack.')

    if action == 'peek':
        top = stack.peek()
        if top is None:
            return back('info', 'The stack is empty, so there is nothing to peek at.')
        return back('info', f'The top value is {top}. Peek only looks, nothing was removed.',
                    hk='peek')

    if action == 'sample':
        stack = Stack()
        for v in (10, 20, 30):
            stack.push(v)
        save_stack('stack_items', stack)
        return back('info', 'Loaded the sample: pushed 10, then 20, then 30.')

    if action == 'clear':
        save_stack('stack_items', Stack())
        return back('info', 'The stack is now empty.')

    return back('error', 'Unknown action.')


# ----- infix -> postfix -----

TOKEN_RE = re.compile(r'\s*(\d+\.?\d*|\.\d+|[A-Za-z_]\w*|[-+*/^%()])')
PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2, '^': 3}
RIGHT_ASSOCIATIVE = {'^'}


def is_operand(token):
    return token not in PRECEDENCE and token not in '()'


def tokenize(expression):
    expression = expression.strip()
    tokens, pos = [], 0
    while pos < len(expression):
        match = TOKEN_RE.match(expression, pos)
        if not match:
            bad = expression[pos:].strip()[:1]
            raise ValueError(f'I don\'t understand "{bad}". Use numbers, letters, '
                             f'+ - * / % ^ and parentheses.')
        tokens.append(match.group(1))
        pos = match.end()
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
                raise ValueError(f'"{t}" needs a number or letter before it '
                                 f'(negative numbers are not supported here).')
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


def infix_to_postfix(tokens):
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
            while True:
                top = operators.peek()
                if top is None or top == '(':
                    break
                higher = PRECEDENCE[top] > PRECEDENCE[t]
                same = PRECEDENCE[top] == PRECEDENCE[t] and t not in RIGHT_ASSOCIATIVE
                if not (higher or same):
                    break
                popped.append(operators.pop())
                output.append(popped[-1])
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


# ----- the page -----

@stack_bp.route('/works/stack', methods=['GET', 'POST'])
def stack_page():
    if request.method == 'POST':
        return handle_basics()

    hk = request.args.get('hk')
    if hk not in ('new', 'peek'):
        hk = None

    ctx = {
        'hk': hk,
        'items': to_list(load_stack('stack_items')),
        'expr': request.args.get('expr', ''),
        'error': None,
    }

    expr = request.args.get('expr')
    if expr is not None:
        try:
            tokens = tokenize(expr)
            check_expression(tokens)
            postfix, steps = infix_to_postfix(tokens)
            ctx.update(postfix=postfix, steps=steps)
        except ValueError as err:
            ctx['error'] = str(err)

    return render_template('stack.html', **ctx)


if __name__ == "__main__":
    # Create an empty stack
    stack = Stack()
    stack.print_stack()

    # Push some elements onto the stack
    stack.push(10)
    stack.push(20)
    stack.push(30)
    stack.print_stack()

    # Peek at the top element without removing it
    print("Top element:", stack.peek())

    # Pop elements off the stack
    print("Popped:", stack.pop())
    print("Popped:", stack.pop())
    stack.print_stack()

    # Pop the last element, then try popping from an empty stack
    print("Popped:", stack.pop())
    print("Popped from empty stack:", stack.pop())
    print("Peek on empty stack:", stack.peek())
    stack.print_stack()