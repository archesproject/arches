:warning: = Breaking change

## 3.1.0
##### 2017-Aug-25
* Provide shrink as a public method (#90)

## 3.0.0
##### 2017-Feb-12
* :warning: shelf-pack is now a scoped package under the @mapbox namespace

## 2.0.1
##### 2016-Aug-11
* Remember original size of free bins and use that for packing free space (#29)

## 2.0.0
##### 2016-Aug-08
* Avoid id collisions by updating `maxId` if a numeric `id` is supplied (#28)
* Skip free bins if they are more wasteful than free shelves (#25)
* Prefer numeric Bin ids over strings (3x perf boost)
* :warning: Remove convenience `width`, `height` properties from Bin object, use only `w`, `h`
* Reference counting (see #20 or README)
  * Each bin now gets a unique id.  An id can be passed as optional param to the
    `packOne()` function, otherwise a numeric id will be generated.
  * Bins are automatically reference counted (i.e. a newly packed Bin will have a `refcount` of 1).
  * Functions `ref(bin)` and `unref(bin)` track which bins are being used.
  * When a Bin's `refcount` decrements to 0, the Bin will be marked as free,
    and its space may be reused by the packing code.

## 1.1.0
##### 2016-Jul-15
* Release as ES6 module alongside UMD build, add `jsnext:main` to `package.json`

## 1.0.0
##### 2016-Mar-29
* :warning: Rename `allocate()` -> `packOne()` for API consistency
* Add `autoResize` option (#7)
* Add `clear()` method
* Generate API docs (#9)
* Add `pack()` batch allocator
* Add benchmarks (#2)
* :warning: Return `null` instead of `{-1,-1}` on failed allocation (#1)
