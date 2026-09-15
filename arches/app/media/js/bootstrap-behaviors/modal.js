/**
 * Modal behaviour, replacing Bootstrap 3's modal plugin.
 *
 * Twenty-nine call sites use it, all inside `arches/app/media/js/views/rdm/`, and all
 * through jQuery's `$(el).modal('show' | 'hide')`. That API is re-exposed in
 * `index.js` so none of those files change.
 *
 * Bootstrap 3 hid `.modal` with `display: none` in CSS and showed it by setting
 * `display: block` inline and adding `.in`, with a separate `.modal-backdrop` element
 * and `.modal-open` on the body. The vendored stylesheet still carries all of those,
 * so this drives the same classes.
 *
 * **Focus is deliberately not trapped.** Bootstrap 3 pulled focus back into the modal,
 * which broke the select2 and chosen dropdowns arches renders inside them — `rdm.js`
 * used to neutralise it with
 * `$.fn.modal.Constructor.prototype.enforceFocus = function () {}`. Not implementing it
 * preserves the behaviour arches actually wanted, and lets that override go away.
 */

const BACKDROP_CLASS = 'modal-backdrop';
const TRANSITION_MS = 300;

let openModals = [];

function hasFade(element) {
    return element.classList.contains('fade');
}

function createBackdrop(element) {
    const backdrop = document.createElement('div');
    backdrop.className = hasFade(element)
        ? `${BACKDROP_CLASS} fade`
        : `${BACKDROP_CLASS} in`;
    document.body.appendChild(backdrop);
    if (hasFade(element)) {
        void backdrop.offsetHeight;
        backdrop.classList.add('in');
    }
    return backdrop;
}

export function show(element) {
    if (!element || openModals.some((entry) => entry.element === element)) {
        return;
    }

    const backdrop = createBackdrop(element);
    openModals.push({ element, backdrop });

    document.body.classList.add('modal-open');
    element.style.display = 'block';
    element.removeAttribute('aria-hidden');
    element.setAttribute('aria-modal', 'true');

    void element.offsetHeight;
    element.classList.add('in');

    element.dispatchEvent(new CustomEvent('shown.bs.modal', { bubbles: true }));
}

export function hide(element) {
    const index = openModals.findIndex((entry) => entry.element === element);
    if (index === -1) {
        return;
    }
    const { backdrop } = openModals[index];
    openModals.splice(index, 1);

    element.classList.remove('in');
    backdrop.classList.remove('in');

    const finish = () => {
        element.style.display = 'none';
        element.setAttribute('aria-hidden', 'true');
        element.removeAttribute('aria-modal');
        backdrop.remove();
        if (openModals.length === 0) {
            document.body.classList.remove('modal-open');
        }
        element.dispatchEvent(new CustomEvent('hidden.bs.modal', { bubbles: true }));
    };

    if (hasFade(element)) {
        window.setTimeout(finish, TRANSITION_MS);
    } else {
        finish();
    }
}

export function toggle(element) {
    if (openModals.some((entry) => entry.element === element)) {
        hide(element);
    } else {
        show(element);
    }
}

function topMost() {
    return openModals.length ? openModals[openModals.length - 1].element : null;
}

export function install(root = document) {
    // `data-dismiss="modal"` — 33 close buttons across the RDM forms.
    root.addEventListener('click', function (event) {
        const dismiss = event.target.closest('[data-dismiss="modal"]');
        if (dismiss) {
            const element = dismiss.closest('.modal');
            if (element) {
                event.preventDefault();
                hide(element);
            }
            return;
        }

        // Clicking the backdrop area closes, matching Bootstrap 3's default.
        const element = topMost();
        if (element && event.target === element) {
            hide(element);
        }
    });

    root.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') {
            return;
        }
        const element = topMost();
        if (element) {
            hide(element);
        }
    });
}
