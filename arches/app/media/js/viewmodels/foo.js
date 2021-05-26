define([
    'knockout', 
    'knockout-mapping', 
    'underscore', 
    'moment', 
    'report-templates',
    'models/report',
    'bindings/let', 
    'views/components/simple-switch',
    'views/components/foo'
], function(ko, koMapping, _, moment, reportLookup, ReportModel) {
    var FooViewModel = function(params) {
        var self = this;

        
        console.log("foo vm init", self, params, reportLookup, reportLookup[params.report_template_id])
        
        this.bar = ko.observable(reportLookup[params.report_template_id])
        
        this.loading = ko.observable(false)

        
        // ko.components.defaultLoader.getConfig('custom_summary_report', function(foo) {
        //     var foobar = function(ddd){ console.log(ddd, foo); return foo.template };

        //     ko.components.defaultLoader.loadTemplate('custom_summary_report', { element: 'foo'}, foobar)
        //     foobar()
        // })


        // ko.components.get('custom_summary_report', function(ccc) {
        //     var foo = $('.foo')[0];
        //     var bar = ccc.createViewModel()
        //     console.log("dsfs", ccc, foo, bar, document.querySelector('.foo'))


            // ko.renderTemplate('custom_summary_report', ccc.createViewModel(), {}, document.querySelector('.foo'), "replaceNode")


            // ko.renderTemplate(
            //     "custom_summary_report",
            //     bar,
            //     {
            //         afterRender: function(renderedElement) {
            //             console.log("rendered!");
            //         }
            //     },
            //     foo,
            //     "replaceNode"
            // );

            // ko.cleanNode(foo);
            // ko.applyBindings(ccc.template, foo)
            // ko.utils.extend(bar)

            // ko.components.defaultLoader.loadTemplate('foo', {}, ccc.template)



        // })



        

        // ko.applyBindings(new ReportModel())
        this.foo = ko.observable(true)

    };
    return FooViewModel;
});
