/**
 * Collapse behaviour, replacing Bootstrap 3's collapse plugin.
 *
 * Bootstrap 3 toggled `.in` on the target and animated its height. The vendored
 * stylesheet still carries `.collapse`, `.collapse.in` and `.collapsing`, so this only
 * has to drive those classes and measure the height for the transition.
 *
 * Used by five triggers, including the public landing page's navbar toggle — the one
 * place a collapse failure is visible to anonymous visitors.
 */

const TRIGGER_SELECTOR = '[data-toggle="collapse"]';

/** Bootstrap 3 accepted the target as `data-target`, falling back to `href`. */
function targetsOf(trigger) {
    const selector =
        trigger.getAttribute('data-target') ||
        trigger.getAttribute('href') ||
        '';
    if (!selector || selector === '#') {
        return [];
    }
    try {
        return Array.from(document.querySelectorAll(selector));
    } catch {
        return [];
    }
}

function isShown(element) {
    return element.classList.contains('in');
}

export function show(element) {
    if (element.classList.contains('collapsing') || isShown(element)) {
        return;
    }
    element.classList.remove('collapse');
    element.classList.add('collapsing');
    element.style.height = '0px';

    // Forces layout so the transition has two distinct heights to run between.
    void element.offsetHeight;
    element.style.height = `${element.scrollHeight}px`;

    window.setTimeout(function () {
        element.classList.remove('collapsing');
        element.classList.add('collapse', 'in');
        element.style.height = '';
    }, 350);
}

export function hide(element) {
    if (element.classList.contains('collapsing') || !isShown(element)) {
        return;
    }
    element.style.height = `${element.getBoundingClientRect().height}px`;
    void element.offsetHeight;

    element.classList.add('collapsing');
    element.classList.remove('collapse', 'in');
    element.style.height = '0px';

    window.setTimeout(function () {
        element.classList.remove('collapsing');
        element.classList.add('collapse');
        element.style.height = '';
    }, 350);
}

export function toggle(element) {
    if (isShown(element)) {
        hide(element);
    } else {
        show(element);
    }
}

export function install(root = document) {
    root.addEventListener('click', function (event) {
        const trigger = event.target.closest(TRIGGER_SELECTOR);
        if (!trigger) {
            return;
        }
        event.preventDefault();

        for (const target of targetsOf(trigger)) {
            const willShow = !isShown(target);
            toggle(target);
            trigger.setAttribute('aria-expanded', String(willShow));
            trigger.classList.toggle('collapsed', !willShow);
        }
    });
}
