import { computed, shallowRef } from "vue";

import type { ComputedRef } from "vue";

const UNDO_HISTORY_LIMIT = 50;

export interface UseCoordinateUndoReturn<Snapshot> {
    canUndo: ComputedRef<boolean>;
    pushSnapshot: (snapshot: Snapshot) => void;
    popSnapshot: () => Snapshot | undefined;
    clearHistory: () => void;
}

export function useCoordinateUndo<
    Snapshot,
>(): UseCoordinateUndoReturn<Snapshot> {
    const undoStack = shallowRef<Snapshot[]>([]);

    const canUndo = computed(() => undoStack.value.length > 0);

    function pushSnapshot(snapshot: Snapshot): void {
        undoStack.value = [...undoStack.value, snapshot].slice(
            -UNDO_HISTORY_LIMIT,
        );
    }

    function popSnapshot(): Snapshot | undefined {
        const previousSnapshot = undoStack.value.at(-1);
        undoStack.value = undoStack.value.slice(0, -1);
        return previousSnapshot;
    }

    function clearHistory(): void {
        undoStack.value = [];
    }

    return { canUndo, pushSnapshot, popSnapshot, clearHistory };
}
