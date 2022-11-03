/* cell highlighting: */
const getCellHeaders = (cell) => {
    const coords = cell.id.split('-');
    const r = coords[1];
    const c = coords[2];

    const colHeaderCell = document.querySelector(`#cell-0-${c}`);
    const rowHeaderCell = document.querySelector(`#cell-${r}-0`);

    return {colHeaderCell, rowHeaderCell};
};

const handleCellMouseenter = (evt) => {
    const cell = evt.target

    const {colHeaderCell, rowHeaderCell} = getCellHeaders(cell);

    cell.classList.add('bg-warning');
    colHeaderCell.classList.add('bg-warning');
    rowHeaderCell.classList.add('bg-warning');
};

const handleCellMouseleave = (evt) => {
    const cell = evt.target

    const {colHeaderCell, rowHeaderCell} = getCellHeaders(cell);

    cell.classList.remove('bg-warning');
    colHeaderCell.classList.remove('bg-warning');
    rowHeaderCell.classList.remove('bg-warning');
};

for (let cell of document.querySelectorAll('.cell_count')) {
    cell.addEventListener('mouseenter', handleCellMouseenter);
    cell.addEventListener('mouseleave', handleCellMouseleave);
}


/* generating pairs: */
const updateCounts = (counts) => {
    console.log(counts);
    // TODO: implement
};

const handleFormGenerate = (evt) => {
    evt.preventDefault();

    const inputs = {absent: []};
    for (let checkbox of document.querySelectorAll('.absent')) {
        if (checkbox.checked) {
            inputs.absent.push(checkbox.value);
        }
    }

    inputs.slug = document.querySelector('#slug').value;

    fetch('/api/generate', {
        method: 'POST',
        body: JSON.stringify(inputs),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then((res) => res.json())
    .then((data) => {
        const resultsUL = document.querySelector('#pair_results');
        resultsUL.innerHTML = '';

        for (let pair of data.pairs) {
            pairString = pair.join(' & ');
            resultsUL.insertAdjacentHTML('beforeend',
                                         `<li>${pairString}</li>`);
        }

        updateCounts(data.new_counts);
    });
};

const formGenerate = document.querySelector('#form_generate');
formGenerate.addEventListener('submit', handleFormGenerate);