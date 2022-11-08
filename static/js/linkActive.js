for (let link of document.querySelectorAll('.nav-link')) {
    let pathname = window.location.pathname.replace('/edit', '');

    if (link.pathname === pathname) {
        link.classList.add('active');
        break;
    }
}