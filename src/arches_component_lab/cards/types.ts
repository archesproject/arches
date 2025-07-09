export interface AliasedTileData {
    tileid: string;
    aliased_data: {
        [key: string]: {
            display_value: string;
            interchange_value: unknown;
        };
    };
}
