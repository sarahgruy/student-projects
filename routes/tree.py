from flask import Blueprint, render_template, request, redirect, url_for, flash, session


class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


class BinaryTree:
    """A general binary tree: you choose which parent each new node goes under."""

    def __init__(self, root_data=None):
        self.root = Node(root_data) if root_data is not None else None

    def insert_left(self, parent, data):
        parent.left = Node(data)
        return parent.left

    def insert_right(self, parent, data):
        parent.right = Node(data)
        return parent.right

    def search(self, root, key):
        # The tree is not ordered, so look at the node, then its left side, then its right side
        if root is None or root.data == key:
            return root
        found = self.search(root.left, key)
        if found is not None:
            return found
        return self.search(root.right, key)

    def pre_traversal(self, start, traversal):
        if start:
            traversal.append(start.data)
            self.pre_traversal(start.left, traversal)
            self.pre_traversal(start.right, traversal)
        return traversal

    def in_traversal(self, start, traversal):
        if start:
            self.in_traversal(start.left, traversal)
            traversal.append(start.data)
            self.in_traversal(start.right, traversal)
        return traversal

    def post_traversal(self, start, traversal):
        if start:
            self.post_traversal(start.left, traversal)
            self.post_traversal(start.right, traversal)
            traversal.append(start.data)
        return traversal

    def delete_node(self, root, key):
        """Remove the node holding key together with everything below it.
        Returns the new root of this subtree (None if the node itself was removed)."""
        if root is None:
            return None
        if root.data == key:
            return None
        root.left = self.delete_node(root.left, key)
        root.right = self.delete_node(root.right, key)
        return root

    def height(self, root):
        if root is None:
            return 0
        return 1 + max(self.height(root.left), self.height(root.right))

    def count(self, root):
        if root is None:
            return 0
        return 1 + self.count(root.left) + self.count(root.right)


# Webpage

tree_bp = Blueprint('binary_tree', __name__)
MAX_NODES = 15
MAX_LEN = 10
TRAVERSALS = {'pre': 'Pre-order', 'in': 'In-order', 'post': 'Post-order'}

# Drawing sizes (pixels) for the SVG picture of the tree
NODE_H, Y_GAP, PAD_Y, PAD_X = 40, 70, 30, 24


def node_to_dict(node):
    if node is None:
        return None
    return {'v': node.data, 'l': node_to_dict(node.left), 'r': node_to_dict(node.right)}


def dict_to_node(d):
    if not d:
        return None
    node = Node(d['v'])
    node.left = dict_to_node(d.get('l'))
    node.right = dict_to_node(d.get('r'))
    return node


def load_tree():
    tree = BinaryTree()
    tree.root = dict_to_node(session.get('btree'))
    return tree


def save_tree(tree):
    session['btree'] = node_to_dict(tree.root)


def back(kind, message, **params):
    """Errors and search/delete results are flashed; everything else just reloads the page."""
    if message:
        flash(message, kind)
    return redirect(url_for('binary_tree.tree_page', **params))


def build_drawing(tree, hk, key):
    """Work out where every node and line goes so the template only has to print them."""
    labels = tree.in_traversal(tree.root, [])
    node_w = max([40] + [len(str(v)) * 11 + 18 for v in labels])   # wider boxes for longer words
    x_gap = node_w + 16
    nodes, edges = [], []
    counter = [0]

    def walk(node, depth):
        if node is None:
            return None
        left = walk(node.left, depth + 1)
        col = counter[0]                 # in-order position gives the x spacing
        counter[0] += 1
        me = {
            'data': node.data,
            'x': PAD_X + node_w / 2 + col * x_gap,
            'y': PAD_Y + depth * Y_GAP,
            'state': hk if key == node.data and hk in ('new', 'found') else '',
        }
        right = walk(node.right, depth + 1)
        nodes.append(me)
        for child in (left, right):
            if child:
                edges.append({'x1': me['x'], 'y1': me['y'], 'x2': child['x'], 'y2': child['y']})
        return me

    walk(tree.root, 0)
    height = tree.height(tree.root)
    return {
        'nodes': nodes,
        'edges': edges,
        'w': node_w,
        'h': NODE_H,
        'half_w': node_w / 2,
        'half_h': NODE_H / 2,
        'width': PAD_X * 2 + node_w + max(len(nodes) - 1, 0) * x_gap,
        'height': PAD_Y * 2 + max(height - 1, 0) * Y_GAP,
    }


