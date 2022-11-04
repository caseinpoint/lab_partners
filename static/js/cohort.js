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

    // check if cell was highlighted in updateCounts() and remove
    if (cell.checked) {
        cell.classList.remove('bg-light');
    }

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

    // replace previous highlighting from updateCounts(), if any
    if (cell.checked) {
        cell.classList.add('bg-light');
    }
};

for (let cell of document.querySelectorAll('.cell_count')) {
    cell.addEventListener('mouseenter', handleCellMouseenter);
    cell.addEventListener('mouseleave', handleCellMouseleave);
}


/* generating pairs: */
const updateCounts = (counts) => {
    for (let r = 1; r < counts.length; r++) {
        for (let c = 1; c < counts[r].length; c++) {
            const cell = document.querySelector(`#cell-${r}-${c}`);

            if (counts[r][c] !== null) {
                // highlight count changes from most recent groups
                if (cell.textContent != counts[r][c]) {
                    cell.classList.add('bg-light');
                    // cell.checked for removing/adding bg-light in mouseover
                    cell.checked = true;
                } else {
                    // remove previous highlighting, if any
                    cell.classList.remove('bg-light');
                    cell.checked = false;
                }

                cell.textContent = counts[r][c];
            } else {
                cell.textContent = '-';
            }
        }
    }
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