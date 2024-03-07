export function getStations() {
    return fetch("/stations").then(d => d.json());
}
export function getStation(stationId) {
    return fetch(`/station/${stationId}`).then(d => d.json());
}

export function getAvailability(stationId, startTime, endTime) {
    return fetch("/availability?" + new URLSearchParams({
        stationId,
        startTime,
        endTime,
    }));
}