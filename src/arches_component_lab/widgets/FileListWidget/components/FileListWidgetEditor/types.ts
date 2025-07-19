export interface FileData {
    name: string;
    size: number;
    type: string;
    url: string;
    file: File;
    node_id: string;
}

export type PrimeVueFile = File & { objectURL: string };
