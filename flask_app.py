from flask import Flask, request, render_template, redirect, session, flash
from glob import iglob
from json import dump, load
from os import remove, rename
from os.path import exists
from pairs import Cohort

app = Flask(__name__)
app.secret_key = 'notreallyasecret'


def get_cohort_slugs():
    """Return a sorted list of all existing cohort slugs."""

    slugs = []

    for filename in iglob('./data/json/*.json'):
        filename = filename.split('/')
        slug = filename[-1].removesuffix('.json')
        slugs.append(slug)

    slugs.sort()
    return slugs


@app.route('/')
def index():
    """View the index."""

    cohorts = get_cohort_slugs()

    return render_template('index.html', cohorts=cohorts)


@app.route('/new', methods=['GET', 'POST'])
def new_cohort():
    """View and handle new cohort form."""

    if request.method == 'GET':
        return render_template('new.html')

    slug = request.form.get('slug', '').strip()

    if len(slug) < 1:
        flash('Cohort slug is required')
        return redirect('/new')
    if slug in get_cohort_slugs():
        flash(f'{slug} already exists.')
        return redirect(f'/cohorts/{slug}')

    students = request.form.get('students', '').strip().split()

    if len(students) < 4:
        flash('At least 4 students are required.')
        return redirect('/new')

    with open(f'./data/json/{slug}.json', 'w') as f:
        dump(students, f)

    cohort = Cohort(slug)
    cohort.save()

    return redirect(f'/cohorts/{slug}')


@app.route('/cohorts/<slug>')
def cohort_details(slug):
    """View cohort details page."""

    if slug not in get_cohort_slugs():
        flash('Cohort slug not found.')
        return redirect('/new')

    if exists(f'./data/pickle/{slug}.pickle'):
        cohort = Cohort.load(slug)
    else:
        cohort = Cohort(slug)
        cohort.save()

    num_students = len(cohort.roster)
    counts = cohort.get_count_matrix()

    return render_template('cohort.html', slug=slug, num_students=num_students, counts=counts)


@app.route('/cohorts/<slug>/delete')
def delete_cohort(slug):
    """Delete a cohort."""

    try:
        remove(f'./data/json/{slug}.json')
        remove(f'./data/pickle/{slug}.pickle')
    except FileNotFoundError as err:
        print(err)

    return redirect('/')


def update_cohort(slug, new_slug, to_remove, to_add):
    """Update a cohort and save."""

    if slug != new_slug:
        rename(f'./data/json/{slug}.json',
               f'./data/json/{new_slug}.json')
        rename(f'./data/pickle/{slug}.pickle',
               f'./data/pickle/{new_slug}.pickle')

    cohort = Cohort.load(new_slug)
    with open(f'./data/json/{new_slug}.json') as f:
        orig_json = load(f)
    orig_len = len(orig_json)

    for student in to_remove:
        cohort.remove_student(student)
        orig_json.remove(student)

    for student in to_add:
        cohort.add_student(student)
        orig_json.append(student)

    if len(orig_json) != orig_len:
        with open(f'./data/json/{new_slug}.json', 'w') as f:
            dump(orig_json, f)

    cohort.save()


@app.route('/cohorts/<slug>/edit', methods=['GET', 'POST'])
def edit_cohort(slug):
    """Edit a cohort."""

    if slug not in get_cohort_slugs():
        flash('Cohort slug not found.')
        return redirect('/new')

    if request.method == 'GET':
        if exists(f'./data/pickle/{slug}.pickle'):
            cohort = Cohort.load(slug)
        else:
            cohort = Cohort(slug)
            cohort.save()

        students = sorted(cohort.roster.keys())

        return render_template('edit.html', slug=slug, students=students)

    new_slug = request.form.get('slug', '').strip()

    if len(new_slug) < 1:
        flash('Cohort slug is required')
        return redirect(f'/cohorts/{slug}/edit')
    if new_slug in get_cohort_slugs():
        flash(f'{new_slug} already exists.')
        return redirect(f'/cohorts/{slug}/edit')

    students_to_remove = request.form.getlist('remove')

    new_students = request.form.get('students', '').strip().split()

    update_cohort(slug,
                  new_slug,
                  students_to_remove,
                  new_students)

    return redirect(f'/cohorts/{new_slug}')


def sort_2d_array(arr):
    """Sort each row, then sort by first colum."""

    for row in arr:
        row.sort()

    arr.sort()


@app.route('/api/generate', methods=['POST'])
def generate_pairs():
    """Generate cohort pairs and return JSON."""

    slug = request.json.get('slug')

    if slug is None or not exists(f'./data/pickle/{slug}.pickle'):
        return {'success': False, 'error': 'Cohort not found.'}

    cohort = Cohort.load(slug)
    absent = set(request.json.get('absent', []))
    pairs = cohort.generate_pairs(absent)
    cohort.save()
    sort_2d_array(pairs)
    new_counts = cohort.get_count_matrix()

    return {'success': True,
            'pairs': pairs,
            'new_counts': new_counts}


if __name__ == '__main__':
    app.debug = True
    app.run()
