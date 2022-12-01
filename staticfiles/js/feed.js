function ShareButton(parent_id) {
    const row = document.getElementById(parent_id);

    if (row.classList.contains('d-share')){
        row.classList.remove('d-share');
    }
    else {
        row.classList.add('d-share');
    }
}