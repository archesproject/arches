import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';

import ExampleComponent from '@/ExampleComponent.vue';


describe('ExampleComponent', () => {
    it('renders correctly', () => {
        const wrapper = mount(ExampleComponent);
        expect(wrapper.exists()).toBeTruthy();
    });


    it('renders h1 element with correct text', () => {
        const wrapper = mount(ExampleComponent);
        expect(wrapper.find('h1').text()).toBe('Hello from the template!');
    });


    it('applies scoped styles to h1 element', () => {
        const wrapper = mount(ExampleComponent);
        const h1 = wrapper.find('h1');
        expect(h1.classes()).toContain('header');
    });
});
