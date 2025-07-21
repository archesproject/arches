import dayjs from "dayjs";

export function formatDate(
    date: Date | null,
    dateFormat: string,
): string | null {
    if (!date) {
        return null;
    }

    return dayjs(date).format(dateFormat);
}
