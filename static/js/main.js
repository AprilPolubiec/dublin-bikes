const DUBLIN_LATITUDE = 53.3498;
const DUBLIN_LONGITUDE = -6.2603;
  function initMap() {
    // Get our station data - can pull from the local cache

    fetch('/stations')
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Now you can use the JSON data in your JavaScript code
        console.log(data);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });

    const dublinCoordinates = { lat: DUBLIN_LATITUDE, lng: DUBLIN_LONGITUDE };
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 4,
        center: dublinCoordinates,
    });

    new google.maps.Marker({
        position: dublinCoordinates,
        map,
        title: "Hello World!",
    });
  }

  window.initMap = initMap;