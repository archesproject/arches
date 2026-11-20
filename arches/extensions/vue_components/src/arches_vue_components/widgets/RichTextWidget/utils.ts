import { removeVueExtension } from "@/arches_vue_components/generics/GenericWidget/utils.ts";

import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";

const RICH_TEXT_WIDGET_COMPONENT =
    "arches_vue_components/widgets/RichTextWidget/RichTextWidget";
const LINE_BREAKING_ELEMENT_SELECTOR =
    "address, blockquote, br, div, h1, h2, h3, h4, h5, h6, li, p, pre, td, th, tr";
const WHITESPACE_PATTERN = /\s+/g;

export function isRichTextWidget(
    cardXNodeXWidgetData: CardXNodeXWidgetData,
): boolean {
    return (
        removeVueExtension(cardXNodeXWidgetData.widget.component) ===
        RICH_TEXT_WIDGET_COMPONENT
    );
}

export function richTextToPlainText(richText: string): string {
    const parsedDocument = new DOMParser().parseFromString(
        richText,
        "text/html",
    );
    for (const lineBreakingElement of parsedDocument.body.querySelectorAll(
        LINE_BREAKING_ELEMENT_SELECTOR,
    )) {
        lineBreakingElement.after(" ");
    }
    return (parsedDocument.body.textContent ?? "")
        .replace(WHITESPACE_PATTERN, " ")
        .trim();
}
