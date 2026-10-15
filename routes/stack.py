from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .stack_inpost import tokenize, check_expression, infix_to_postfix


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    def __init__(self):
        self.top = None

    def push(self, data):
        new_node = Node(data)
        new_node.next = self.top
        self.top = new_node

    def pop(self):
        if self.top is None:
            return None
        data = self.top.data
        self.top = self.top.next
        return data

    def peek(self):
        if self.top is None:
            return None
        return self.top.data


def to_list(stack):
    items = []
    node = stack.top
    while node:
        items.append(node.data)
        node = node.next
    return items


# webpage 

stack_bp = Blueprint('stack', __name__)
MAX_ITEMS = 12


def load_stack():
    stack = Stack()
    for value in session.get('stack_items', []):
        stack.push(value)
    return stack


def save_stack(stack):
    session['stack_items'] = to_list(stack)[::-1]  


def parse_value(raw):
    try:
        return int(raw)
    except ValueError:
        return raw


def back(kind, message, hk=None):
    if kind == 'error':
        flash(message, kind)
    return redirect(url_for('stack.stack_page', hk=hk))


def handle_basics():
    action = request.form.get('action', '')
    raw = request.form.get('value', '').strip()
    stack = load_stack()

    if action == 'push':
        if raw == '':
            return back('error', 'Enter a value first.')
        if len(raw) > 20:
            return back('error', 'Please keep the value to 20 characters or fewer.')
        if len(to_list(stack)) >= MAX_ITEMS:
            return back('error', f'The demo stack holds up to {MAX_ITEMS} values. Pop one first.')
        value = parse_value(raw)
        stack.push(value)
        save_stack(stack)
        return back('success', f'Pushed {value} onto the top of the stack.', hk='new')

    if action == 'pop':
        removed = stack.pop()
        if removed is None:
            return back('error', 'The stack is empty, so there is nothing to pop.')
        save_stack(stack)
        return back('success', f'Popped {removed} off the top of the stack.')

    if action == 'peek':
        top = stack.peek()
        if top is None:
            return back('info', 'The stack is empty, so there is nothing to peek at.')
        return back('info', f'The top value is {top}.', hk='peek')

    if action == 'sample':
        stack = Stack()
        for v in (10, 20, 30):
            stack.push(v)
        save_stack(stack)
        return back('info', 'Loaded the sample: pushed 10, then 20, then 30.')

    if action == 'clear':
        save_stack(Stack())
        return back('info', 'The stack is now empty.')

    return back('error', 'Unknown action.')


@stack_bp.route('/works/stack', methods=['GET', 'POST'])
def stack_page():
    if request.method == 'POST':
        return handle_basics()

    hk = request.args.get('hk')
    if hk not in ('new', 'peek'):
        hk = None

    ctx = {
        'hk': hk,
        'items': to_list(load_stack()),
        'expr': request.args.get('expr', ''),
        'error': None,
    }

    expr = request.args.get('expr')
    if expr is not None:
        try:
            tokens = tokenize(expr)
            check_expression(tokens)
            postfix, steps = infix_to_postfix(tokens, Stack, to_list)
            ctx.update(postfix=postfix, steps=steps)
        except ValueError as err:
            ctx['error'] = str(err)

    return render_template('stack.html', **ctx)