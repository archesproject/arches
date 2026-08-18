import { existsSync, readFileSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

import { createProjectNodeModulesFallbackPlugin } from "./project-node-modules-fallback.ts";

import type { Plugin } from "vite";

const currentDirectory = path.dirname(fileURLToPath(import.meta.url));

function resolveViaPlugin(plugin: Plugin, source: string): string | null {
    const hook = plugin.resolveId;
    if (typeof hook !== "function") {
        throw new Error("resolveId hook is not a plain function");
    }
    return hook.call(
        {} as never,
        source,
        undefined,
        {} as never,
    ) as string | null;
}

describe("createProjectNodeModulesFallbackPlugin", () => {
    test("has the expected plugin name and hook ordering", () => {
        const plugin = createProjectNodeModulesFallbackPlugin();

        expect(plugin.name).toBe("project-node-modules-fallback");
        expect(plugin.enforce).toBe("post");
    });

    test("ignores relative specifiers", () => {
        const plugin = createProjectNodeModulesFallbackPlugin();

        expect(resolveViaPlugin(plugin, "./sibling-file")).toBeNull();
        expect(resolveViaPlugin(plugin, "../parent-file")).toBeNull();
    });

    test("ignores absolute specifiers", () => {
        const plugin = createProjectNodeModulesFallbackPlugin();
        const absoluteSpecifier = path.join(
            currentDirectory,
            "project-node-modules-fallback.ts",
        );

        expect(resolveViaPlugin(plugin, absoluteSpecifier)).toBeNull();
    });

    test("resolves a bare specifier installed in this project's own node_modules", () => {
        const plugin = createProjectNodeModulesFallbackPlugin();
        const resolved = resolveViaPlugin(plugin, "typescript");

        expect(resolved).toBeTruthy();
        expect(existsSync(resolved!)).toBe(true);
        expect(resolved).toContain(path.join("node_modules", "typescript"));
    });

    test("returns null instead of throwing for a specifier that cannot be found anywhere", () => {
        const plugin = createProjectNodeModulesFallbackPlugin();

        expect(
            resolveViaPlugin(plugin, "this-package-does-not-exist-anywhere-abc123"),
        ).toBeNull();
    });

    // kept in sync by hand across projects; this project and arches core are the two known copies
    const thisFile = path.resolve(
        currentDirectory,
        "project-node-modules-fallback.test.ts",
    );
    const otherCopies = ["test-modular-reports", "arches"]
        .map((project) =>
            path.resolve(
                currentDirectory,
                "..",
                "..",
                project,
                "vitest-utils",
                "project-node-modules-fallback.test.ts",
            ),
        )
        .filter((copy) => copy !== thisFile && existsSync(copy));

    test.skipIf(otherCopies.length === 0)(
        "stays byte-identical to the other project copies of this file",
        () => {
            const thisContent = readFileSync(thisFile, "utf-8");
            const mismatches = otherCopies.filter(
                (copy) => readFileSync(copy, "utf-8") !== thisContent,
            );
            expect(mismatches).toEqual([]);
        },
    );
});
