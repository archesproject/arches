export const REMOVE = "remove";
export const UPDATE_METADATA = "update:metadata";

export const PRIMARY_FILE_METADATA_FIELDS = ["altText"] as const;
export const ADDITIONAL_FILE_METADATA_FIELDS = [
    "title",
    "attribution",
    "description",
] as const;
export const FILE_METADATA_FIELDS = [
    ...PRIMARY_FILE_METADATA_FIELDS,
    ...ADDITIONAL_FILE_METADATA_FIELDS,
] as const;
