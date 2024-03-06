import { getStations } from './db_queries.js';

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
      fields: ["place_id"],
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
    for (const station of stations) {
        const position = new google.maps.LatLng(parseFloat(station.PositionLatitude), parseFloat(station.PositionLongitude))
        const marker = new google.maps.Marker({
            position,
            map,
            title: station.Name,
        });

        const contentString =
            '<div class="infowindow-content">' +
            "<p><b>Availability: </b> 0 " +
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
    // TODO: show current location https://developers.google.com/maps/documentation/javascript/geolocation
    map.fitBounds(markerBounds);
    // new AutocompleteDirectionsHandler(map);
    const directionsService = new google.maps.DirectionsService();
    const directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map)
    document.getElementById("search-form").onsubmit = (e) => getDirections(e, directionsService, directionsRenderer, start_location, end_location)

}

// https://developers.google.com/maps/documentation/javascript/examples/places-autocomplete-directions
function getDirections(e, directionsService, directionsRenderer,start_location, end_location) {
  e.preventDefault();
  console.log(e, start_location, end_location)
  const start_place = start_location.getPlace();
  const end_place = end_location.getPlace();
 
  directionsService.route(
    {
      origin: { placeId: start_place.place_id},
      destination: { placeId: end_place.place_id },
      // TODO: now need routes with walking and biking too
      travelMode: google.maps.TravelMode.WALKING,
    },
    (response, status) => {
      if (status === "OK") {
        directionsRenderer.setDirections(response);
      } else {
        window.alert("Directions request failed due to " + status);
      }
    },
  );

  console.log(start_place, end_place)
}

window.initMap = initMap;
