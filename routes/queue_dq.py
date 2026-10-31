from flask import Blueprint, render_template, request, redirect, url_for, flash, session


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Queue:
    def __init__(self):
        self.front = None
        self.rear = None

    def enqueue(self, data):
        new_node = Node(data)
        if self.rear is None:          
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node

    def dequeue(self):
        if self.front is None:
            return None
        data = self.front.data
        self.front = self.front.next
        if self.front is None:        
            self.rear = None
        return data

    def peek(self):
        if self.front is None:
            return None
        return self.front.data


def to_list(queue):

    items = []
    node = queue.front
    while node:
        items.append(node.data)
        node = node.next
    return items


# ---------------------------------------------------------------
# Double-ended queue (deque): a doubly linked list, so both ends
# can be added to and removed from in constant time.
# ---------------------------------------------------------------

class DNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class Deque:
    def __init__(self):
        self.front = None
        self.rear = None

    def add_front(self, data):
        new_node = DNode(data)
        if self.front is None:
            self.front = self.rear = new_node
        else:
            new_node.next = self.front
            self.front.prev = new_node
            self.front = new_node

    def add_rear(self, data):
        new_node = DNode(data)
        if self.rear is None:
            self.front = self.rear = new_node
        else:
            new_node.prev = self.rear
            self.rear.next = new_node
            self.rear = new_node

    def remove_front(self):
        if self.front is None:
            return None
        data = self.front.data
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        else:
            self.front.prev = None
        return data

    def remove_rear(self):
        if self.rear is None:
            return None
        data = self.rear.data
        self.rear = self.rear.prev
        if self.rear is None:
            self.front = None
        else:
            self.rear.next = None
        return data

    def peek_front(self):
        return None if self.front is None else self.front.data

    def peek_rear(self):
        return None if self.rear is None else self.rear.data


def deque_to_list(dq):
    items = []
    node = dq.front
    while node:
        items.append(node.data)
        node = node.next
    return items


# Webpage 

queue_bp = Blueprint('queue_dq', __name__)
MAX_ITEMS = 12


def load_queue():
    queue = Queue()
    for value in session.get('queue_items', []):
        queue.enqueue(value)
    return queue


def save_queue(queue):
    session['queue_items'] = to_list(queue)


def parse_value(raw):
    try:
        return int(raw)
    except ValueError:
        return raw


def back(kind, message, hk=None):
    """Only errors are flashed; everything else just reloads the page."""
    if kind == 'error':
        flash(message, kind)
    return redirect(url_for('queue_dq.queue_dq_page', hk=hk))


def handle_basics():
    action = request.form.get('action', '')
    raw = request.form.get('value', '').strip()
    queue = load_queue()

    if action == 'enqueue':
        if raw == '':
            return back('error', 'Enter a value first.')
        if len(raw) > 20:
            return back('error', 'Please keep the value to 20 characters or fewer.')
        if len(to_list(queue)) >= MAX_ITEMS:
            return back('error', f'The demo queue holds up to {MAX_ITEMS} values. Dequeue one first.')
        value = parse_value(raw)
        queue.enqueue(value)
        save_queue(queue)
        return back('success', f'Added {value} to the rear of the queue.', hk='new')

    if action == 'dequeue':
        removed = queue.dequeue()
        if removed is None:
            return back('error', 'The queue is empty, so there is nothing to dequeue.')
        save_queue(queue)
        return back('success', f'Removed {removed} from the front of the queue.')

    if action == 'peek':
        front = queue.peek()
        if front is None:
            return back('error', 'The queue is empty, so there is nothing to peek at.')
        return back('success', f'The front value is {front}.', hk='peek')

    if action == 'sample':
        queue = Queue()
        for value in (10, 20, 30, 40, 50):
            queue.enqueue(value)
        save_queue(queue)
        return back('success', 'Loaded the sample: enqueued 10, then 20, then 30.')

    if action == 'clear':
        save_queue(Queue())             # save an EMPTY queue
        return back('success', 'The queue is now empty.')

    return back('error', 'Unknown action.')


# ---------------------------------------------------------------
# Deque section of the same page (all of its actions start with dq_)
# ---------------------------------------------------------------

def load_deque():
    dq = Deque()
    for value in session.get('deque_items', []):
        dq.add_rear(value)
    return dq


def save_deque(dq):
    session['deque_items'] = deque_to_list(dq)


def deque_back(kind, message, hk=None):
    """Only errors are flashed (category 'dq_error' so they appear inside the
    deque box, not the queue box). The anchor scrolls back to the deque section."""
    if kind == 'error':
        flash(message, 'dq_error')
    return redirect(url_for('queue_dq.queue_dq_page', hk=hk, _anchor='deque'))


def handle_deque():
    action = request.form.get('action', '')
    raw = request.form.get('value', '').strip()
    dq = load_deque()

    if action in ('dq_add_front', 'dq_add_rear'):
        if raw == '':
            return deque_back('error', 'Enter a value first.')
        if len(raw) > 20:
            return deque_back('error', 'Please keep the value to 20 characters or fewer.')
        if len(deque_to_list(dq)) >= MAX_ITEMS:
            return deque_back('error', f'The demo deque holds up to {MAX_ITEMS} values. Remove one first.')
        value = parse_value(raw)
        if action == 'dq_add_front':
            dq.add_front(value)
            save_deque(dq)
            return deque_back('success', f'Added {value} to the front of the deque.', hk='dq_new_front')
        dq.add_rear(value)
        save_deque(dq)
        return deque_back('success', f'Added {value} to the rear of the deque.', hk='dq_new_rear')

    if action == 'dq_remove_front':
        removed = dq.remove_front()
        if removed is None:
            return deque_back('error', 'The deque is empty, so there is nothing to remove.')
        save_deque(dq)
        return deque_back('success', f'Removed {removed} from the front of the deque.')

    if action == 'dq_remove_rear':
        removed = dq.remove_rear()
        if removed is None:
            return deque_back('error', 'The deque is empty, so there is nothing to remove.')
        save_deque(dq)
        return deque_back('success', f'Removed {removed} from the rear of the deque.')

    if action == 'dq_peek_front':
        value = dq.peek_front()
        if value is None:
            return deque_back('error', 'The deque is empty, so there is nothing to peek at.')
        return deque_back('success', f'The front value is {value}.', hk='dq_peek_front')

    if action == 'dq_peek_rear':
        value = dq.peek_rear()
        if value is None:
            return deque_back('error', 'The deque is empty, so there is nothing to peek at.')
        return deque_back('success', f'The rear value is {value}.', hk='dq_peek_rear')

    if action == 'dq_sample':
        dq = Deque()
        for value in (10, 20, 30, 40, 50):
            dq.add_rear(value)
        save_deque(dq)
        return deque_back('success', 'Loaded the sample: 10, 20, 30, 40, 50.')

    if action == 'dq_clear':
        save_deque(Deque())
        return deque_back('success', 'The deque is now empty.')

    return deque_back('error', 'Unknown action.')


@queue_bp.route('/works/queue_dq', methods=['GET', 'POST'])
def queue_dq_page():
    if request.method == 'POST':
        if request.form.get('action', '').startswith('dq_'):
            return handle_deque()
        return handle_basics()

    hk = request.args.get('hk')
    if hk not in ('new', 'peek', 'dq_new_front', 'dq_new_rear', 'dq_peek_front', 'dq_peek_rear'):
        hk = None

    ctx = {
        'hk': hk,
        'items': to_list(load_queue()),
        'deque_items': deque_to_list(load_deque()),
    }
    return render_template('queue_dq.html', **ctx)