export function getStations() {
  return fetch('/stations').then((d) => d.json());
}
// export function getStation(stationId) {
//   return fetch(`/station/${stationId}`).then((d) => d.json());
// }

export function getAvailabilities() {
  return fetch(`/availability`).then((d) => d.json());
}

export function getCurrentWeather(lat, lon) {
  return fetch(
    `https://api.openweathermap.org/data/2.5/weather?` +
      new URLSearchParams({
        units: 'metric',
        lat,
        lon,
        appid: '6cc534f5dd39c8f71e2d56c29c35dc71',
      })
  ).then((d) => d.json());
}

export function getHourlyForecast(lat, lon) {
  return fetch(
    `https://pro.openweathermap.org/data/2.5/forecast/hourly?` +
      new URLSearchParams({
        units: 'metric',
        lat,
        lon,
        appid: '6cc534f5dd39c8f71e2d56c29c35dc71',
      })
  ).then((d) => d.json());
}
