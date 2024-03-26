const SLUG = document.querySelector('#slug').value;

const getHeaderCells = (cell) => {
    const coords = cell.id.split('-');
    const r = coords[1];
    const c = coords[2];
    
    const colHeaderCell = document.querySelector(`#cell-0-${c}`);
    const rowHeaderCell = document.querySelector(`#cell-${r}-0`);
    
    return {colHeaderCell, rowHeaderCell};
};

const updateCounts = (counts) => {
    for (let r = 1; r < counts.length; r++) {
        for (let c = 1; c < counts[r].length; c++) {
            const cell = document.querySelector(`#cell-${r}-${c}`);

            if (counts[r][c] !== null) {
                // highlight count changes from most recent groups
                if (cell.textContent != counts[r][c]) {
                    cell.classList.add('bg-light');
                    // for removing/adding bg-light in mouseover
                    cell.dataset.highlight = 'true';
                } else {
                    // remove previous highlighting, if any
                    cell.classList.remove('bg-light');
                    cell.dataset.highlight = 'false';
                }

                cell.textContent = counts[r][c];
                cell.dataset.count = counts[r][c];
            } else {
                cell.textContent = '-';
            }
        }
    }
};

/* manual count editing */
const handleKeyPress = (evt) => {
    if (evt.key === 'Escape') {
        const input = evt.target;
        const parentTd = document.getElementById(input.dataset.cellId);
        parentTd.innerHTML = '';
        parentTd.textContent = parentTd.dataset.count;
    }
};

const handleEditCount = (evt) => {
    evt.preventDefault();

    const form = evt.target;
    const parentTd = document.getElementById(form.dataset.cellId);

    const inputs = {slug: SLUG};

    for (let input of form.querySelectorAll('input')) {
        inputs[input.name] = input.value;
    }

    handleKeyPress({key: 'Escape', target: form});

    if (inputs.count !== parentTd.dataset.count) {
        fetch('/api/update-count', {
            method: 'POST',
            body: JSON.stringify(inputs),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then((res) => res.json())
        .then((data) => {
            updateCounts(data.new_counts);
        });
    }
};

const handleDblclick = (evt) => {
    const cell = evt.target;
    const {colHeaderCell, rowHeaderCell} = getHeaderCells(cell);
    cell.innerHTML = '';

    const inputCount = document.createElement('input');
    inputCount.name = 'count';
    inputCount.value = cell.dataset.count;
    inputCount.dataset.cellId = cell.id;
    inputCount.type = 'number';
    inputCount.required = true;
    inputCount.classList.add('form-control');
    inputCount.onkeydown = handleKeyPress;

    const inputStudent1 = document.createElement('input');
    inputStudent1.name = 'student1';
    inputStudent1.value = rowHeaderCell.dataset.student;
    inputStudent1.type = 'hidden';

    const inputStudent2 = document.createElement('input');
    inputStudent2.name = 'student2';
    inputStudent2.value = colHeaderCell.dataset.student;
    inputStudent2.type = 'hidden';

    const newForm = document.createElement('form');
    newForm.dataset.cellId = cell.id;
    newForm.appendChild(inputCount);
    newForm.appendChild(inputStudent1);
    newForm.appendChild(inputStudent2);
    newForm.onsubmit = handleEditCount;

    cell.appendChild(newForm);
    inputCount.focus();
};

/* cell highlighting: */
const handleCellMouseenter = (evt) => {
    const cell = evt.target

    const {colHeaderCell, rowHeaderCell} = getHeaderCells(cell);

    // check if cell was highlighted in updateCounts() and remove
    if (cell.dataset.highlight === 'true') {
        cell.classList.remove('bg-light');
    }

    cell.classList.add('bg-warning');
    colHeaderCell.classList.add('bg-warning');
    rowHeaderCell.classList.add('bg-warning');
};

const handleCellMouseleave = (evt) => {
    const cell = evt.target

    const {colHeaderCell, rowHeaderCell} = getHeaderCells(cell);

    cell.classList.remove('bg-warning');
    colHeaderCell.classList.remove('bg-warning');
    rowHeaderCell.classList.remove('bg-warning');

    // replace previous highlighting from updateCounts(), if any
    if (cell.dataset.highlight === 'true') {
        cell.classList.add('bg-light');
    }
};

/* generating pairs: */
const handleFormGenerate = (evt) => {
    evt.preventDefault();
    
    const inputs = {absent: []};
    for (let checkbox of document.querySelectorAll('.absent')) {
        if (checkbox.checked) {
            inputs.absent.push(checkbox.value);
        }
    }
    
    inputs.slug = SLUG;
    
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
        
        if (!data.success) {
            resultsUL.insertAdjacentHTML('beforeend',
            `<li>error: ${data.error}</li>`);
        } else {
            for (let pair of data.pairs) {
                pairString = pair.join(' & ');
                resultsUL.insertAdjacentHTML('beforeend',
                `<li>${pairString}</li>`);
            }
            
            updateCounts(data.new_counts);
        }
    });
};


for (let cell of document.querySelectorAll('.cell_count')) {
    cell.addEventListener('mouseenter', handleCellMouseenter);
    cell.addEventListener('mouseleave', handleCellMouseleave);
    if (cell.dataset.count !== '-') {
        cell.addEventListener('dblclick', handleDblclick);
    }
}

const formGenerate = document.querySelector('#form_generate');
formGenerate.addEventListener('submit', handleFormGenerate);
