export function getStations() {
    return fetch("/stations").then(d => d.json());
}
export function getStation(stationId) {
    return fetch(`/station/${stationId}`).then(d => d.json());
}

export function getAvailabilities() {
    return fetch(`/availability`).then(d => d.json());
}