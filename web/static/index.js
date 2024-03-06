import { getStations } from './db_queries.js';

const DUBLIN_LATITUDE = 53.3498;
const DUBLIN_LONGITUDE = 6.2603;

async function initMap() {
    const dublinCoordinates = { lat: DUBLIN_LATITUDE, lng: DUBLIN_LONGITUDE };
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 4,
        center: dublinCoordinates,
    });

    const stations = await getStations();
    for (const station of stations) {
        const lat = parseFloat(station.PositionLatitude);
        const lng = parseFloat(station.PositionLongitude);
        const marker = new google.maps.Marker({
            position: { lat, lng },
            map,
            title: station.Name,
        });

        // const contentString =
        //     '<div id="bodyContent">' +
        //     "<p><b>Availability: </b> 0 " +
        //     "</div>";
      // const infowindow = new google.maps.InfoWindow({
      //   content: contentString,
      //   ariaLabel: station.Name,
      // });

      // marker.addListener("click", () => {
      //   infowindow.open({
      //     anchor: marker,
      //     map,
      //   });
      // });
    }

}

window.initMap = initMap;
