from flask import Flask, request, render_template, redirect, session, flash
from glob import iglob
from json import dump
from os import remove
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

    new_counts = cohort.get_count_matrix()

    return {
        'success': True,
        'pairs': pairs,
        'new_counts': new_counts
    }


if __name__ == '__main__':
    app.debug = True
    app.run()
