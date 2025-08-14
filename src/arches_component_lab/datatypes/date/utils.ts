import dayjs from "dayjs";

export function formatDate(date: Date | null, dateFormat: string): string {
    if (!date) {
        return "";
    }

    if (isNaN(date.getTime())) {
        throw new Error("Invalid date");
    } else {
        return dayjs(date).format(dateFormat);
    }
}
