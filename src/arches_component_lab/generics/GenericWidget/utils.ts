export function removeVueExtension(inputFilename: string): string {
    if (typeof inputFilename !== "string") {
        throw new TypeError(
            `Expected a string but received ${typeof inputFilename}`,
        );
    }

    const vueExtensionPattern = /\.vue$/i;
    if (!vueExtensionPattern.test(inputFilename)) {
        return inputFilename;
    }

    return inputFilename.replace(vueExtensionPattern, "");
}
