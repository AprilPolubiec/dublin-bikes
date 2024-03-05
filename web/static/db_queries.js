export function getStations() {
    return fetch("/stations");
}
export function getStation(stationId) {
    return fetch(`/station/${stationId}`);
}

export function getAvailability(stationId, startTime, endTime) {
    return fetch("/availability?" + new URLSearchParams({
        stationId,
        startTime,
        endTime,
    }));
}