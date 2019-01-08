(function() {

  const uploadButton = document.getElementById('upload-button');
  const selectButton = document.getElementById('select-photos');
  const fileInput = document.getElementById('file-input');
  const photoElements = document.getElementsByClassName('photo-tile');
  const deleteButton = document.getElementById('delete-photos');
  let selectOverlays = document.getElementsByClassName('select-overlay');

  uploadButton.addEventListener('click', (event) => {
    event.preventDefault();
    const fileInput = document.getElementById('file-input');
    fileInput.click();
  });
  
  fileInput.addEventListener('change', (event) => {
    const form = document.getElementById('upload-form');
    form.submit();
  });

  selectButton.addEventListener('click', (event) => {
    deleteButton.classList.toggle('uk-hidden');
    for(let elem of photoElements) {
      let overlay = elem.querySelector('.select-overlay');
      overlay.classList.toggle('uk-hidden');
    }
  });

  for(let elem of photoElements) {
    elem.addEventListener('click', (event) => {
      let a = elem.querySelector('.photo-lightbox a');
      a.click();
    });
  }

  for(let elem of selectOverlays) {
    elem.addEventListener('click', (event) => {
      event.stopPropagation();
      event.target.classList.toggle('select-overlay-selected');
    })
  }

  deleteButton.addEventListener('click', (event) => {
    const selected = document.getElementsByClassName('select-overlay-selected');
    //console.log(selected);
    let files = [];
    for(let elem of selected) {
      //console.log(elem.getAttribute('data-filename'));
      filename = elem.getAttribute('data-filename');
      files.push(filename);
    }
    query = '/deletephotos?';
    for(let filename of files) {
      query += 'name=' + filename + '&';
    }
    console.log(query);
    let deleteForm = document.getElementById('delete-form');
    deleteForm.setAttribute('action', query);
    deleteForm.submit();
  });

})();