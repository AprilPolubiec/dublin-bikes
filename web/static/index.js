import { getAvailabilities, getCurrentWeather, getHourlyForecast, getStations } from './db_queries.js';
const DUBLIN_LATITUDE = 53.3498;
const DUBLIN_LONGITUDE = 6.2603;

function addDestinationAutocompleteInputs(dublinCoordinates, elId) {
  // https://developers.google.com/maps/documentation/javascript/place-autocomplete#javascript_5
  // Create a bounding box with sides ~10km away from the center point
  const defaultBounds = {
    north: dublinCoordinates.lat + 0.1,
    south: dublinCoordinates.lat - 0.1,
    east: dublinCoordinates.lng + 0.1,
    west: dublinCoordinates.lng - 0.1,
  };
  const start_input = document.getElementById(elId);
  const options = {
    bounds: defaultBounds,
    componentRestrictions: { country: 'ie' },
    // Fields: https://developers.google.com/maps/documentation/javascript/reference/places-service#PlaceResult
    fields: ['place_id', 'geometry'],
    // fields: ["address_components", "geometry", "icon", "name"],
    strictBounds: false,
  };
  return new google.maps.places.Autocomplete(start_input, options);
}

async function initMap() {
  const dublinCoordinates = { lat: DUBLIN_LATITUDE, lng: DUBLIN_LONGITUDE };
  const map = new google.maps.Map(document.getElementById('map'), {
    zoom: 6,
    center: dublinCoordinates,
  });
  const markerIcon = {
    url: 'web/static/bicycle-1054.png',
    scaledSize: new google.maps.Size(32, 32), // Icon size
    origin: new google.maps.Point(0, 0), // Icon origin
    anchor: new google.maps.Point(16, 32) // Anchor point
};

  var markerBounds = new google.maps.LatLngBounds();
  var markers = [];
  const stations = await getStations();

  const availabilities = await getAvailabilities();
  console.log(availabilities);
  const availabilityByStation = availabilities.reduce((acc, val) => {
    acc[val.StationId] = val;
    return acc;
  }, {});

  for (const station of stations) {
    const position = new google.maps.LatLng(parseFloat(station.PositionLatitude), parseFloat(station.PositionLongitude));
    
    // Define the marker icon
    const markerIcon = {
        url: 'your_image_url.png', // Replace 'your_image_url.png' with the URL of your custom marker image
        scaledSize: new google.maps.Size(40, 40) // Adjust the size if needed
    };

    // Create the marker with custom icon
    const marker = new google.maps.Marker({
        position: position,
        map: map,
        icon: markerIcon,
        title: station.Name,
        fillColor: '#99ff33', // This property doesn't directly affect the marker, you may remove it if unnecessary
    });

    // Push the marker to an array if needed
    markers.push(marker);
    markers.push(marker);

    const availability = availabilityByStation[station.Id];
    const contentString = '<div class="infowindow-content">' + `<p><b>Availability: </b> ${availability.ElectricBikesAvailable + availability.MechanicalBikesAvailable}` + '</div>';
    const infowindow = new google.maps.InfoWindow({
      content: contentString,
      ariaLabel: station.Name,
    });

    marker.addListener('click', () => {
      infowindow.open({
        anchor: marker,
        map,
      });
    });
    markerBounds.extend(position);
  }
  map.fitBounds(markerBounds);
  
  const directionsService = new google.maps.DirectionsService();
  const markerCluster = new markerClusterer.MarkerClusterer({ markers, map });

  const backButton = document.getElementById('back-button');
  const resultsEl = document.getElementById("results");
  const formEl = document.getElementById("search-form");

  backButton.addEventListener('click', () => {
    resultsEl.style.display = 'none';
    formEl.style.display = 'block';
    for (const marker of markers) {
      marker.setMap(map);
    }
    markerCluster.addMarkers(markers);
  })

  document.getElementById('search-form').onsubmit = (e) => {
    getDirections(e, directionsService, map, stations, start_location, end_location)
    for (const marker of markers) {
      marker.setMap(null);
    }
    markerCluster.clearMarkers();
  };

  renderCurrentWeather();
}

