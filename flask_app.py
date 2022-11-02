from flask import Flask, request, render_template, redirect, session, flash
from glob import iglob
from json import dump
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


if __name__ == '__main__':
    app.debug = True
    app.run()
