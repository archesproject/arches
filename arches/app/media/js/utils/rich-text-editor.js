import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import { Placeholder } from '@tiptap/extensions';
import { Image } from '@tiptap/extension-image';
import { TableKit } from '@tiptap/extension-table';


/**
 * Creates the Tiptap editor used by Arches rich text editors, so the Knockout and Vue components save the same HTML.
 * The caller attaches it to the page with `editor.mount(element)`. Returns the Tiptap `editor`, with `getValue()` and
 * `setContent(html)` for keeping it in sync with a value.
 * @param {string} [options.content] - the initial HTML
 * @param {boolean} [options.editable] - whether editor can be used or is readonly
 * @param {string} [options.placeholder] - placeholder value set in node
 */
export default function createRichTextEditor({
    content = '',
    editable = true,
    placeholder = '',
} = {}) {
    const editor = new Editor({
        content,
        editable,
        extensions: [
            StarterKit.configure({
                link: { openOnClick: false, HTMLAttributes: { target: null, rel: null } },
                // don't add an empty paragraph to the end of saved content
                trailingNode: false,
            }),
            Image.configure({ inline: true, allowBase64: false }),
            TableKit,
            Placeholder.configure({ placeholder }),
        ],
    });

    const getValue = () => editor.isEmpty ? '' : editor.getHTML();

    return {
        editor,
        getValue,
        // replaces the content without an update event, or an undo step
        setContent: (html) => {
            if ((html || '') !== getValue()) {
                editor.chain()
                    .command(({ tr }) => tr.setMeta('addToHistory', false))
                    .setContent(html || '', { emitUpdate: false })
                    .run();
            }
        },
    };
}
