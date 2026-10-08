import { describe, expect, it } from "vitest";

import { useCoordinateUndo } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinateUndo.ts";

describe("useCoordinateUndo", () => {
    it("pops snapshots in reverse order", () => {
        const { canUndo, pushSnapshot, popSnapshot } =
            useCoordinateUndo<number>();
        expect(canUndo.value).toBe(false);

        pushSnapshot(1);
        pushSnapshot(2);
        expect(canUndo.value).toBe(true);
        expect(popSnapshot()).toBe(2);
        expect(popSnapshot()).toBe(1);
        expect(popSnapshot()).toBeUndefined();
        expect(canUndo.value).toBe(false);
    });

    it("keeps only the most recent fifty snapshots", () => {
        const { pushSnapshot, popSnapshot } = useCoordinateUndo<number>();
        for (let snapshot = 1; snapshot <= 60; snapshot++) {
            pushSnapshot(snapshot);
        }

        const remainingSnapshots: number[] = [];
        let snapshot = popSnapshot();
        while (snapshot !== undefined) {
            remainingSnapshots.push(snapshot);
            snapshot = popSnapshot();
        }
        expect(remainingSnapshots).toHaveLength(50);
        expect(remainingSnapshots.at(-1)).toBe(11);
    });

    it("clears history", () => {
        const { canUndo, pushSnapshot, clearHistory } =
            useCoordinateUndo<number>();
        pushSnapshot(1);
        clearHistory();
        expect(canUndo.value).toBe(false);
    });
});
