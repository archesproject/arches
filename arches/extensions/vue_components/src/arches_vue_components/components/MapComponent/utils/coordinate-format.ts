const HEMISPHERES = {
    latitude: { positive: "N", negative: "S" },
    longitude: { positive: "E", negative: "W" },
};

const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_DEGREE = 60;

export function formatDegreesMinutesSeconds(
    value: number,
    axis: keyof typeof HEMISPHERES,
): string {
    const hemisphere =
        value >= 0 ? HEMISPHERES[axis].positive : HEMISPHERES[axis].negative;
    const absoluteValue = Math.abs(value);

    let degrees = Math.floor(absoluteValue);
    const fractionalMinutes = (absoluteValue - degrees) * MINUTES_PER_DEGREE;
    let minutes = Math.floor(fractionalMinutes);
    let seconds = (fractionalMinutes - minutes) * SECONDS_PER_MINUTE;

    if (seconds.toFixed(1) === SECONDS_PER_MINUTE.toFixed(1)) {
        seconds = 0;
        minutes += 1;
    }
    if (minutes === MINUTES_PER_DEGREE) {
        minutes = 0;
        degrees += 1;
    }

    const paddedMinutes = String(minutes).padStart(2, "0");
    const paddedSeconds = seconds.toFixed(1).padStart(4, "0");

    return `${degrees}°${paddedMinutes}'${paddedSeconds}"${hemisphere}`;
}
