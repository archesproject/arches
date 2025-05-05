import { palette } from "@primeuix/themes";
import { ArchesPreset, DEFAULT_THEME } from "@/arches/themes/default.ts";

describe("ArchesPreset", () => {
    test("should define the correct arches primitive colors", () => {
        const arches = ArchesPreset.primitive.arches;
        expect(arches.blue).toBe("#579ddb");
        expect(arches.green).toBe("#3acaa1");
        expect(arches.red).toBe("#f75d3f");

        // Verify that legacy tokens are also set correctly
        expect(arches.legacy).toBeDefined();
        expect(arches.legacy.sidebar).toBe("#2d3c4b");
    });

    test("should assign proper palette values to primitive tokens", () => {
        // Compare the computed palette value with a call to palette (if palette returns a consistent structure)
        expect(ArchesPreset.primitive.blue).toEqual(palette("#579ddb"));
        expect(ArchesPreset.primitive.green).toEqual(palette("#3acaa1"));
        expect(ArchesPreset.primitive.red).toEqual(palette("#f75d3f"));
    });

    test("should contain the correct semantic tokens", () => {
        // The primary token is using the blue palette
        expect(ArchesPreset.semantic.primary).toEqual(palette("#579ddb"));

        // Check navigation tokens
        expect(ArchesPreset.semantic.navigation.list).toBeDefined();
        expect(ArchesPreset.semantic.navigation.list.padding).toBe("0");

        expect(ArchesPreset.semantic.navigation.item).toBeDefined();
        expect(ArchesPreset.semantic.navigation.item.padding).toBe("1rem");

        // Custom token that uses a reference to legacy value
        expect(ArchesPreset.semantic.navigation.header).toBeDefined();
        expect(ArchesPreset.semantic.navigation.header.color).toBe(
            "{arches.legacy.sidebar}",
        );
    });

    test("should correctly assign component tokens", () => {
        // Components tokens such as the splitter handle background
        expect(ArchesPreset.components.splitter).toBeDefined();
        expect(ArchesPreset.components.splitter.handle).toBeDefined();
        expect(ArchesPreset.components.splitter.handle.background).toBe(
            "{surface.500}",
        );
    });
});

describe("DEFAULT_THEME", () => {
    test("should reference the correct preset", () => {
        // The default theme should reference the ArchesPreset
        expect(DEFAULT_THEME.theme.preset).toBe(ArchesPreset);
    });

    test("should have the proper theme options", () => {
        const options = DEFAULT_THEME.theme.options;
        expect(options.prefix).toBe("p");
        expect(options.darkModeSelector).toBe(".arches-dark");
        expect(options.cssLayer).toBe(false);
    });
});