def handle_basics():
    action = request.form.get('action', '')
    raw = request.form.get('value', '').strip()
    parent_raw = request.form.get('parent', '').strip()
    tree = load_tree()

    if action in ('set_root', 'insert_left', 'insert_right', 'delete', 'search'):
        if raw == '':
            return back('error', 'Enter a value first.')
        if len(raw) > MAX_LEN:
            return back('error', f'Please keep the value to {MAX_LEN} characters or fewer.')

        if action == 'set_root':
            if tree.root is not None:
                return back('error', 'The root is already set. Delete it first to set a new one.')
            tree.root = Node(raw)
            save_tree(tree)
            return back('success', None, hk='new', k=raw)

        if action in ('insert_left', 'insert_right'):
            side = 'left' if action == 'insert_left' else 'right'
            if tree.root is None:
                return back('error', 'Set the root first.')
            if parent_raw == '':
                return back('error', 'Enter the parent (an existing node) first.')
            parent = tree.search(tree.root, parent_raw)
            if parent is None:
                return back('error', f'The parent "{parent_raw}" is not in the tree.')
            if tree.search(tree.root, raw) is not None:
                return back('error', f'"{raw}" is already in the tree. Each value can only appear once.')
            if tree.count(tree.root) >= MAX_NODES:
                return back('error', f'The demo tree holds up to {MAX_NODES} values. Delete one first.')
            existing = parent.left if side == 'left' else parent.right
            if existing is not None:
                return back('error', f'"{parent_raw}" already has a {side} child ("{existing.data}"). Delete it first.')
            if side == 'left':
                tree.insert_left(parent, raw)
            else:
                tree.insert_right(parent, raw)
            save_tree(tree)
            return back('success', None, hk='new', k=raw)

        if action == 'delete':
            if tree.search(tree.root, raw) is None:
                return back('error', f'"{raw}" is not in the tree, so it cannot be deleted.')
            before = tree.count(tree.root)
            tree.root = tree.delete_node(tree.root, raw)
            removed = before - tree.count(tree.root)
            save_tree(tree)
            msg = f'Deleted "{raw}"'
            if removed > 1:
                msg += f' and the {removed - 1} node{"s" if removed > 2 else ""} below it'
            return back('success', msg + '.')

        # search
        if tree.search(tree.root, raw) is None:
            return back('error', f'"{raw}" was not found in the tree.')
        return back('success', f'Found "{raw}" in the tree.', hk='found', k=raw)

    if action in TRAVERSALS:
        if tree.root is None:
            return back('error', 'The tree is empty, so there is nothing to traverse.')
        return back('success', None, trav=action)

    if action == 'sample':
        # the tree from the lesson picture
        tree = BinaryTree("R")
        a = tree.insert_left(tree.root, "A")
        b = tree.insert_right(tree.root, "B")
        tree.insert_left(a, "C")
        tree.insert_right(a, "D")
        tree.insert_left(b, "E")
        f = tree.insert_right(b, "F")
        tree.insert_left(f, "G")
        save_tree(tree)
        return back('success', None)

    if action == 'clear':
        save_tree(BinaryTree())          # save an EMPTY tree (the Set Root button turns on again)
        return back('success', None)

    return back('error', 'Unknown action.')


@tree_bp.route('/works/binary_tree', methods=['GET', 'POST'])
def tree_page():
    if request.method == 'POST':
        return handle_basics()

    hk = request.args.get('hk')
    if hk not in ('new', 'found'):
        hk = None
    key = request.args.get('k')

    trav = request.args.get('trav')
    if trav not in TRAVERSALS:
        trav = None

    tree = load_tree()
    traversal = None
    if trav == 'pre':
        traversal = tree.pre_traversal(tree.root, [])
    elif trav == 'in':
        traversal = tree.in_traversal(tree.root, [])
    elif trav == 'post':
        traversal = tree.post_traversal(tree.root, [])

    ctx = {
        'size': tree.count(tree.root),
        'height': tree.height(tree.root),
        'root_value': tree.root.data if tree.root else None,
        'drawing': build_drawing(tree, hk, key),
        'trav_name': TRAVERSALS.get(trav),
        'traversal': traversal,
    }
    return render_template('binary_tree.html', **ctx)