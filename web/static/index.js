import { getAvailabilities, getStations } from './db_queries.js';

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
      componentRestrictions: { country: "ie" },
      // Fields: https://developers.google.com/maps/documentation/javascript/reference/places-service#PlaceResult
      fields: ["place_id", "geometry"],
      // fields: ["address_components", "geometry", "icon", "name"],
      strictBounds: false,
    };
    return new google.maps.places.Autocomplete(start_input, options);
}

async function initMap() {
    const dublinCoordinates = { lat: DUBLIN_LATITUDE, lng: DUBLIN_LONGITUDE };
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 6,
        center: dublinCoordinates,
    });

    const start_location = addDestinationAutocompleteInputs(dublinCoordinates, "start-location")
    const end_location = addDestinationAutocompleteInputs(dublinCoordinates, "end-location")
  
    var markerBounds = new google.maps.LatLngBounds();
    const stations = await getStations();
    const availabilities = await getAvailabilities();
    console.log(availabilities)
    const availabilityByStation = availabilities.reduce((acc, val) => {
      acc[val.StationId] = val;
      return acc;
    }, {})

    for (const station of stations) {
        const position = new google.maps.LatLng(parseFloat(station.PositionLatitude), parseFloat(station.PositionLongitude))

        const marker = new google.maps.Marker({
            position,
            map,
            title: station.Name,
            fillColor: "#99ff33"
        });
        const availability = availabilityByStation[station.Id];
        const contentString =
            '<div class="infowindow-content">' +
            `<p><b>Availability: </b> ${availability.ElectricBikesAvailable + availability.MechanicalBikesAvailable}` +
            "</div>";
      const infowindow = new google.maps.InfoWindow({
        content: contentString,
        ariaLabel: station.Name,
      });

      marker.addListener("click", () => {
        infowindow.open({
          anchor: marker,
          map,
        });
      });
      markerBounds.extend(position)
    }
    map.fitBounds(markerBounds);
    const directionsService = new google.maps.DirectionsService();
    document.getElementById("search-form").onsubmit = (e) => getDirections(e, directionsService, map, stations, start_location, end_location)

}

function getClosestStation(placeGeometry, stations) {
  let closestDistance = google.maps.geometry.spherical.computeDistanceBetween({lat: parseFloat(stations[0].PositionLatitude), lng: parseFloat(stations[0].PositionLongitude)}, placeGeometry);
  let closestStation = stations[0];
  for (const station of stations) {
    const lng = parseFloat(station.PositionLongitude)
    const lat = parseFloat(station.PositionLatitude)
    const distance = google.maps.geometry.spherical.computeDistanceBetween({lat, lng}, placeGeometry)
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
  console.log(e, start_location, end_location)
  const start_place = start_location.getPlace();
  const end_place = end_location.getPlace();
//  TODO: make these take over the entire nav and add a back button to go back to the search
  const closest_start_station = getClosestStation(start_place.geometry.location, stations)
  const closest_end_station = getClosestStation(end_place.geometry.location, stations)
  // const closest_start_station = {lat: parseFloat(stations[0].PositionLatitude), lng: parseFloat(stations[0].PositionLongitude)}
  // const closest_end_station = {lat: parseFloat(stations[1].PositionLatitude), lng: parseFloat(stations[1].PositionLongitude)}
  // Get walking directions from start location to the start station
  const firstLegRenderer = new google.maps.DirectionsRenderer( {
    map: map,
    preserveViewport: true,
    // suppressMarkers: true,
    polylineOptions: {
      strokeColor: 'red'
    }});
  firstLegRenderer.setPanel(document.getElementById('leg1Panel'));
  directionsService.route(
    {
      origin: { placeId: start_place.place_id},
      destination: closest_start_station,
      travelMode: google.maps.TravelMode.WALKING,
    },
    (response, status) => {
      if (status === "OK") {
        firstLegRenderer.setDirections(response);
      } else {
        window.alert("Directions request failed due to " + status);
      }
    },
  );

  // Get bike directions from start station to end station
  const secondLegRenderer = new google.maps.DirectionsRenderer(new google.maps.DirectionsRenderer( {
    map: map,
    preserveViewport: true,
    // suppressMarkers: true,
    polylineOptions: {
      strokeColor: 'blue'
    }}));
    secondLegRenderer.setPanel(document.getElementById('leg2Panel'));
  directionsService.route(
    {
      origin: closest_start_station,
      destination: closest_end_station,
      travelMode: google.maps.TravelMode.BICYCLING,
    },
    (response, status) => {
      if (status === "OK") {
        secondLegRenderer.setDirections(response);
      } else {
        window.alert("Directions request failed due to " + status);
      }
    },
  );

  // Get walking directions from end station to destination
  const thirdLegRenderer = new google.maps.DirectionsRenderer(new google.maps.DirectionsRenderer( {
    map: map,
    preserveViewport: true,
    // suppressMarkers: true,
    polylineOptions: {
      strokeColor: 'red'
    }}));
    thirdLegRenderer.setPanel(document.getElementById('leg3Panel'));
  directionsService.route(
    {
      origin: closest_end_station,
      destination: { placeId: end_place.place_id },
      travelMode: google.maps.TravelMode.WALKING,
    },
    (response, status) => {
      if (status === "OK") {
        thirdLegRenderer.setDirections(response);
      } else {
        window.alert("Directions request failed due to " + status);
      }
    },
  );

  console.log(start_place, end_place)
}

window.initMap = initMap;
