export const REMOVE = "remove";
export const UPDATE_METADATA = "update:metadata";

export const FILE_METADATA_FIELDS = [
    "altText",
    "title",
    "description",
    "attribution",
] as const;

// Grouped as in the Knockout file widget: alt text is always shown, and the
// rest sit in a collapsible "Additional metadata" section.
export const PRIMARY_FILE_METADATA_FIELDS = ["altText"] as const;
export const ADDITIONAL_FILE_METADATA_FIELDS = [
    "title",
    "attribution",
    "description",
] as const;
