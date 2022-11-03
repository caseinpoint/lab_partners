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