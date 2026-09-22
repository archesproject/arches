/**
 * Dropdown behaviour, replacing Bootstrap 3's dropdown plugin. Toggles `.open` on the
 * trigger's parent, which is what the vendored Bootstrap 3 stylesheet styles.
 */

const TRIGGER_SELECTOR = '[data-toggle="dropdown"]';
const PARENT_SELECTOR = '.dropdown, .btn-group, .dropup, .input-group-btn';
const OPEN_CLASS = 'open';

function parentOf(trigger) {
    return trigger.closest(PARENT_SELECTOR) || trigger.parentElement;
}

function closeAll(except = null) {
    for (const open of document.querySelectorAll(`.${OPEN_CLASS}`)) {
        // `.open` is a generic enough class name that arches uses it elsewhere, so
        // only close elements that actually hold a dropdown trigger.
        const trigger = open.querySelector(TRIGGER_SELECTOR);
        if (open === except || !trigger) {
            continue;
        }
        open.classList.remove(OPEN_CLASS);
        trigger.setAttribute('aria-expanded', 'false');
    }
}

export function toggle(trigger) {
    const parent = parentOf(trigger);
    if (!parent) {
        return;
    }
    const willOpen = !parent.classList.contains(OPEN_CLASS);
    closeAll(willOpen ? parent : null);
    parent.classList.toggle(OPEN_CLASS, willOpen);
    trigger.setAttribute('aria-expanded', String(willOpen));
}

export function hideAll() {
    closeAll();
}

export function install(root = document) {
    root.addEventListener('click', function (event) {
        const trigger = event.target.closest(TRIGGER_SELECTOR);
        if (trigger) {
            event.preventDefault();
            toggle(trigger);
            return;
        }
        // A click inside an open menu should not close it; anywhere else should.
        if (!event.target.closest('.dropdown-menu')) {
            closeAll();
        }
    });

    root.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            closeAll();
        }
    });
}
