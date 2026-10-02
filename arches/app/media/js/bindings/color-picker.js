import ko from 'knockout';
import arches from 'arches';

/**
 * Colour picker binding, replacing bootstrap-colorpicker 2.5.3, which was Bootstrap
 * 3-only and unmaintained since 2019. Usage is unchanged:
 *
 *     data-bind="colorPicker: {color: someObservable, format: 'rgba'}"
 *
 * The bound element stays a text input, so a value can still be typed. Every call site
 * already ends its `.input-group` with an `.input-group-addon` holding an `ion-stop`
 * icon tinted to the current colour, so a native `<input type="color">` is overlaid
 * transparently on that addon rather than added beside it, which would break the
 * group's layout. Where no addon is present the swatch is appended to the group.
 *
 * `type="color"` cannot express an alpha channel, so `format: 'rgba'` also gets an
 * opacity slider.
 */

const SWATCH_CLASS = 'color-picker-swatch';
const ALPHA_CLASS = 'color-picker-alpha';
const ALPHA_FIELD_CLASS = 'color-picker-alpha-field';

let alphaFieldSequence = 0;

function hexToRgb(hex) {
    const value = parseInt((hex.length === 4 ? expandShorthandHex(hex) : hex).slice(1), 16);
    return { red: (value >> 16) & 255, green: (value >> 8) & 255, blue: value & 255 };
}

function rgbToHex(red, green, blue) {
    return '#' + ((1 << 24) + (red << 16) + (green << 8) + blue).toString(16).slice(1);
}

/** Accepts the hex and rgb/rgba spellings bootstrap-colorpicker emitted. */
function parseColor(rawValue) {
    const value = String(rawValue ?? '').trim();

    const rgbMatch = value.match(
        /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)$/
    );
    if (rgbMatch) {
        return {
            hex: rgbToHex(Number(rgbMatch[1]), Number(rgbMatch[2]), Number(rgbMatch[3])),
            alpha: rgbMatch[4] === undefined ? 1 : parseFloat(rgbMatch[4]),
        };
    }

    if (/^#[0-9a-f]{3}$/i.test(value) || /^#[0-9a-f]{6}$/i.test(value)) {
        return { hex: value.length === 4 ? expandShorthandHex(value) : value, alpha: 1 };
    }

    // Eight-digit hex carries alpha in the last pair.
    if (/^#[0-9a-f]{8}$/i.test(value)) {
        return { hex: value.slice(0, 7), alpha: parseInt(value.slice(7), 16) / 255 };
    }

    return null;
}

function expandShorthandHex(hex) {
    return '#' + hex[1] + hex[1] + hex[2] + hex[2] + hex[3] + hex[3];
}

function formatColor(hex, alpha, format) {
    if (format !== 'rgba') {
        return hex;
    }
    const { red, green, blue } = hexToRgb(hex);
    return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
}

