import { beforeAll, vi } from 'vitest';
import '@/{{ project_name }}/declarations.d.ts';


beforeAll(() => {
    vi.mock('vue3-gettext', () => ({
        useGettext: () => ({
            $gettext: (text: string) => (text)
        })
    }));
});
