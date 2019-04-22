define([
    'knockout'
], function(ko) {
    var WorkflowSelect = function() {
        var self = this;
        self.workflows = ko.observableArray([
            {
                name: "Application Area",
                bgColor: "#87bceb",
                circleColor: "#a7cdf0",
                icon: "fa-building-o",
                desc: "An area that may be re-developed pr newly built"
            },
            {
                name: "Communication",
                bgColor: "#5fa2dd",
                circleColor: "#88bae6",
                icon: "fa-comment-o",
                desc: "A conversation via phone, email, or other channel"
            },
            {
                name: "Consultation",
                bgColor: "#5fa2dd",
                circleColor: "#88bae6",
                icon: "fa-file-text-o",
                desc: "Advice on the potential work related to a development area"
            },
            {
                name: "Application Area",
                bgColor: "#87bceb",
                circleColor: "#a7cdf0",
                icon: "fa-building-o",
                desc: "An area that may be re-developed pr newly built"
            },
            {
                name: "Communication",
                bgColor: "#5fa2dd",
                circleColor: "#88bae6",
                icon: "fa-comment-o",
                desc: "A conversation via phone, email, or other channel"
            },
            {
                name: "Consultation",
                bgColor: "#5fa2dd",
                circleColor: "#88bae6",
                icon: "fa-file-text-o",
                desc: "Advice on the potential work related to a development area"
            },
            {
                name: "Application Area",
                bgColor: "#87bceb",
                circleColor: "#a7cdf0",
                icon: "fa-building-o",
                desc: "An area that may be re-developed pr newly built"
            },
            {
                name: "Communication",
                bgColor: "#5fa2dd",
                circleColor: "#88bae6",
                icon: "fa-comment-o",
                desc: "A conversation via phone, email, or other channel"
            },
            {
                name: "Consultation",
                bgColor: "#5fa2dd",
                circleColor: "#88bae6",
                icon: "fa-file-text-o",
                desc: "Advice on the potential work related to a development area"
            },
            {
                name: "Application Area",
                bgColor: "#87bceb",
                circleColor: "#a7cdf0",
                icon: "fa-building-o",
                desc: "An area that may be re-developed pr newly built"
            },
            {
                name: "Communication",
                bgColor: "#5fa2dd",
                circleColor: "#88bae6",
                icon: "fa-comment-o",
                desc: "A conversation via phone, email, or other channel"
            },
            {
                name: "Consultation",
                bgColor: "#5fa2dd",
                circleColor: "#88bae6",
                icon: "fa-file-text-o",
                desc: "Advice on the potential work related to a development area"
            },
            {
                name: "Application Area",
                bgColor: "#87bceb",
                circleColor: "#a7cdf0",
                icon: "fa-building-o",
                desc: "An area that may be re-developed pr newly built"
            },
            {
                name: "Communication",
                bgColor: "#5fa2dd",
                circleColor: "#88bae6",
                icon: "fa-comment-o",
                desc: "A conversation via phone, email, or other channel"
            },
            {
                name: "Consultation",
                bgColor: "#5fa2dd",
                circleColor: "#88bae6",
                icon: "fa-file-text-o",
                desc: "Advice on the potential work related to a development area"
            }
        ]);
    };
    return WorkflowSelect;
});