export async function getStations() {
  const response = await fetch('stations');
  if (response.status === 200) {
    return response.json();
  } else {
    const errorText = await response.text();
    throw new Error(errorText);
  }
}

export async function getAvailabilities() {
  const response = await fetch('/availability');
  if (response.status === 200) {
    return response.json();
  } else {
    const errorText = await response.text();
    throw new Error(errorText);
  }
}

// Uses API to ensure the most up to date
export async function getCurrentWeather(lat, lon) {
  const response = await fetch(
    `https://api.openweathermap.org/data/2.5/weather?` +
      new URLSearchParams({
        units: 'metric',
        lat,
        lon,
        appid: '6cc534f5dd39c8f71e2d56c29c35dc71',
      })
  );
  if (response.status === 200) {
    return response.json();
  } else {
    const errorText = await response.text();
    throw new Error(errorText);
  }
}

export async function getHourlyForecast(lat, lon) {
  const response = await fetch(
    `https://pro.openweathermap.org/data/2.5/forecast/hourly?` +
      new URLSearchParams({
        units: 'metric',
        lat,
        lon,
        appid: '6cc534f5dd39c8f71e2d56c29c35dc71',
      })
  );
  if (response.status === 200) {
    return response.json();
  } else {
    const errorText = await response.text();
    throw new Error(errorText);
  }
}

export async function getPredictedAvailabilities(date) {
  let timestamp = new Date(date).getTime() / 1000;
  const response = await fetch(`/predicted-availabilities?` + new URLSearchParams({ date_timestamp: timestamp }));
  if (response.status === 200) {
    return response.json();
  } else {
    const errorText = await response.text();
    throw new Error(errorText);
  }
}
export async function getHistoricalAverageAvailabilities(stationId) {
  const response = await fetch(`/historical-availability/${stationId}`);
  if (response.status === 200) {
    return response.json();
  } else {
    const errorText = await response.text();
    throw new Error(errorText);
  }
}
