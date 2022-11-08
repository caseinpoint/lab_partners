let pathname = window.location.pathname.replace('/edit', '');
for (let link of document.querySelectorAll('.nav-link')) {

    if (link.pathname === pathname) {
        link.classList.add('active');
        break;
    }
}