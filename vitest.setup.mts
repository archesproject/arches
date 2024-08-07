import { beforeAll, vi } from 'vitest';
import '@/arches/declarations.d.ts';

beforeAll(() => {
    vi.mock('vue3-gettext', () => ({
        useGettext: () => ({
            $gettext: (text: string) => (text)
        })
    }));
});
