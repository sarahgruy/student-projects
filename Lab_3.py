# Lab exercies 3: Linked List - starter file

# Keep every name exactly as written. A renamed class or method counts as a
# missing answer, even if the code inside it is correct.

# Put your own experiments inside the `if __name__ == "__main__":` block at the
# bottom. Code at the top level of this file runs when your work is marked, so
# a stray print() or input() up there will show up in your feedback.


import math
from flask import Blueprint, render_template, request, redirect, url_for, flash


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_at_beginning(self, data):
        new_node = Node(data)
        if self.head:
            new_node.next = self.head
            self.head = new_node
        else:
            self.head = new_node
            self.tail = new_node

    def insert_at_end(self, data):
        new_node = Node(data)
        if self.head:
            self.tail.next = new_node
            self.tail = new_node
        else:
            self.tail = new_node
            self.head = new_node

    def search(self, data):
        current_node = self.head
        while current_node:
            if current_node.data == data:
                return True
            current_node = current_node.next
        return False

    def printLinkedList(self):
        current_node = self.head
        while current_node:
            print(current_node.data)
            current_node = current_node.next

    # TODO a: remove the FIRST node and return its data (not the Node).
    # If the list is empty, return None.
    def remove_beginning(self):
        if self.head == None:
            return None
        else:
            remove_data = self.head.data
            self.head = self.head.next

        if self.head == None:
            self.tail = None

        return remove_data

    # TODO b: remove the LAST node and return its data (not the Node).
    # If the list is empty, return None.
    def remove_at_end(self):
        if self.tail == None:
            return None
        else:
            remove_data = self.tail.data

            if self.head == self.tail:
                self.head = None
                self.tail = None
            else:
                current_node = self.head

                while current_node.next != self.tail:
                    current_node = current_node.next
                self.tail = current_node
                self.tail.next = None

            return remove_data

    # TODO c: remove the first node holding `data` and return its data.
    # If no node holds `data`, return None and leave the list unchanged.
    def remove_at(self, data):
        if self.head == None:
            return None

        if self.head.data == data:
            return self.remove_beginning()

        current_node = self.head
        while current_node.next:
            if current_node.next.data == data:
                remove_data = current_node.next.data

                if current_node.next == self.tail:
                    self.tail = current_node
                current_node.next = current_node.next.next
                return remove_data

            current_node = current_node.next
        return None

    # TODO d: insert a new node holding `data` right after the first node
    # holding `nodedata`.
    # If no node holds `nodedata`, return None and leave the list unchanged.
    def insert_after(self, nodedata, data):
        current_node = self.head

        while current_node:
            if current_node.data == nodedata:
                new_node = Node(data)
                new_node.next = current_node.next
                current_node.next = new_node

                if current_node == self.tail:
                    self.tail = new_node
                return None

            current_node = current_node.next
        return None


# ---------- Web page for the linked list ----------

linked_bp = Blueprint('linked', __name__)

my_list = LinkedList()
history = []  # newest first: (kind, message)


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


def list_items():
    items = []
    node = my_list.head
    while node:
        items.append(node.data)
        node = node.next
    return items


def index_of(value):
    for i, item in enumerate(list_items()):
        if item == value:
            return i
    return None


def done(kind, message, hl=None, hk=None):
    """Remember the result, then redirect so a refresh doesn't repeat the action."""
    flash(message, kind)
    history.insert(0, (kind, message))
    del history[10:]
    return redirect(url_for('linked.linked_list', hl=hl, hk=hk))


@linked_bp.route('/works/linkedlist', methods=['GET', 'POST'])
def linked_list():
    global my_list

    if request.method == 'POST':
        action = request.form.get('action', '')
        raw = request.form.get('value', '').strip()
        raw_after = request.form.get('after', '').strip()

        needs_value = action in ('insert_beginning', 'insert_end',
                                 'insert_after', 'search', 'remove_at')
        if needs_value and raw == '':
            return done('error', 'Enter a value first.')
        value = parse_value(raw) if raw else None

        if action == 'insert_beginning':
            my_list.insert_at_beginning(value)
            return done('success', f'Inserted {value} at the beginning.', 0, 'new')

        if action == 'insert_end':
            my_list.insert_at_end(value)
            return done('success', f'Inserted {value} at the end.',
                        len(list_items()) - 1, 'new')

        if action == 'insert_after':
            if raw_after == '':
                return done('error', 'Enter the value to insert after.')
            after = parse_value(raw_after)
            pos = index_of(after)
            if pos is None:
                return done('error', f'{after} is not in the list, so nothing was inserted.')
            my_list.insert_after(after, value)
            return done('success', f'Inserted {value} after {after}.', pos + 1, 'new')

        if action == 'search':
            pos = index_of(value)
            if pos is None:
                return done('info', f'{value} is not in the list.')
            return done('success', f'Found {value} at position {pos}.', pos, 'found')

        if action == 'remove_beginning':
            removed = my_list.remove_beginning()
            if removed is None:
                return done('error', 'The list is already empty.')
            return done('success', f'Deleted {removed} from the beginning.')

        if action == 'remove_end':
            removed = my_list.remove_at_end()
            if removed is None:
                return done('error', 'The list is already empty.')
            return done('success', f'Deleted {removed} from the end.')

        if action == 'remove_at':
            removed = my_list.remove_at(value)
            if removed is None:
                return done('error', f'{value} is not in the list, so nothing was deleted.')
            return done('success', f'Deleted {removed} from the list.')

        if action == 'sample':
            my_list = LinkedList()
            for v in (10, 20, 30, 40):
                my_list.insert_at_end(v)
            return done('info', 'Loaded the sample list: 10, 20, 30, 40.')

        if action == 'clear':
            my_list = LinkedList()
            return done('info', 'The list is now empty.')

        return done('error', 'Unknown action.')

    hk = request.args.get('hk')
    if hk not in ('new', 'found'):
        hk = None
    items = list_items()
    return render_template('linkedlist.html', items=items, size=len(items),
                           history=history, hl=request.args.get('hl', type=int), hk=hk)


if __name__ == "__main__":
    ll = LinkedList()
    for value in [10, 20, 30]:
        ll.insert_at_end(value)
    ll.printLinkedList()