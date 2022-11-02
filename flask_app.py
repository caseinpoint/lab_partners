from flask import Flask, request, render_template, redirect, session, flash
from glob import iglob
from os.path import exists
from pairs import Cohort

app = Flask(__name__)
app.secret_key = 'notreallyasecret'


@app.route('/')
def index():
    """View the index."""

    cohorts = []

    for filename in iglob('./data/json/*.json'):
        filename = filename.split('/')
        slug = filename[-1].removesuffix('.json')

        if exists(f'./data/pickle/{slug}.pickle'):
            cohort = Cohort.load(slug)
        else:
            cohort = Cohort(slug)
            cohort.save()

        cohorts.append(cohort)

    return render_template('index.html', cohorts=cohorts)


if __name__ == '__main__':
    app.debug = True
    app.run()
