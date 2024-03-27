import type { ControlledListItem } from "@/types/ControlledListManager";

export const bestLabel = (item: ControlledListItem, languageCode: string) => {
    const labelsInLang = item.labels.filter(l => l.language === languageCode);
    const bestLabel = (
        labelsInLang.find(l => l.valuetype === "prefLabel")
        ?? labelsInLang.find(l => l.valuetype === "altLabel")
        ?? item.labels.find(l => l.valuetype === "prefLabel")
    );
    if (!bestLabel) {
        throw new Error();
    }
    return bestLabel;
};