async function renderCurrentWeather() {
  const response = await getCurrentWeather(DUBLIN_LATITUDE, DUBLIN_LONGITUDE * -1);
  const currentWeather = response['weather'][0];
  const { description, icon } = currentWeather;
  const { temp } = response['main'];
  const iconUrl = `https://openweathermap.org/img/wn/${icon}.png`;
  const weatherEl = document.getElementById('current-weather');
  const descriptionEl = document.createElement('li');
  descriptionEl.innerText = description;

  const iconEl = document.createElement('img');
  iconEl.src = iconUrl;

  const tempEl = document.createElement('li');
  tempEl.innerText = `${Math.round(temp)}°`;

  weatherEl.append(iconEl, tempEl);


  const hourlyForecastResponse = await getHourlyForecast(DUBLIN_LATITUDE, DUBLIN_LONGITUDE * -1);
  let today = new Date();
  const dateString = today.toISOString().split('T')[0];
  const todaysForecast = hourlyForecastResponse['list'].filter((f) => f['dt_txt'].includes(dateString));
  const weatherDetailsEl = document.getElementById('weather-details');
  const weatherDetailsContainerEl = weatherDetailsEl.children[0];
  
  todaysForecast.forEach((forecast) => {
    const containerEl = document.createElement('div');
    containerEl.className = "weather-details-el";
    const timeEl = document.createElement('small');
    timeEl.className = "forecast-time";
    const date = new Date(forecast['dt_txt']);
    const hour = date.getHours();
    timeEl.innerText = hour > 12 ? `${hour - 12}pm` : `${hour}am`;
  
    const iconEl = document.createElement('img');
    const { icon, description } = forecast['weather'][0];
    iconEl.src = `https://openweathermap.org/img/wn/${icon}.png`;

    const tempEl = document.createElement('div');
    const { temp } = forecast['main'];
    tempEl.innerText = `${Math.round(temp)}°`;
    containerEl.append(timeEl, iconEl, tempEl);
    weatherDetailsContainerEl.append(containerEl);
  });

  weatherEl.addEventListener('click', () => {
    const currentVisibility = weatherDetailsEl.style.visibility;
    weatherDetailsEl.style.visibility = currentVisibility == 'visible' ? 'hidden' : 'visible';
  })
}

function getClosestStation(placeGeometry, stations) {
  let closestDistance = google.maps.geometry.spherical.computeDistanceBetween({ lat: parseFloat(stations[0].PositionLatitude), lng: parseFloat(stations[0].PositionLongitude) }, placeGeometry);
  let closestStation = stations[0];
  for (const station of stations) {
    const lng = parseFloat(station.PositionLongitude);
    const lat = parseFloat(station.PositionLatitude);
    const distance = google.maps.geometry.spherical.computeDistanceBetween({ lat, lng }, placeGeometry);
    if (distance < closestDistance) {
      closestDistance = distance;
      closestStation = station;
    }
  }

  return { lat: parseFloat(closestStation.PositionLatitude), lng: parseFloat(closestStation.PositionLongitude) };
}

// https://developers.google.com/maps/documentation/javascript/examples/places-autocomplete-directions
function getDirections(e, directionsService, map, stations, start_location, end_location) {
  e.preventDefault();
  console.log(e, start_location, end_location);
  const start_place = start_location.getPlace();
  const end_place = end_location.getPlace();
  //  TODO: make these take over the entire nav and add a back button to go back to the search
  const closest_start_station = getClosestStation(start_place.geometry.location, stations);
  const closest_end_station = getClosestStation(end_place.geometry.location, stations);
  // const closest_start_station = {lat: parseFloat(stations[0].PositionLatitude), lng: parseFloat(stations[0].PositionLongitude)}
  // const closest_end_station = {lat: parseFloat(stations[1].PositionLatitude), lng: parseFloat(stations[1].PositionLongitude)}
  // Get walking directions from start location to the start station
  const firstLegRenderer = new google.maps.DirectionsRenderer({
    map: map,
    preserveViewport: true,
    // suppressMarkers: true,
    polylineOptions: {
      strokeColor: 'red',
    },
  });
  firstLegRenderer.setPanel(document.getElementById('leg1Panel'));
  directionsService.route(
    {
      origin: { placeId: start_place.place_id },
      destination: closest_start_station,
      travelMode: google.maps.TravelMode.WALKING,
    },
    (response, status) => {
      if (status === 'OK') {
        firstLegRenderer.setDirections(response);
      } else {
        window.alert('Directions request failed due to ' + status);
      }
    }
  );

  // Get bike directions from start station to end station
  const secondLegRenderer = new google.maps.DirectionsRenderer(
    new google.maps.DirectionsRenderer({
      map: map,
      preserveViewport: true,
      // suppressMarkers: true,
      polylineOptions: {
        strokeColor: 'blue',
      },
    })
  );
  secondLegRenderer.setPanel(document.getElementById('leg2Panel'));
  directionsService.route(
    {
      origin: closest_start_station,
      destination: closest_end_station,
      travelMode: google.maps.TravelMode.BICYCLING,
    },
    (response, status) => {
      if (status === 'OK') {
        secondLegRenderer.setDirections(response);
      } else {
        window.alert('Directions request failed due to ' + status);
      }
    }
  );

  // Get walking directions from end station to destination
  const thirdLegRenderer = new google.maps.DirectionsRenderer(
    new google.maps.DirectionsRenderer({
      map: map,
      preserveViewport: true,
      // suppressMarkers: true,
      polylineOptions: {
        strokeColor: 'red',
      },
    })
  );
  thirdLegRenderer.setPanel(document.getElementById('leg3Panel'));
  directionsService.route(
    {
      origin: closest_end_station,
      destination: { placeId: end_place.place_id },
      travelMode: google.maps.TravelMode.WALKING,
    },
    (response, status) => {
      if (status === 'OK') {
        thirdLegRenderer.setDirections(response);
      } else {
        window.alert('Directions request failed due to ' + status);
      }
    }
  );

  const resultsEl = document.getElementById("results");
  resultsEl.style.display = 'block';
  const formEl = document.getElementById("search-form");
  formEl.style.display = 'none';
}

window.initMap = initMap;
