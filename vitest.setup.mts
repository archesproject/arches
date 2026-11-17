import { vi } from 'vitest';

vi.mock('arches', () => ({
    default: '',
}));

vi.mock('vue3-gettext', () => ({
    useGettext: () => ({
        $gettext: (text: string) => (text)
    })
}));