ko.bindingHandlers.colorPicker = {
    init: function (element, valueAccessor) {
        const options = ko.unwrap(valueAccessor());
        const colorObservable = options.color;
        const format = options.format || 'hex';

        const initialColor = parseColor(ko.unwrap(colorObservable)) || { hex: '#000000', alpha: 1 };

        // Guards the two-way sync: writing to the observable re-enters this binding
        // through its own subscription.
        let synchronizing = false;

        const swatch = document.createElement('input');
        swatch.type = 'color';
        swatch.value = initialColor.hex;
        swatch.setAttribute('aria-label', element.getAttribute('placeholder') || 'Select a color');

        const inputGroup = element.closest('.input-group');
        const existingAddon = inputGroup && inputGroup.querySelector('.input-group-addon');

        if (existingAddon) {
            swatch.className = `${SWATCH_CLASS} ${SWATCH_CLASS}--overlay`;
            existingAddon.classList.add(`${SWATCH_CLASS}-host`);
            existingAddon.appendChild(swatch);
        } else {
            swatch.className = SWATCH_CLASS;
            element.parentNode.insertBefore(swatch, element.nextSibling);
        }

        // `type="color"` carries no alpha channel, so an rgba value needs a second
        // control for it. It sits below the input group rather than inside it, because
        // an `.input-group` is a table row and cannot stack.
        let alphaSlider = null;
        let alphaReadout = null;
        let alphaWidthObserver = null;

        if (format === 'rgba') {
            const sliderId = `color-picker-alpha-${++alphaFieldSequence}`;
            const anchor = inputGroup || element;

            alphaSlider = document.createElement('input');
            alphaSlider.type = 'range';
            alphaSlider.className = ALPHA_CLASS;
            alphaSlider.id = sliderId;
            alphaSlider.min = '0';
            alphaSlider.max = '1';
            alphaSlider.step = '0.01';
            alphaSlider.value = String(initialColor.alpha);

            const label = document.createElement('label');
            label.className = 'color-picker-alpha-label';
            label.htmlFor = sliderId;
            label.textContent = arches?.translations?.opacity || 'Opacity';

            alphaReadout = document.createElement('output');
            alphaReadout.className = 'color-picker-alpha-value';
            alphaReadout.htmlFor = sliderId;

            const header = document.createElement('div');
            header.className = 'color-picker-alpha-header';
            header.append(label, alphaReadout);

            const field = document.createElement('div');
            field.className = ALPHA_FIELD_CLASS;
            field.append(header, alphaSlider);
            anchor.insertAdjacentElement('afterend', field);

            // The width has to be matched in script rather than CSS. The eleven call
            // sites size their input group differently — arches caps the one in graph
            // settings at 250px, while the map-styling forms let it fill a column — and
            // the field is a sibling, so `width: 100%` resolves against the form group
            // instead. Left alone the slider ran the full width of the form beneath a
            // quarter-width input.
            const matchAnchorWidth = () => {
                field.style.inlineSize = `${anchor.getBoundingClientRect().width}px`;
            };
            matchAnchorWidth();
            if (typeof ResizeObserver !== 'undefined') {
                alphaWidthObserver = new ResizeObserver(matchAnchorWidth);
                alphaWidthObserver.observe(anchor);
            }
        }

        if (!element.value) {
            element.value = formatColor(initialColor.hex, initialColor.alpha, format);
        }

        function writeToObservable(hex, alpha) {
            if (!ko.isObservable(colorObservable)) {
                return;
            }
            synchronizing = true;
            colorObservable(formatColor(hex, alpha, format));
            synchronizing = false;
        }

        function renderAlphaReadout(alpha) {
            if (alphaReadout) {
                alphaReadout.value = `${Math.round(alpha * 100)}%`;
            }
        }

        function showInControls(hex, alpha) {
            swatch.value = hex;
            if (alphaSlider) {
                alphaSlider.value = String(alpha);
            }
            renderAlphaReadout(alpha);
        }

        renderAlphaReadout(initialColor.alpha);

        function publishFromControls() {
            const alpha = alphaSlider ? parseFloat(alphaSlider.value) : 1;
            // The readout has to be refreshed here as well as in showInControls: this
            // path runs while dragging the slider, which never round-trips through the
            // observable, so the percentage would otherwise sit at its initial value.
            renderAlphaReadout(alpha);
            element.value = formatColor(swatch.value, alpha, format);
            writeToObservable(swatch.value, alpha);
        }

        swatch.addEventListener('input', publishFromControls);
        if (alphaSlider) {
            alphaSlider.addEventListener('input', publishFromControls);
        }

        // Only propagate once the typed value parses, so a half-typed "#ab" does not
        // clobber the observable.
        element.addEventListener('input', function () {
            const parsed = parseColor(element.value);
            if (!parsed) {
                return;
            }
            showInControls(parsed.hex, parsed.alpha);
            writeToObservable(parsed.hex, parsed.alpha);
        });

        if (ko.isObservable(colorObservable)) {
            const subscription = colorObservable.subscribe(function (newValue) {
                if (synchronizing) {
                    return;
                }
                const parsed = parseColor(newValue);
                if (!parsed) {
                    return;
                }
                element.value = formatColor(parsed.hex, parsed.alpha, format);
                showInControls(parsed.hex, parsed.alpha);
            });

            ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                subscription.dispose();
            });
        }

        ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            alphaWidthObserver?.disconnect();
        });
    }
};

ko.bindingHandlers.colorPicker.init = ko.bindingHandlers.colorPicker.init.bind(ko.bindingHandlers.colorPicker);
export default ko.bindingHandlers.colorPicker;
