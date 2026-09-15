import ko from 'knockout';

/**
 * Image carousel binding, replacing knockstrap 1.3.2, which was Bootstrap 3-only and
 * unmaintained since 2016. Carries no Bootstrap dependency: its own markup, styles and
 * transition, styled by css/components/_carousel.scss.
 *
 *     data-bind="carousel: { content: { name: 'itemTemplate', data: images } }"
 *
 * Each item is `{ src, alt }`, matching what reports/image.js builds. `content.name`
 * names an optional template rendered into each slide's caption.
 */

function readItems(content) {
    const data = ko.unwrap(content.data);
    return Array.isArray(data) ? data : [];
}

ko.bindingHandlers.carousel = {
    init: function (element, valueAccessor) {
        const options = ko.unwrap(valueAccessor()) || {};
        const content = options.content;

        if (!content || !content.data) {
            throw new Error('carousel binding requires content.data');
        }

        const interval = ko.unwrap(options.interval) ?? 0;

        element.classList.add('arches-carousel');
        element.setAttribute('role', 'region');
        element.setAttribute('aria-roledescription', 'carousel');

        const track = document.createElement('div');
        track.className = 'arches-carousel-track';

        const indicators = document.createElement('div');
        indicators.className = 'arches-carousel-indicators';
        indicators.setAttribute('role', 'tablist');

        let currentIndex = 0;
        let slideCount = 0;
        let autoAdvanceTimer = null;

        const previousButton = buildControl('previous', '‹');
        const nextButton = buildControl('next', '›');

        element.appendChild(previousButton);
        element.appendChild(track);
        element.appendChild(nextButton);
        element.appendChild(indicators);

        function buildControl(direction, glyph) {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `arches-carousel-control arches-carousel-control--${direction}`;
            button.setAttribute('aria-label', direction === 'previous' ? 'Previous image' : 'Next image');
            button.textContent = glyph;
            button.addEventListener('click', function () {
                goTo(direction === 'previous' ? currentIndex - 1 : currentIndex + 1);
            });
            return button;
        }

        function goTo(index) {
            if (slideCount === 0) {
                return;
            }
            currentIndex = ((index % slideCount) + slideCount) % slideCount;
            applySelection();
        }

        function applySelection() {
            Array.from(track.children).forEach(function (slide, index) {
                const isCurrent = index === currentIndex;
                slide.classList.toggle('is-current', isCurrent);
                slide.setAttribute('aria-hidden', String(!isCurrent));
            });
            Array.from(indicators.children).forEach(function (indicator, index) {
                const isCurrent = index === currentIndex;
                indicator.classList.toggle('is-current', isCurrent);
                indicator.setAttribute('aria-selected', String(isCurrent));
                indicator.tabIndex = isCurrent ? 0 : -1;
            });
            const multiple = slideCount > 1;
            previousButton.hidden = !multiple;
            nextButton.hidden = !multiple;
            indicators.hidden = !multiple;
        }

        function renderCaption(slide, item) {
            if (!content.name) {
                return;
            }
            const source = document.getElementById(content.name);
            if (!source || !source.innerHTML.trim()) {
                return;
            }
            const caption = document.createElement('div');
            caption.className = 'arches-carousel-caption';
            slide.appendChild(caption);
            ko.renderTemplate(content.name, item, {}, caption, 'replaceChildren');
        }

        function render() {
            const items = readItems(content);
            slideCount = items.length;

            track.replaceChildren();
            indicators.replaceChildren();

            items.forEach(function (item, index) {
                const slide = document.createElement('div');
                slide.className = 'arches-carousel-slide';
                slide.setAttribute('role', 'group');
                slide.setAttribute('aria-roledescription', 'slide');
                slide.setAttribute('aria-label', `${index + 1} of ${items.length}`);

                const image = document.createElement('img');
                image.className = 'arches-carousel-image';
                // Assigned as properties, never interpolated into markup, so a
                // filename can never be read as HTML.
                image.src = ko.unwrap(item.src) || '';
                image.alt = ko.unwrap(item.alt) || '';
                slide.appendChild(image);

                renderCaption(slide, item);
                track.appendChild(slide);

                const indicator = document.createElement('button');
                indicator.type = 'button';
                indicator.className = 'arches-carousel-indicator';
                indicator.setAttribute('role', 'tab');
                indicator.setAttribute('aria-label', `Show image ${index + 1}`);
                indicator.addEventListener('click', function () {
                    goTo(index);
                });
                indicators.appendChild(indicator);
            });

            if (currentIndex >= slideCount) {
                currentIndex = 0;
            }
            applySelection();
            restartAutoAdvance();
        }

        function restartAutoAdvance() {
            if (autoAdvanceTimer) {
                clearInterval(autoAdvanceTimer);
                autoAdvanceTimer = null;
            }
            if (interval > 0 && slideCount > 1) {
                autoAdvanceTimer = setInterval(function () {
                    goTo(currentIndex + 1);
                }, interval);
            }
        }

        element.addEventListener('keydown', function (event) {
            if (event.key === 'ArrowLeft') {
                goTo(currentIndex - 1);
            } else if (event.key === 'ArrowRight') {
                goTo(currentIndex + 1);
            }
        });

        const renderSubscription = ko.computed(render, null, {
            disposeWhenNodeIsRemoved: element,
        });

        ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            if (autoAdvanceTimer) {
                clearInterval(autoAdvanceTimer);
            }
            renderSubscription.dispose();
        });

        // The binding owns this subtree; Knockout must not also bind it.
        return { controlsDescendantBindings: true };
    }
};

export default ko.bindingHandlers.carousel;
