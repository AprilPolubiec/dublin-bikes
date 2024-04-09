export function getStations() {
  return fetch('/stations').then((d) => d.json());
}

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

export function getPredictedAvailability(station_id, date) {
  let timestamp = new Date(date).getTime() / 1000;
  return fetch(`/predicted-availability/${station_id}` + new URLSearchParams({ date_timestamp: timestamp })).then((d) => d.json());
}
export function getPredictedAvailabilities(date) {
  let timestamp = new Date(date).getTime() / 1000;
  return fetch(`/predicted-availabilities?` + new URLSearchParams({ date_timestamp: timestamp })).then((d) => d.json());
}
export function getHistoricalAverageAvailabilities(stationId) {
  return fetch(`/historical-availability/${stationId}`).then((d) => d.json());
}
