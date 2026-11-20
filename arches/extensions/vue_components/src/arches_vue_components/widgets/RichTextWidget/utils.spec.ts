import { describe, expect, it } from "vitest";

import { richTextToPlainText } from "@/arches_vue_components/widgets/RichTextWidget/utils.ts";

describe("richTextToPlainText", () => {
    it("keeps words in separate paragraphs and lines apart", () => {
        expect(
            richTextToPlainText(
                "<p>First <strong>bold</strong></p><p>Second<br>Third</p>",
            ),
        ).toBe("First bold Second Third");
    });
});
