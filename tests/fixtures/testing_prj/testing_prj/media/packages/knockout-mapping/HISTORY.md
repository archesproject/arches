## 2.6.0 (2016-02-28)

* Issue [#124](https://github.com/SteveSanderson/knockout.mapping/issues/124): Use hasOwnProperty to check for bucket existence
* Small performance improvements [e6c5631](https://github.com/crissdev/knockout.mapping/commit/e6c56313d22375e0e1ac7242f18dce9811577ad2), [f97d5cd](https://github.com/crissdev/knockout.mapping/commit/f97d5cde145962af919a6472d22418f9f0f43626), [57a0b56](https://github.com/crissdev/knockout.mapping/commit/57a0b56c6368bb3b8816fb0d78c35820aa719bf3)
* Issue [#96](https://github.com/SteveSanderson/knockout.mapping/issues/96): Fix incorrect handling of properties with periods
* Issue [#205](https://github.com/SteveSanderson/knockout.mapping/issues/205): Allow JSON.stringify parameters to be specified to ko.mapping.toJSON
* Issue [#9](https://github.com/crissdev/knockout.mapping/issues/9): Fix pure computeds are treated the same as deferred, not auto-evaluated after mapping

## 2.5.0 (2015-02-12)

* Remove deprecated methods (`updateFromJS` and `updateFromJSON`) 
* Issue [#1](https://github.com/crissdev/knockout.mapping/issues/1): Compatibility with Knockout 3.x may still be a problem
* Issue [#4](https://github.com/crissdev/knockout.mapping/issues/4): Library is not exported in ko namespace for CommonJS/Node

## 2.4.1 (2013-02-08) 

* Added mappedGet for observable arrays
* Issue [#134](https://github.com/SteveSanderson/knockout.mapping/issues/134): Throttle issue using mapping
* Issue [#135](https://github.com/SteveSanderson/knockout.mapping/issues/135): Why is custom update for observableArray firing twice when using mapping plugin?

## 2.4.0 (2013-02-04)

* Removed asynchronous processing that was used to reset mapping nesting
* Improved getType performance

## 2.3.5 (2012-12-10)

* Issue [#121](https://github.com/SteveSanderson/knockout.mapping/issues/121): Added functionality so that explicit declared none observable members on a ViewModel will remain none observable after mapping

## 2.3.4 (2012-11-22)

* Issue [#114](https://github.com/SteveSanderson/knockout.mapping/issues/114): Added new "observe" array to options

## 2.3.3 (2012-10-30)

* Fixed issue [#105](https://github.com/SteveSanderson/knockout.mapping/issues/105), [#111](https://github.com/SteveSanderson/knockout.mapping/issues/111): Update callback is not being called
* Fixed issue [#107](https://github.com/SteveSanderson/knockout.mapping/issues/107): String values in mapping cause infinite recursion in extendObject

## 2.3.2 (2012-08-20)

* Fixed issue [#86](https://github.com/SteveSanderson/knockout.mapping/issues/86): Don't update properties on object with update callback

## 2.3.1 (2012-08-06)

* Fixed issue [#33](https://github.com/SteveSanderson/knockout.mapping/issues/33): Create method in mappings receive meaningless options.parent for observableArray properties
* Fixed issue [#99](https://github.com/SteveSanderson/knockout.mapping/issues/99): Updating throttled observable
* Fixed issue [#100](https://github.com/SteveSanderson/knockout.mapping/issues/100): private variable leaks onto window object

## 2.3.0 (2012-07-31)

* Added support for not mapping certain array elements (return "options.skip" from your create callback)
* Fixed issue [#91](https://github.com/SteveSanderson/knockout.mapping/issues/91): "wrap" function makes computed writable
* Fixed issue [#94](https://github.com/SteveSanderson/knockout.mapping/issues/94): Bug/problem with ignore argument in mapping.fromJS

