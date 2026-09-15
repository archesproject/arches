import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import ko from 'knockout';

import './carousel.js';

/**
 * Covers the carousel binding that replaced knockstrap 1.3.2.
 *
 * The image report is the only consumer and it needs a resource with uploaded
 * images to render, so it sits outside the visual-regression harness. These
 * assertions are the safety net for it.
 */

function applyCarousel(images, options = {}) {
    const element = document.createElement('div');
    document.body.appendChild(element);
    ko.applyBindingsToNode(element, {
        carousel: { content: { name: 'itemTemplate', data: images }, ...options },
    });
    return element;
}

describe('carousel binding', () => {
    beforeEach(() => {
        document.body.replaceChildren();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('renders one slide and one indicator per image', () => {
        const element = applyCarousel([
            { src: '/a.png', alt: 'first' },
            { src: '/b.png', alt: 'second' },
            { src: '/c.png', alt: 'third' },
        ]);

        expect(element.querySelectorAll('.arches-carousel-slide')).toHaveLength(3);
        expect(element.querySelectorAll('.arches-carousel-indicator')).toHaveLength(3);
        expect(element.querySelector('.arches-carousel-image').src).toContain('/a.png');
        expect(element.querySelector('.arches-carousel-image').alt).toBe('first');
    });

    it('marks only the first slide current on render', () => {
        const element = applyCarousel([{ src: '/a.png' }, { src: '/b.png' }]);
        const slides = element.querySelectorAll('.arches-carousel-slide');

        expect(slides[0].classList.contains('is-current')).toBe(true);
        expect(slides[1].classList.contains('is-current')).toBe(false);
        expect(slides[1].getAttribute('aria-hidden')).toBe('true');
    });

    it('wraps in both directions so the controls never dead-end', () => {
        const element = applyCarousel([{ src: '/a.png' }, { src: '/b.png' }]);
        const slides = element.querySelectorAll('.arches-carousel-slide');

        // Backwards from the first slide lands on the last.
        element.querySelector('.arches-carousel-control--previous').click();
        expect(slides[1].classList.contains('is-current')).toBe(true);

        // Forwards from the last returns to the first.
        element.querySelector('.arches-carousel-control--next').click();
        expect(slides[0].classList.contains('is-current')).toBe(true);
    });

    it('jumps to the indicator that was clicked', () => {
        const element = applyCarousel([{ src: '/a.png' }, { src: '/b.png' }, { src: '/c.png' }]);

        element.querySelectorAll('.arches-carousel-indicator')[2].click();

        const slides = element.querySelectorAll('.arches-carousel-slide');
        expect(slides[2].classList.contains('is-current')).toBe(true);
        expect(element.querySelectorAll('.arches-carousel-indicator')[2].getAttribute('aria-selected')).toBe('true');
    });

    it('hides navigation when there is nothing to navigate between', () => {
        const element = applyCarousel([{ src: '/only.png' }]);

        expect(element.querySelector('.arches-carousel-control--next').hidden).toBe(true);
        expect(element.querySelector('.arches-carousel-indicators').hidden).toBe(true);
    });

    it('re-renders when the observable image list changes', () => {
        const images = ko.observableArray([{ src: '/a.png' }]);
        const element = applyCarousel(images);

        expect(element.querySelectorAll('.arches-carousel-slide')).toHaveLength(1);

        images.push({ src: '/b.png' });

        expect(element.querySelectorAll('.arches-carousel-slide')).toHaveLength(2);
        expect(element.querySelector('.arches-carousel-control--next').hidden).toBe(false);
    });

    it('assigns image attributes as properties so a filename cannot inject markup', () => {
        const element = applyCarousel([
            { src: '/x.png"><script>alert(1)</script>', alt: '"><img onerror=alert(1)>' },
        ]);

        expect(element.querySelectorAll('script')).toHaveLength(0);
        expect(element.querySelectorAll('img')).toHaveLength(1);
        expect(element.querySelector('.arches-carousel-image').alt).toBe('"><img onerror=alert(1)>');
    });

    it('does not auto-advance unless an interval is given', () => {
        vi.useFakeTimers();
        const element = applyCarousel([{ src: '/a.png' }, { src: '/b.png' }]);

        vi.advanceTimersByTime(60_000);

        expect(element.querySelectorAll('.arches-carousel-slide')[0].classList.contains('is-current')).toBe(true);
    });

    it('auto-advances when an interval is given, and stops once disposed', () => {
        vi.useFakeTimers();
        const element = applyCarousel([{ src: '/a.png' }, { src: '/b.png' }], { interval: 1000 });

        vi.advanceTimersByTime(1000);
        expect(element.querySelectorAll('.arches-carousel-slide')[1].classList.contains('is-current')).toBe(true);

        const clearIntervalSpy = vi.spyOn(globalThis, 'clearInterval');
        ko.cleanNode(element);
        expect(clearIntervalSpy).toHaveBeenCalled();
    });
});
