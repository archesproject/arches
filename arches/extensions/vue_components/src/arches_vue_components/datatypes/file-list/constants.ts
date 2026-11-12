export const REMOVE = "remove";
export const UPDATE_METADATA = "update:metadata";
export const UPDATE_METADATA_LANGUAGE = "update:metadataLanguage";

export const FILE_METADATA_FIELDS = [
    "altText",
    "title",
    "description",
    "attribution",
] as const;

export const PRIMARY_FILE_METADATA_FIELDS = ["altText"] as const;
export const ADDITIONAL_FILE_METADATA_FIELDS = [
    "title",
    "attribution",
    "description",
] as const;
