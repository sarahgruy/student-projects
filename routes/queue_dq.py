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


@queue_bp.route('/works/queue_dq', methods=['GET', 'POST'])
def queue_dq_page():
    if request.method == 'POST':
        return handle_basics()

    hk = request.args.get('hk')
    if hk not in ('new', 'peek'):
        hk = None

    ctx = {
        'hk': hk,
        'items': to_list(load_queue()),
    }
    return render_template('queue_dq.html', **ctx)