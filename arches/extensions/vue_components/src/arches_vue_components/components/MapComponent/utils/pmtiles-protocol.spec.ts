import { describe, expect, it, vi } from "vitest";

const { addProtocol } = vi.hoisted(() => ({ addProtocol: vi.fn() }));

vi.mock("maplibre-gl", () => ({ addProtocol }));

import { registerPmtilesProtocol } from "@/arches_vue_components/components/MapComponent/utils/pmtiles-protocol.ts";

describe("registerPmtilesProtocol", () => {
    it("registers the pmtiles protocol once, however many maps call it", () => {
        registerPmtilesProtocol();
        registerPmtilesProtocol();

        expect(addProtocol).toHaveBeenCalledTimes(1);
        expect(addProtocol).toHaveBeenCalledWith(
            "pmtiles",
            expect.any(Function),
        );
    });
});
