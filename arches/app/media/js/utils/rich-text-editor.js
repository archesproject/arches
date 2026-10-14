import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import { Placeholder } from '@tiptap/extensions';
import { Image } from '@tiptap/extension-image';
import { TableKit } from '@tiptap/extension-table';


/**
 * Creates a Tiptap rich text editor inside `element`. Shared by the knockout `tiptap` binding and Vue components,
 * which each add their own toolbar. Returns the Tiptap `editor`, with `getValue()` and
 * `setContent(html)` for keeping it in sync with a value.
 * @param {HTMLElement} element - the element to create the editing area in
 * @param {string} [options.content] - the initial HTML
 * @param {boolean} [options.editable] - whether editor can be used or is readonly 
 * @param {string} [options.direction] - Arches i18n ltr/rtl
 * @param {string} [options.placeholder] - placeholder value set in node
 * @param {function} [options.onChange] - called with the HTML ('' when empty) after each change
 */
export default function createRichTextEditor(element, {
    content = '',
    editable = true,
    direction = 'ltr',
    placeholder = '',
    onChange,
} = {}) {
    const editor = new Editor({
        element,
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
    element.classList.add('rich-text-editor');
    editor.view.dom.dir = direction;

    const getValue = () => editor.isEmpty ? '' : editor.getHTML();
    editor.on('update', () => onChange?.(getValue()));

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
