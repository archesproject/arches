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

export function getUpdatedComponentPath(
    deprecatedComponentPath: string,
): string {
    const deprecatedComponentToUpdatedComponentPathMap: Record<string, string> =
        {
            "views/components/widgets/text":
                "arches_component_lab/widgets/NonLocalizedStringWidget/NonLocalizedStringWidget",
            "views/components/widgets/concept-select":
                "arches_component_lab/widgets/ConceptSelectWidget/ConceptSelectWidget",
            "views/components/widgets/datepicker":
                "arches_component_lab/widgets/DatePickerWidget/DatePickerWidget",
            "views/components/widgets/rich-text":
                "arches_component_lab/widgets/RichTextWidget/RichTextWidget",
            "views/components/widgets/radio-boolean":
                "arches_component_lab/widgets/RadioBooleanWidget/RadioBooleanWidget",
            "views/components/widgets/map":
                "arches_component_lab/widgets/MapWidget/MapWidget",
            "views/components/widgets/number":
                "arches_component_lab/widgets/NumberWidget/NumberWidget",
            "views/components/widgets/concept-radio":
                "arches_component_lab/widgets/ConceptRadioWidget/ConceptRadioWidget",
            "views/components/widgets/concept-multiselect":
                "arches_component_lab/widgets/ConceptMultiselectWidget/ConceptMultiselectWidget",
            "views/components/widgets/concept-checkbox":
                "arches_component_lab/widgets/ConceptCheckboxWidget/ConceptCheckboxWidget",
            "views/components/widgets/domain-select":
                "arches_component_lab/widgets/DomainSelectWidget/DomainSelectWidget",
            "views/components/widgets/domain-multiselect":
                "arches_component_lab/widgets/DomainMultiselectWidget/DomainMultiselectWidget",
            "views/components/widgets/domain-radio":
                "arches_component_lab/widgets/DomainRadioWidget/DomainRadioWidget",
            "views/components/widgets/domain-checkbox":
                "arches_component_lab/widgets/DomainCheckboxWidget/DomainCheckboxWidget",
            "views/components/widgets/file":
                "arches_component_lab/widgets/FileWidget/FileWidget",
            "views/components/widgets/resource-instance-select":
                "arches_component_lab/widgets/ResourceInstanceSelectWidget/ResourceInstanceSelectWidget",
            "views/components/widgets/non-localized-text":
                "arches_component_lab/widgets/NonLocalizedStringWidget/NonLocalizedStringWidget",
            "views/components/widgets/edtf":
                "arches_component_lab/widgets/EdtfWidget/EdtfWidget",
            "views/components/widgets/urldatatype":
                "arches_component_lab/widgets/URLWidget/URLWidget",
            "views/components/widgets/node-value-select":
                "arches_component_lab/widgets/NodeValueSelectWidget/NodeValueSelectWidget",
            "views/components/widgets/resource-instance-multiselect":
                "arches_component_lab/widgets/ResourceInstanceMultiselectWidget/ResourceInstanceMultiselectWidget",
        };

    const resolvedUpdatedComponentPath: string | undefined =
        deprecatedComponentToUpdatedComponentPathMap[deprecatedComponentPath];

    if (resolvedUpdatedComponentPath === undefined) {
        throw new Error(
            `No updated component path found for deprecated path "${deprecatedComponentPath}".`,
        );
    }

    return resolvedUpdatedComponentPath;
}
