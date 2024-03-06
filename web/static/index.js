import { getStations } from './db_queries.js';

const DUBLIN_LATITUDE = 53.3498;
const DUBLIN_LONGITUDE = 6.2603;

async function initMap() {
    const dublinCoordinates = { lat: DUBLIN_LATITUDE, lng: DUBLIN_LONGITUDE };
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 6,
        center: dublinCoordinates,
    });
  
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

    map.fitBounds(markerBounds);

}

window.initMap = initMap;
