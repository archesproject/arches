export type CoordinateEntryKind = "point" | "line" | "polygon";

export interface CoordinateRow {
    x: number | null;
    y: number | null;
}

export interface CompleteCoordinateRow {
    x: number;
    y: number;
}
