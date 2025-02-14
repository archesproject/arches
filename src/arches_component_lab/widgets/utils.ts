export function convertISO8601DatetimeFormatToPrimevueDatetimeFormat(
    inputFormat: string,
): { dateFormat: string; shouldShowTime: boolean } {
    const dateTokenMap: Record<string, string> = {
        YYYY: "yy", // 4-digit year → "yy"
        YY: "y", // 2-digit year → "y"
        MMMM: "MM", // full month name → "MM"
        MMM: "M", // abbreviated month name → "M"
        MM: "mm", // month with leading zero → "mm"
        M: "m", // month without leading zero → "m"
        dddd: "DD", // full day name → "DD"
        ddd: "D", // abbreviated day name → "D"
        DDDD: "oo", // day of year (three digits) → "oo"
        DDD: "o", // day of year (no leading zero) → "o"
        DD: "dd", // day with leading zero → "dd"
        D: "d", // day without leading zero → "d"
        "@": "@", // Unix timestamp → "@"
        "!": "!", // Windows ticks → "!"
    };

    const timeTokens: string[] = [
        "HH",
        "H",
        "hh",
        "h", // Hours
        "mm", // Minutes
        "ss",
        "s", // Seconds
        "SSS", // Milliseconds
        "A",
        "a", // AM/PM markers
        "Z",
        "ZZ", // Timezone offsets
        "kk",
        "k", // Alternative hour tokens
    ];

    // Sort tokens so that longer ones are replaced before shorter ones.
    const sortedDateTokens = Object.keys(dateTokenMap).sort(
        (a, b) => b.length - a.length,
    );
    const sortedTimeTokens = [...timeTokens].sort(
        (a, b) => b.length - a.length,
    );

    // Remove all time tokens and mark that time info is present.
    let containsTime = false;
    let processedFormat = inputFormat;

    for (const timeToken of sortedTimeTokens) {
        if (processedFormat.includes(timeToken)) {
            containsTime = true;
            processedFormat = processedFormat.split(timeToken).join("");
        }
    }

    // Replace date tokens with their mapped equivalents.
    for (const dateToken of sortedDateTokens) {
        processedFormat = processedFormat
            .split(dateToken)
            .join(dateTokenMap[dateToken]);
    }

    // Final cleanup: collapse any repeated colons (or other punctuation) that may result.
    processedFormat = processedFormat.replace(/:/g, "");
    processedFormat = processedFormat.trim();

    return { dateFormat: processedFormat, shouldShowTime: containsTime };
}
