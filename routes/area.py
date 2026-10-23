import math
from flask import Blueprint, render_template, request

area_bp = Blueprint('area', __name__)

# key: (title, [(input name, label), ...])
SHAPES = {
    'circle':    ('Circle',    [('radius', 'Radius')]),
    'square':    ('Square',    [('side', 'Side')]),
    'triangle':  ('Triangle',  [('base', 'Base'), ('height', 'Height')]),
    'rectangle': ('Rectangle', [('length', 'Length'), ('width', 'Width')]),
}


def get_number(name):
    """Read a positive number from the form, or raise ValueError."""
    value = float(request.form.get(name, ''))
    if value <= 0:
        raise ValueError
    return value


def calculate(shape):
    if shape == 'circle':
        return math.pi * get_number('radius') ** 2
    if shape == 'triangle':
        return get_number('base') * get_number('height') / 2
    if shape == 'square':
        return get_number('side') ** 2
    if shape == 'rectangle':
        return get_number('length') * get_number('width')
    raise KeyError


@area_bp.route('/works/area', methods=['GET', 'POST'])
def area_page():
    shape, result, error = None, None, None

    if request.method == 'POST':
        shape = request.form.get('shape')
        try:
            result = round(calculate(shape), 2)
        except ValueError:
            error = 'Enter a number greater than 0 in every box.'
        except KeyError:
            error = 'Unknown shape.'

    return render_template('area.html', shapes=SHAPES, shape=shape,
                           result=result, error=error, values=request.form)