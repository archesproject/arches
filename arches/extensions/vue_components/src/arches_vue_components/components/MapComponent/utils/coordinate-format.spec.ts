import { describe, expect, it } from "vitest";

import { formatDegreesMinutesSeconds } from "@/arches_vue_components/components/MapComponent/utils/coordinate-format.ts";

describe("formatDegreesMinutesSeconds", () => {
    it("formats a negative longitude with a western hemisphere", () => {
        expect(formatDegreesMinutesSeconds(-0.1276, "longitude")).toBe(
            `0°07'39.4"W`,
        );
    });

    it("carries rounded seconds into the next minute and degree", () => {
        expect(formatDegreesMinutesSeconds(10.99999, "latitude")).toBe(
            `11°00'00.0"N`,
        );
    });
});
