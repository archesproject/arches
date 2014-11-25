define(['jquery', 'backbone', 'knockout'], function ($, Backbone, ko) {
    // add knockout binding handlers for select2
    ko.bindingHandlers.select2 = {
        init: function(el, valueAccessor, allBindingsAccessor, viewModel) {
          ko.utils.domNodeDisposal.addDisposeCallback(el, function() {
            $(el).select2('destroy');
          });

          var allBindings = allBindingsAccessor(),
              select2 = ko.utils.unwrapObservable(allBindings.select2);

          $(el).select2(select2);
        },
        update: function (el, valueAccessor, allBindingsAccessor, viewModel) {
            var allBindings = allBindingsAccessor();

            if ("value" in allBindings) {
                $(el).select2("val", allBindings.value());
            } else if ("selectedOptions" in allBindings) {
                var converted = [];
                var textAccessor = function(value) { return value; };
                if ("optionsText" in allBindings) {
                    textAccessor = function(value) {
                        var valueAccessor = function (item) { return item; }
                        if ("optionsValue" in allBindings) {
                            valueAccessor = function (item) { return item[allBindings.optionsValue]; }
                        }
                        var items = $.grep(allBindings.options(), function (e) { return valueAccessor(e) == value});
                        if (items.length == 0 || items.length > 1) {
                            return "UNKNOWN";
                        }
                        return items[0][allBindings.optionsText];
                    }
                }
                $.each(allBindings.selectedOptions(), function (key, value) {
                    converted.push({id: value, text: textAccessor(value)});
                });
                $(el).select2("data", converted);
            }
        }
    };

    return Backbone.View.extend({
        
        events: function(){
            return {
                'click #submitform': 'submit'  
            }
        },

        constructor: function (options) {
            Backbone.View.apply(this, arguments);

            ko.applyBindings(this.viewModel, this.el);
            return this;
        },

        initialize: function() {
            var self = this;
            this.form = this.$el;
            // parse then restringify JSON data to ensure whitespace is identical
            this._rawdata = ko.toJSON(JSON.parse(this.form.find('#formdata').val()));
            this.viewModel = JSON.parse(this._rawdata);
            this.viewModel._editing = {};
            this.viewModel._defaults = {};

            $('input,select').change(function() {
                var isDirty = self.isDirty();
                self.trigger('change', isDirty);
            });
        },

        isDirty: function () {
            return this.getData() !== this._rawdata;
        },

        getData: function(){
            return ko.toJSON(this.viewModel);
        },

        validate: function(){
            return true;
        },

        submit: function(){
            if (this.validate()){
                this.form.find('#formdata').val(this.getData());
                this.form.submit(); 
            }
        }
    });
});