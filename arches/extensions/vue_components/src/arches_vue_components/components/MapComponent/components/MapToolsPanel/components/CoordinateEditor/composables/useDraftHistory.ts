import { computed, shallowRef } from "vue";

import { cloneDeep, isEqual } from "es-toolkit";

import type { ComputedRef, Ref } from "vue";

const UNDO_HISTORY_LIMIT = 50;

export interface UseDraftHistoryReturn {
    canUndo: ComputedRef<boolean>;
    commit: () => void;
    commitIfChanged: () => void;
    undo: () => void;
    reset: () => void;
}

export function useDraftHistory<Draft>(
    draft: Ref<Draft>,
): UseDraftHistoryReturn {
    const undoStack = shallowRef<Draft[]>([]);

    let committedDraft = cloneDeep(draft.value);

    const canUndo = computed(() => undoStack.value.length > 0);

    function commit(): void {
        undoStack.value = [...undoStack.value, committedDraft].slice(
            -UNDO_HISTORY_LIMIT,
        );
        committedDraft = cloneDeep(draft.value);
    }

    function commitIfChanged(): void {
        if (!isEqual(draft.value, committedDraft)) {
            commit();
        }
    }

    function undo(): void {
        const previousDraft = undoStack.value.at(-1);
        if (!previousDraft) {
            return;
        }

        undoStack.value = undoStack.value.slice(0, -1);
        committedDraft = previousDraft;
        draft.value = cloneDeep(previousDraft);
    }

    function reset(): void {
        undoStack.value = [];
        committedDraft = cloneDeep(draft.value);
    }

    return { canUndo, commit, commitIfChanged, undo, reset };
}
