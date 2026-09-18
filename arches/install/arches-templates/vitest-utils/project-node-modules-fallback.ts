import path from "path";
import { createRequire } from "module";
import { fileURLToPath } from "url";

import type { Plugin } from "vite";

export function createProjectNodeModulesFallbackPlugin(): Plugin {
    const projectRoot = path.resolve(
        path.dirname(fileURLToPath(import.meta.url)),
        "..",
    );
    const requireFromProjectRoot = createRequire(
        path.join(projectRoot, "package.json"),
    );

    return {
        name: "project-node-modules-fallback",
        enforce: "post",
        resolveId(source) {
            if (source.startsWith(".") || path.isAbsolute(source)) {
                return null;
            }
            try {
                return requireFromProjectRoot.resolve(source);
            } catch {
                return null;
            }
        },
    };
}
