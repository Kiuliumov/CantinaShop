  function toggleEdit(id) {
    const content = document.getElementById(`comment-content-${id}`);
    const form = document.getElementById(`edit-form-${id}`);
    if (form.classList.contains('hidden')) {
      form.classList.remove('hidden');
      content.classList.add('hidden');
    } else {
      form.classList.add('hidden');
      content.classList.remove('hidden');
    }
  }
