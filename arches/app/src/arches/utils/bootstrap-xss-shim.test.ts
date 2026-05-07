import { describe, it, expect, beforeAll } from "vitest";

type GlobalWithJQuery = typeof globalThis & {
    jQuery: JQueryStatic;
    $: JQueryStatic;
};

type BS3jQuery = JQuery & {
    tooltip(config?: string | Record<string, unknown>): BS3jQuery;
    popover(config?: string | Record<string, unknown>): BS3jQuery;
    button(state?: string): BS3jQuery;
};

describe("bootstrap-xss-shim", () => {
    let $: JQueryStatic;

    beforeAll(async () => {
        const jquery = await import("jquery");
        $ = jquery.default;
        (globalThis as GlobalWithJQuery).jQuery = $;
        (globalThis as GlobalWithJQuery).$ = $;

        await import("bootstrap");
        await import("@/arches/../../media/js/utils/bootstrap-xss-shim.js");
    });

    describe("Tooltip XSS (SNYK-JS-BOOTSTRAP-10176066)", () => {
        it("escapes HTML in tooltip title attribute", () => {
            document.body.innerHTML =
                '<span id="target" data-toggle="tooltip" title="<img src=x onerror=alert(1)>">hover</span>';
            const $el = $("#target") as BS3jQuery;
            $el.tooltip("show");

            const tooltipInner = document.querySelector(".tooltip-inner");
            expect(tooltipInner).not.toBeNull();
            expect(tooltipInner!.innerHTML).not.toContain("<img");
            expect(tooltipInner!.textContent).toContain("<img");
        });

        it("escapes script tags in tooltip title option", () => {
            document.body.innerHTML = '<span id="target2">hover</span>';
            const $el = $("#target2") as BS3jQuery;
            $el.tooltip({ title: '<script>alert("xss")</script>', html: true });
            $el.tooltip("show");

            const tooltipInner = document.querySelector(".tooltip-inner");
            expect(tooltipInner).not.toBeNull();
            expect(tooltipInner!.innerHTML).not.toContain("<script>");
            expect(tooltipInner!.textContent).toContain("<script>");
        });
    });

    describe("Popover XSS (SNYK-JS-BOOTSTRAP-10176066)", () => {
        it("escapes HTML in popover title and content", () => {
            document.body.innerHTML = '<button id="pop1">click</button>';
            const $el = $("#pop1") as BS3jQuery;
            $el.popover({
                title: "<img src=x onerror=alert(1)>",
                content: '<script>alert("xss")</script>',
                html: true,
            });
            $el.popover("show");

            const popTitle = document.querySelector(".popover-title");
            const popContent = document.querySelector(".popover-content");
            expect(popTitle).not.toBeNull();
            expect(popContent).not.toBeNull();
            expect(popTitle!.innerHTML).not.toContain("<img");
            expect(popContent!.innerHTML).not.toContain("<script>");
        });
    });

    describe("Button XSS (SNYK-JS-BOOTSTRAP-7444617)", () => {
        it("escapes HTML in data-loading-text", () => {
            document.body.innerHTML =
                '<button id="btn1" data-loading-text="<img src=x onerror=alert(1)>">Submit</button>';
            const $el = $("#btn1") as BS3jQuery;
            $el.button("loading");

            return new Promise<void>((resolve) => {
                setTimeout(() => {
                    expect($el.html()).not.toContain("<img");
                    expect($el.text()).toContain("<img");
                    resolve();
                }, 10);
            });
        });
    });
});
