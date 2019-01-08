(function() {

  let range = [];

  const subnets = ["192.168.1.", "10.0.0."];

  subnets.forEach(subnet => {
    for (let i = 0; i < 256; i++) {
      range.push(subnet + i.toString());
    }
  });
  
  range.push('benjen.me'); // remove in prod
  
  remaining_addresses = range.slice();

  range.forEach(function(address) {
    probeDevice(address);
  });

  function probeDevice(address) {
  
    let xhr = new XMLHttpRequest();
  
    let url = 'http://' + address.toString() + ':8050/hello'; 
    console.log('probing ' + url);
  
    xhr.onload = function() {
  
      if (xhr.status >= 200 && xhr.status < 300) {
        console.log(xhr.response);
        if(xhr.response.split('@')[0] === 'magicframe') {
          let frameID = xhr.response.split('@')[1];
          console.log('Found frame with id ' + frameID + ' at ' + address);
          addFrameToList(address, frameID);
        }
      } 
      else {
        console.log('No frame found at ' + address);
      }
  
    };

    xhr.addEventListener('loadend', function() {
      remaining_addresses = remaining_addresses.filter(elem => elem != address);
      if(remaining_addresses.length === 0) {
        replaceSpinner();
      }
    });
  
    xhr.open('GET', url);
    xhr.timeout = 5000; // milliseconds
    xhr.send(null);
  
  }
  
  function addFrameToList(address, frameID) {
  
    let a = document.createElement('a');
    a.className = 'uk-margin-bottom uk-button uk-button-primary';
    a.innerHTML = 'Frame at ' + address;
    a.href = '/addframe?id=' + frameID;
  
    let framesList = document.getElementById('frames-list');
    framesList.appendChild(a);
  
  }

  function replaceSpinner() {
    let searching = document.getElementById('discovery-progress-label');
    searching.style.display = 'none'
    let spinner = document.getElementById('discovery-spinner');
    let message = document.createElement('a');
    message.href = '/notlisted';
    message.innerText = 'My frame isn\'t listed';
    spinner.parentNode.replaceChild(message, spinner);
  }

})();


