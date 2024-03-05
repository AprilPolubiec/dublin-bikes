import { getAvailability, getStation } from './db_queries.js';

const DUBLIN_LATITUDE = 53.3498;
const DUBLIN_LONGITUDE = 6.2603;

function initMap() {
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