<!-- 
 This is a one-off component because the Quill-based `Editor` 
 component uses a non-labellable `div` for its input element
 -->

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from "vue";

const { nodeAlias } = defineProps<{ nodeAlias: string }>();

const wrapperElementRef = ref<HTMLElement | null>(null);

let removeWrapperFocusIn: (() => void) | null = null;
let removeLabelPointerDown: (() => void) | null = null;

function focusTextArea(wrapperElement: HTMLElement): void {
    const maxFindFrames = 20;
    let framesTried = 0;

    const findTextArea = () => {
        const targetElement = wrapperElement.querySelector<HTMLElement>(
            '[contenteditable="true"]',
        );
        if (!targetElement) {
            if (framesTried++ < maxFindFrames)
                requestAnimationFrame(findTextArea);
            return;
        }

        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                const selection = document.getSelection();
                if (!selection) return;

                const range = document.createRange();
                range.selectNodeContents(targetElement);
                range.collapse(false);

                selection.removeAllRanges();
                selection.addRange(range);
            });
        });
    };

    requestAnimationFrame(findTextArea);
}

onMounted(() => {
    const wrapperElement = wrapperElementRef.value;
    if (!wrapperElement) return;

    const onFocusIn = (focusEvent: FocusEvent) => {
        if (focusEvent.target === wrapperElement) {
            focusTextArea(wrapperElement);
        }
    };
    wrapperElement.addEventListener("focusin", onFocusIn);
    removeWrapperFocusIn = () =>
        wrapperElement.removeEventListener("focusin", onFocusIn);

    const associatedLabelElement =
        Array.from(document.getElementsByTagName("label")).find(
            (labelElement) => labelElement.htmlFor === nodeAlias,
        ) ?? null;

    if (associatedLabelElement) {
        const onPointerDown = (_event: PointerEvent) => {
            wrapperElement.focus();
            focusTextArea(wrapperElement);
        };
        associatedLabelElement.addEventListener(
            "pointerdown",
            onPointerDown,
            true,
        );
        removeLabelPointerDown = () =>
            associatedLabelElement.removeEventListener(
                "pointerdown",
                onPointerDown,
                true,
            );
    }
});

onBeforeUnmount(() => {
    removeWrapperFocusIn?.();
    removeLabelPointerDown?.();
});
</script>

<template>
    <div
        :id="nodeAlias"
        ref="wrapperElementRef"
        tabindex="-1"
    >
        <slot />
    </div>
</template>
