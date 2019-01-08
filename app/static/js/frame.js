(function() {

  const POLLING_INTERVAL   = 20000;
  const SLIDESHOW_INTERVAL = 5000;
  const XHR_TIMEOUT        = 10000; 
  const ANIMATION_DURATION = 1000;
  
  let PHOTO_QUEUE   = [];
  let CURRENT_PHOTO = 0;

  console.log('Frame ID: ' + FRAME_ID);
  getPhotoList();
  window.setTimeout(nextPhoto, 5000);
  

  function getPhotoList(address) {
    let xhr = new XMLHttpRequest();
    let url = '/framephotos?id=' + FRAME_ID;
    xhr.onload = function() {
      if (xhr.status >= 200 && xhr.status < 300) {
        const json_response = JSON.parse(xhr.response);
        enqueuePhotos(json_response);
      } 
      else {
        console.log('Failed to get photo list');
      }
    };
    xhr.addEventListener('loadend', function() {
      window.setTimeout(getPhotoList, POLLING_INTERVAL);
    });
    xhr.open('GET', url);
    xhr.timeout = XHR_TIMEOUT;
    xhr.send(null);
  }

  function enqueuePhotos(photos) {
    photos.forEach((photo) => {
      if(!PHOTO_QUEUE.includes(photo)) {
        PHOTO_QUEUE.push(photo);
      }
    });
    PHOTO_QUEUE.forEach((photo) => {
      if(!photos.includes(photo)) {
        PHOTO_QUEUE.splice(PHOTO_QUEUE.indexOf(photo), 1);
      }
    })
    console.log('Photo queue: ' + PHOTO_QUEUE);
    updateImages();
  }

  function updateImages() {
    let imgs = document.querySelectorAll('#photos img');
    // add images until >= PHOTO_QUEUE.length
    while(imgs.length < PHOTO_QUEUE.length) {
      let new_img = document.createElement('img');
      new_img.style.display = 'none';
      imgs[0].parentNode.appendChild(new_img);
      imgs = document.querySelectorAll('#photos img');
    }
    // remove images until = PHOTO_QUEUE.length
    while(imgs.length != PHOTO_QUEUE.length) {
      imgs[imgs.length - 1].remove();
      imgs = document.querySelectorAll('#photos img');
    }
    for(let i=0; i<imgs.length; i++) {
      const src = `/framegetphoto?id=${FRAME_ID}&name=${PHOTO_QUEUE[i]}`
      imgs[i].setAttribute('src', src);
    }
    if(PHOTO_QUEUE.length === 0) show(document.getElementById('title'));
    else {
      hide(document.getElementById('title'));
      showCurrentPhoto();
    }
  }

  function nextPhoto() {
    console.log('Next photo')
    CURRENT_PHOTO ++;
    if(CURRENT_PHOTO > PHOTO_QUEUE.length - 1) {
      CURRENT_PHOTO = 0;
    }
    showCurrentPhoto();
    window.setTimeout(nextPhoto, SLIDESHOW_INTERVAL);
  }

  function showCurrentPhoto() {
    let imgs = document.querySelectorAll('#photos img');
    for(let img of imgs) {
      fadeOut(img);
      window.setTimeout( () => {
        hide(img);
      }, ANIMATION_DURATION);
    }
    window.setTimeout( () => {
      show(imgs[CURRENT_PHOTO])
      fadeIn(imgs[CURRENT_PHOTO]);
    }, ANIMATION_DURATION);
  }
  
  function fadeIn(elem) {
    elem.style.opacity = '1';
  }

  function fadeOut(elem) {
    elem.style.opacity = '0';
  }

  function hide(elem) {
    elem.style.display = 'none';
  }

  function show(elem) {
    elem.style.display = 'block';
  }

})();