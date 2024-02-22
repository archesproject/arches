// Cannot find a way to import this type from vue
// Copied from https://github.com/vuejs/core/blob/v3.4.19/packages/reactivity/src/ref.ts

declare const RefSymbol: unique symbol;
export declare const RawSymbol: unique symbol;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export interface Ref<T = any> {
  value: T
  /**
   * Type differentiator only.
   * We need this to be in public d.ts but don't want it to show up in IDE
   * autocomplete, so we use a private Symbol instead.
   */
  [RefSymbol]: true
}
