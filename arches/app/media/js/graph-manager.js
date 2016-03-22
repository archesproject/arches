require([
    'jquery',
    'd3',
    'views/page-view',
    'plugins/nifty',
    'chosen',
    'bootstrap-nifty'
], function($, d3, PageView) {
    var viewModel = {};

    var root = {
        "name": "889a5542-add8-4cc5-992e-10a183e7ca32",
        "property": "",
        "entitytypeid": "MARITIME HERITAGE.E18",
        "value": "",
        "children": [
            {
                "name": "e8ea6e75-06ea-44ea-af81-d16434ae592e",
                "property": "P53",
                "entitytypeid": "PLACE.E53",
                "value": "",
                "children": [
                    {
                        "name": "bb173e11-8c6c-435d-bbbc-cc54b23303ac",
                        "property": "P87",
                        "entitytypeid": "SPATIAL COORDINATES_GEOMETRY.E47",
                        "value": "POLYGON ((-0.7242682653884868 54.5386654478622650, -0.7215216833576376 54.5368229924573810, -0.7207492071614455 54.5373707581581610, -0.7233241278153981 54.5391633945041220, -0.7242682653884868 54.5386654478622650))",
                        "children": [
                            {
                                "name": "e57f10b6-0f1e-44f3-ae76-f3013defb494",
                                "property": "P2",
                                "entitytypeid": "GEOMETRY QUALIFIER.E55",
                                "value": "Circumscribed Polygon",
                                "children": []
                            }
                        ]
                    },
                    {
                        "name": "f488c18c-2eff-48eb-966e-279371458bc4",
                        "property": "P87",
                        "entitytypeid": "SPATIAL COORDINATES_GEOMETRY.E47",
                        "value": "POINT (-0.7218003251307087 54.5376910321448560)",
                        "children": [
                            {
                                "name": "479dfd86-a472-4c5c-9b95-39b6a10d39fa",
                                "property": "P2",
                                "entitytypeid": "GEOMETRY QUALIFIER.E55",
                                "value": "Vicinity Point",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "name": "deb416d1-b069-4eb3-9c5b-9ec79001b725",
                "property": "-P70",
                "entitytypeid": "ARCHES RECORD.E31",
                "value": "",
                "children": [
                    {
                        "name": "651587ad-11a6-4e77-9263-50a71085588e",
                        "property": "P48",
                        "entitytypeid": "REFERENCE NUMBER (INTERNAL).E42",
                        "value": "889a5542-add8-4cc5-992e-10a183e7ca32",
                        "children": []
                    },
                    {
                        "name": "20fe7074-8ba9-4960-88e2-8fd023fa97bb",
                        "property": "-P94",
                        "entitytypeid": "CREATION EVENT.E65",
                        "value": "",
                        "children": [
                            {
                                "name": "cfe8f51b-4cc4-48bc-9b79-63dfe38dcaef",
                                "property": "P4",
                                "entitytypeid": "TIME-SPAN_CREATION EVENT.E52",
                                "value": "",
                                "children": [
                                    {
                                        "name": "047ae196-9c90-4446-87c8-4bd4dded4cb9",
                                        "property": "P78",
                                        "entitytypeid": "DATE OF COMPILATION.E50",
                                        "value": "2013-12-13 05:39:24",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "name": "2eaf4d15-d4b7-49d7-9d2a-f99c39180bb0",
                                "property": "P14",
                                "entitytypeid": "COMPILER_PERSON.E21",
                                "value": "",
                                "children": [
                                    {
                                        "name": "40451957-9f48-42bf-973b-8effeb687b40",
                                        "property": "P131",
                                        "entitytypeid": "COMPILER.E82",
                                        "value": "dwuthrich",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "name": "dc11bbac-7d29-4b4e-8d89-147dea404ded",
                                "property": "-P134",
                                "entitytypeid": "UPDATE EVENT.E65",
                                "value": "",
                                "children": [
                                    {
                                        "name": "c9d40176-dd15-4ac8-b992-695ae52ba5ad",
                                        "property": "P4",
                                        "entitytypeid": "TIME-SPAN_UPDATE EVENT.E52",
                                        "value": "",
                                        "children": [
                                            {
                                                "name": "88b7d4ce-d0a8-41b1-a277-cc4620a21230",
                                                "property": "P78",
                                                "entitytypeid": "DATE OF LAST UPDATE.E50",
                                                "value": "2014-02-27 14:17:35.029000",
                                                "children": []
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "name": "d896631b-dac0-43ff-8e21-f335da321fc5",
                "property": "P1",
                "entitytypeid": "NAME.E41",
                "value": "HMS Carlisle",
                "children": [
                    {
                        "name": "d8e79a7b-81c6-423b-b70b-64d9be961a4a",
                        "property": "P2",
                        "entitytypeid": "NAME TYPE.E55",
                        "value": "Primary",
                        "children": []
                    }
                ]
            },
            {
                "name": "4fce058e-7d30-4cba-bebd-55f3ce2c9bb2",
                "property": "-P108",
                "entitytypeid": "PRODUCTION.E12",
                "value": "",
                "children": [
                    {
                        "name": "8d56fbd0-511f-4c87-be1c-b08b2e22fe56",
                        "property": "-P41",
                        "entitytypeid": "PHASE TYPE ASSIGNMENT.E17",
                        "value": "",
                        "children": [
                            {
                                "name": "e4df926c-a673-4fda-8f14-034834bada76",
                                "property": "P42",
                                "entitytypeid": "CULTURAL PERIOD.E55",
                                "value": "Second World War",
                                "children": []
                            },
                            {
                                "name": "7f1fcb55-9dd1-4d13-ba97-db92d56bac29",
                                "property": "P42",
                                "entitytypeid": "MARITIME HERITAGE TYPE.E55",
                                "value": "Landing Craft Infantry",
                                "children": []
                            },
                            {
                                "name": "af4f92fe-e72b-4f96-8027-b6088e66c1da",
                                "property": "P4",
                                "entitytypeid": "TIME-SPAN_PHASE.E52",
                                "value": "",
                                "children": [
                                    {
                                        "name": "ae26e373-47c9-471f-8c55-e1a432ff4fa8",
                                        "property": "P78",
                                        "entitytypeid": "FROM DATE.E49",
                                        "value": "1939",
                                        "children": []
                                    },
                                    {
                                        "name": "6917eb17-728f-482e-9ad8-8bb58e3d5ac7",
                                        "property": "P78",
                                        "entitytypeid": "TO DATE.E49",
                                        "value": "1945",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "name": "24ae8061-fe8a-4da8-9689-0fee20d10a6d",
                "property": "P1",
                "entitytypeid": "NAME.E41",
                "value": "Test alternate name",
                "children": [
                    {
                        "name": "91d12042-41b6-44ac-8eec-1148951bce50",
                        "property": "P2",
                        "entitytypeid": "NAME TYPE.E55",
                        "value": "Pseudonym",
                        "children": []
                    }
                ]
            },
            {
                "name": "cd0f97d2-472f-43a4-a450-6cfa34cfff22",
                "property": "P104",
                "entitytypeid": "RIGHT.E30",
                "value": "",
                "children": [
                    {
                        "name": "095669e6-3a67-4ce3-a4a0-7fbd7bf3ea31",
                        "property": "-P94",
                        "entitytypeid": "PROTECTION EVENT.E65",
                        "value": "",
                        "children": [
                            {
                                "name": "e881c077-14a4-41d1-a5c6-c3464d1f151c",
                                "property": "P2",
                                "entitytypeid": "TYPE OF DESIGNATION OR PROTECTION.E55",
                                "value": "Listed Grade 1 - National Importance",
                                "children": []
                            },
                            {
                                "name": "5c651b6e-c003-44f7-ae5b-92381096618e",
                                "property": "P4",
                                "entitytypeid": "TIME SPAN OF DESIGNATION AND PROTECTION.E52",
                                "value": "",
                                "children": [
                                    {
                                        "name": "82969ed9-6714-4b69-a144-1c53d14b8b2b",
                                        "property": "P78",
                                        "entitytypeid": "DESIGNATION AND PROTECTION FROM DATE.E49",
                                        "value": "2014-01-14T08:00:00.000Z",
                                        "children": []
                                    },
                                    {
                                        "name": "2c92d725-3a5f-4ab7-bab6-5593e3c181a7",
                                        "property": "P78",
                                        "entitytypeid": "DESIGNATION AND PROTECTION TO DATE.E49",
                                        "value": "",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "name": "609b7854-7070-4cab-965f-065e2d198496",
                "property": "-P34",
                "entitytypeid": "CONDITION ASSESSMENT.E14",
                "value": "",
                "children": [
                    {
                        "name": "49448167-9310-4fc9-b238-6477583879de",
                        "property": "P35",
                        "entitytypeid": "CONDITION STATE.E3",
                        "value": "",
                        "children": [
                            {
                                "name": "610c0657-d601-4fee-a8e7-2bc6e50d448f",
                                "property": "P2",
                                "entitytypeid": "CONDITION TYPE.E55",
                                "value": "Very Bad",
                                "children": []
                            },
                            {
                                "name": "e9cb2b54-15a2-4516-82e3-c969ef03f254",
                                "property": "P4",
                                "entitytypeid": "DATE CONDITION ASSESSED.E49",
                                "value": "",
                                "children": []
                            }
                        ]
                    },
                    {
                        "name": "49448167-9310-4fc9-b238-6477583879de",
                        "property": "P35",
                        "entitytypeid": "CONDITION STATE.E3",
                        "value": "",
                        "children": [
                            {
                                "name": "610c0657-d601-4fee-a8e7-2bc6e50d448f",
                                "property": "P2",
                                "entitytypeid": "CONDITION TYPE.E55",
                                "value": "Good",
                                "children": []
                            },
                            {
                                "name": "e9cb2b54-15a2-4516-82e3-c969ef03f254",
                                "property": "P4",
                                "entitytypeid": "DATE CONDITION ASSESSED.E49",
                                "value": "May 14 2014",
                                "children": []
                            }
                        ]
                    }
                ]
            }
        ]
    };

    $("#crm").chosen({
	  	disable_search_threshold: 5,
	  	inherit_select_classes: true,
	  	width: '100%'
	});

	$("#property").chosen({
	  	disable_search_threshold: 15,
	  	inherit_select_classes: true,
	  	width: '100%'
	});

	$("#data-type").chosen({
	  	disable_search_threshold: 15,
	  	inherit_select_classes: true,
	  	width: '100%'
	});

	$("#node-group").chosen({
	  	disable_search_threshold: 15,
	  	inherit_select_classes: true,
	  	width: '100%'
	});

	$("#permissions").chosen({
	  	disable_search_threshold: 15,
	  	inherit_select_classes: true,
	  	width: '100%'
	});


//
// // 	Switches
// 	new Switchery(document.getElementById('node-required'), {size: 'small'});
// 	new Switchery(document.getElementById('node-cardinality'), {size: 'small'});



//	Library Panel
	$('#permissions-close').on('click', function (ev) {
		ev.preventDefault();
		$('#permissions-panel').fadeOut(100, "linear");

		//"unselect" permissions items
		$( "#user-grid>div" ).each(function() {
	    	$( this ).removeClass( "selected-card" );
	  	});
	});


	$('.library-card.permissions').on('click', function (ev) {
		ev.preventDefault();
		$(this).toggleClass("selected-card");
		$('#permissions-panel').fadeIn(100, "linear");

		//console.log('permission card clicked')
	});


	$('.library-card.graph-library').on('click', function (ev) {
		ev.preventDefault();

		// Clear all selected branches
		$( "#branch-grid>div" ).each(function() {
	    	$( this ).removeClass( "selected-card" );
	  	});

	  	//Highlight selected branch
		$(this).toggleClass("selected-card");
		$('#branch-panel').fadeIn(100, "linear");

		//console.log('permission card clicked')
	});


	$('.library-card.node-list').on('click', function (ev) {
		ev.preventDefault();
		$(this).toggleClass("selected-card");
	});


	$('#apply-permissions').on('click', function (ev) {
		ev.preventDefault();
		$('#confirm-permissions').fadeIn(100, "linear");
	});


	$('#clear-user-selection').on('click', function (ev) {
		ev.preventDefault();
	  	$( "#user-grid>div" ).each(function() {
	    	$( this ).removeClass( "selected-card" );
	  	});
	});


	$('#clear-node-selection').on('click', function (ev) {
		ev.preventDefault();
	  	$( "#node-grid>div" ).each(function() {
	    	$( this ).removeClass( "selected-card" );
	  	});
	});


//	Toggle all accounts when user selects "all"
	$('#all').on('click', function (ev) {
		ev.preventDefault();

		if ($('#all').hasClass("selected-card")) {
		    $( "#user-grid>div" ).each(function() {
		    	$( this ).addClass( "selected-card" );
		  	});

		} else {
		    console.log("update accounts to selected");
		    $( "#user-grid>div" ).each(function() {
		    	$( this ).removeClass( "selected-card" );
		  	});
		}

	});



//	Permissions Alert
	$('.permission-alert').on('click', function (ev) {
		ev.preventDefault();

		// Card Alert (Uncomment to show alert panel and notification text)
		$.niftyNoty({
		    type: 'danger',
		    container : '#permission-alert',
		    html : '<h4 class="alert-title">Parent Node is No Access</h4><p class="alert-message">You can not give this user [Permission] because they do not have access privileges for [Parent Node].</p><div class="mar-top"><button type="button" class="btn btn-mint" data-dismiss="noty">OK</button></div>',
		    closeBtn : false
		});

	});



//	Branch Panel
	$('#branch-close').on('click', function (ev) {
		ev.preventDefault();
		$('#branch-panel').fadeOut(100, "linear");

		//"unselect" branch items
		$( "#branch-grid>div" ).each(function() {
	    	$( this ).removeClass( "selected-card" );
	  	});

	});


	$('#branch-append').on('click', function (ev) {
		ev.preventDefault();

		// Card Alert (Uncomment to show alert panel and notification text)
		$.niftyNoty({
		    type: 'mint',
		    container : '#branch-alert',
		    html : '<h4 class="alert-title" style="color: #123;">Branch Added!</h4><p class="alert-message" style="color: #123;">You have successfully appended this branch to your resource graph.  Great job! </p><div class="mar-top"><button type="button" class="btn btn-mint" style="color: #123;" data-dismiss="noty">OK</button></div>',
		    closeBtn : false
		});

	});


//	Manage Visibility of Branch/Permissions Panels
	$('#nodes-tab').on('click', function (ev) {
		ev.preventDefault();

		// Close Branch if it is visible
		if ($("#branch-panel").is(':visible')) {
			$('#branch-panel').fadeOut(100, "linear");
		}

		// Close Permissions if it is visible
		if ($("#permissions-panel").is(':visible')) {
			$('#permissions-panel').fadeOut(100, "linear");
		}

		//"unselect" all node items
		$( "#node-grid>div" ).each(function() {
	    	$( this ).removeClass( "selected-card" );
	  	});

	});


	$('#permissions-tab').on('click', function (ev) {
		ev.preventDefault();

		// Close Branch if it is visible
		if ($("#branch-panel").is(':visible')) {
			$('#branch-panel').fadeOut(100, "linear");
		}

		//"unselect" all permissions items
		$( "#user-grid>div" ).each(function() {
	    	$( this ).removeClass( "selected-card" );
	  	});

	});


	$('#branches-tab').on('click', function (ev) {
		ev.preventDefault();

		// Close Branch if it is visible
		if ($("#permissions-panel").is(':visible')) {
			$('#permissions-panel').fadeOut(100, "linear");
		}

		//"unselect" all branches items
		$( "#branch-grid>div" ).each(function() {
	    	$( this ).removeClass( "selected-card" );
	  	});

	});






//	CRUD Panel
	$('#node-crud-close').on('click', function (ev) {
		ev.preventDefault();
		$('#nodeCrud').fadeOut(200, "linear");;
	});

    //D3 Radial Tree Layout

	//Define basic SVG Container variables
    var nodesize = 6;  //Default node size
        nodeMouseOver = 8;	//Mouseover Node size
        opacity = 0.5;

	var diameter = 960;

	var tree = d3.layout.tree()
	    .size([360, diameter / 2 ])
	    .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

	var diagonal = d3.svg.diagonal.radial()
	    .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

	var svg = d3.select("#graph").append("svg")
	    .attr("width", diameter)
	    .attr("height", diameter - 150)
	    .call(d3.behavior.zoom().on("zoom", redraw))
	    .append("g")
	    .attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + "), rotate(0)");


	  var nodes = tree.nodes(root),
	      links = tree.links(nodes);

	  var link = svg.selectAll(".link")
	    .data(links)
	    .enter().append("path")
	    .attr("class", "link")
	    .attr("d", diagonal);

	  var node = svg.selectAll(".node")
	    .data(nodes)
	    .enter().append("g")
	    .attr("class", "node")
	    .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })


	  node.append("circle")
	    .attr("r", nodesize)

			//add interactivity
		    .on("mouseover", function() {
              	d3.select(this)
	          	.attr("r", nodeMouseOver)
	          	.attr("class", "nodeMouseOver")
		    })

		    .on("click", function (d) {
		    	d3.select(this)

				//Get the Node Name
				var nodeName = d.entitytypeid;

				d3.select("#nodeCrud")
				.select("#nodeName")
				.text(nodeName);

				// move entire graph on click
				// var tempx = 100;
				// var tempy = 100;
				// svg.attr("transform", "translate(" + tempx + "," + tempy + "), rotate(0)");

		    	//Show the form if user clicks on a node
    			d3.select("#nodeCrud").classed("hidden", false);


    			console.log("x: " + d.x + " y: " + d.y);
				// svg.attr("transform",
	   //    			"translate(" + d.x + "," + d.y + ")"
	   //    			+ " scale(" + 1.75 + ")");


				 $("#nodeCrud").fadeIn(300, "linear");

		        // Close Permissions/Branch Library panels
		        $('#branch-panel').fadeOut(200, "linear");
		        $('#permissions-panel').fadeOut(200, "linear");



    		})


		    .on("mouseout", function(d) {
		      	d3.select(this)
		      	.attr("r", nodesize)
		      	.attr("class", "node");

		      	//Hide the form
				//d3.select("#nodeCrud").classed("hidden", true);
		    })


	  node.append("text")
	    .attr("dy", ".31em")
	    .attr("class", "node-text")
	    .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
	    .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
	    // .text(function(d) { return d.name; });

	    .text(function (d) {
        	if(d.entitytypeid.length > 13)
           		return d.entitytypeid.substring(0,13)+'...';
         	else
             	return d.entitytypeid;
        });

	d3.select("#graph").style("height", diameter - 150 + "px");


	//Zoom support: Redraw Graph on zoom
	function redraw() {

	  	//console.log("here", d3.event.translate[0], d3.event.translate[1], d3.event.scale);

	  	var xt = d3.event.translate[0] + 180;

	  	svg.attr("transform",
	      	"translate(" + xt + "," + d3.event.translate[1] + ")"
	      	+ " scale(" + d3.event.scale + ")");
	}





$(document).ready(function(){
  	$("#graph").click(function(e){

        //get cursor position, add a bit of offset
        // var x = e.pageX + 15;
        // var y = e.pageY - 5;

        //Get cursor position, add x offset
        var x = e.pageX + 15;
        var y = e.pageY;

        var xScreen = e.clientX;
        var yScreen = e.clientY;
        var windowHeight = $(window).height();
        //console.log ("xScreen = " + xScreen + ", yScreen = " + yScreen + "window" + windowHeight);


        // Offset Crud Form.
        // Magic Numbers: 	top of form should be at 130px.
        //         			Form is 600px tall; half of form is 300px;
        //
        // If current node position is less than 430 (e.g.: 130 + 300) place top of crud form at 130px
        // Else, offset crud form up 300px so that it is centered around node


        // $("#nodeCrud").fadeIn(300, "linear");

        // // Close Permissions/Branch Library panels
        // $('#branch-panel').fadeOut(200, "linear");
        // $('#permissions-panel').fadeOut(200, "linear");


  //       if ((yScreen + 300) > windowHeight) {
		//     $("#nodeCrud").offset({left:x,top:300});

		//     //scroll div to top of page
		// 	$("html, body").animate({ scrollTop: $("#nodeCrud").offset().top }, 400);
		//  //    console.log("hitting bottom");

		// } else if ((yScreen - 300) < 150) {
		//     $("#nodeCrud").offset({left:x,top:yScreen-100});
		//     $("html, body").animate({ scrollTop: $("#page-title").offset().top }, 400);
		//     // console.log("hitting top");

		// } else {
		//     $("#nodeCrud").offset({left:x,top:y-300});
		//     $("html, body").animate({ scrollTop: $("#nodeCrud").offset().top }, 400);
		// }



    })
})




    new PageView({
        viewModel: viewModel
    });
});
