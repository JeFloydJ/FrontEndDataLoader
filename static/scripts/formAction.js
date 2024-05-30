function setAction(action) {
    const form = document.getElementById('upload-form');
    if (action === 'upload') {
        form.action = '/upload';
    } else if (action === 'delete') {
        form.action = '/delete';
    }
}