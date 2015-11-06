/**
 * Draws a network graph of O*NET occupations.
 *
 * Code borrowed heavily from:
 * http://languagenetwork.cotrino.com/langnet.js
 * Many thanks to Cotrino.
 */

(function($, d3, window) {
  var w = 0, h = 0;
  var chart = "network";

  var networkChart = {
		vis : null,
		nodes : [],
		labelAnchors : [],
		labelAnchorLinks : [],
		links : [],
		force : null,
		force2 : null
  };

  var hideUnrelated = false;
  var similarityThresholdMin = 100;
  var similarityThresholdMax = 0;
  var similarityThreshold = 50;

  var min_zoom = 0.5;
  var max_zoom = 20;

  var nominal_stroke = 1;
  var max_stroke = 4.5;
  var nominal_text_size = 10;
  var max_text_size = 14;
  var nominal_base_node_size = 5;
  var max_base_node_size = 15;

  function restart() {
    if(d3.select("#graph") !== null) {
      d3.select("#graph").remove();
    }

    w = $('#graph-holder').width();
    h = $('#graph-holder').height();

    if ($('#similarity').length) {
      $('#similarity').html(Math.round(similarityThreshold) + "%");
    }

    // clear network, if available
    if (networkChart.force !== null) {
      networkChart.force.stop();
    }

    if (networkChart.force2 !== null) {
      networkChart.force2.stop();
    }

    networkChart.nodes = [];
    networkChart.labelAnchors = [];
    networkChart.labelAnchorLinks = [];
    networkChart.links = [];

    if(chart == "network") {
      drawNetwork();
    }
  }

  function drawNetwork() {
    buildNetwork();

    if ($("#hint").length) {
      $("#hint").html("Move the mouse over any occupation to show further information or click to grab the bubble around.");
    }

    networkChart.vis = d3.select("#graph-holder")
      .append("svg:svg")
      .attr("id", "graph")
      .attr("width", w)
      .attr("height", h);

    var g = networkChart.vis.append("svg:g");

    networkChart.force = d3.layout.force()
      .size([w, h])
      .nodes(networkChart.nodes)
      .links(networkChart.links)
      .gravity(0.1)
      .linkDistance(function(x) {
        return x.weight;
      })
      .charge(-30)
      .linkStrength(function(x) {
        return x.weight;
      });

    var zoom = d3.behavior.zoom()
      .scaleExtent([min_zoom, max_zoom]);

    var size = d3.scale.pow().exponent(1)
      .domain([1,100])
      .range([nominal_base_node_size, max_text_size]);

    networkChart.force.start();

    var link = g.selectAll("line.link")
    .data(networkChart.links)
    .enter()
    .append("svg:line")
    .attr("class", "link")
    .style("stroke", function(d, i) {
      return d.color; })
    .style("stroke-width", nominal_stroke);

    var node = g.selectAll("g.node")
      .data(networkChart.force.nodes())
      .enter()
      .append("svg:g")
      .attr("id", function(d, i) {
        return d.label; })
      .attr("class", "node");

    var circle = node.append("svg:circle")
      .attr("id",function(d, i) {
        return "c_" + d.label; })
      .attr("r", function(d, i) {
        return nominal_base_node_size; })
      .style("fill", function(d, i) { return d.color })
      .style("stroke", "#aaa")
      .style("stroke-width", nominal_stroke);

    var text = node.append("svg:text")
      .attr("id",function(d, i) {
        return "t_"+d.label; })
      .text(function(d, i) {
        return i % 2 == 0 ? "" : d.label; })
      .style("fill", function(d, i) {
        return "#666"; })
      .style("font-family", "Arial")
      .style("font-size", nominal_text_size + "px")
      .style("text-anchor", "middle");
    //.on("mouseover", function(d) {
    //  showInformation(d.label);
    //});

    //node.call(networkChart.force.drag);

    node.on("dblclick.zoom", function(d) {
      d3.event.stopPropagation();
      var dcx = (window.innerWidth/2-d.x*zoom.scale());
      var dcy = (window.innerHeight/2-d.y*zoom.scale());
      zoom.translate([dcx,dcy]);
       g.attr("transform", "translate("+ dcx + "," + dcy  + ")scale(" + zoom.scale() + ")");
      });

    zoom.on("zoom", function() {
      var stroke = nominal_stroke;
      if (nominal_stroke*zoom.scale()>max_stroke) {
        stroke = max_stroke/zoom.scale();
      }

      link.style("stroke-width", stroke);
      circle.style("stroke-width", stroke);

      var base_radius = nominal_base_node_size;
      if (nominal_base_node_size*zoom.scale()>max_base_node_size) {
        base_radius = max_base_node_size/zoom.scale();
      }

      circle.attr("r", function(d, i) {
        return size(d.size)*base_radius/nominal_base_node_size||base_radius;
      });

      var text_size = nominal_text_size;
      if (nominal_text_size*zoom.scale()>max_text_size) {
        text_size = max_text_size/zoom.scale();
      }
      text.style("font-size",text_size + "px");

      g.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    });

    networkChart.vis.call(zoom);

    node.on("mouseover", function(d) {
      showInformation(d.label);
    });

    var updateLink = function() {
      this.attr("x1", function(d) {
        return d.source.x;
      }).attr("y1", function(d) {
        return d.source.y;
      }).attr("x2", function(d) {
        return d.target.x;
      }).attr("y2", function(d) {
        return d.target.y;
      });

    }

    var updateNode = function() {
      this.attr("transform", function(d) {
        return "translate(" + d.x + "," + d.y + ")";
      });

    }

    networkChart.force.on("tick", function() {
      node.call(updateNode);
      link.call(updateLink);
    });

  }

  function buildNetwork() {
    var newMapping = [];
    var k = 0;
    for(var i=0; i<nodesArray.length; i++) {
      var node = nodesArray[i];
      var draw = true;
      if( hideUnrelated ) {
        if( getAmountLinks(i) == 0 ) {
          draw = false;
        }
      }
      if( draw ) {
        newMapping[i] = k;
        networkChart.nodes.push(node);
        networkChart.labelAnchors.push({ node : node });
        networkChart.labelAnchors.push({ node : node	});
        k++;
      } else {
        newMapping[i] = -1;
      }
    }

    for(var j=0; j<linksArray.length; j++) {
      var link = linksArray[j];
      var sim = link.weight;

      if (typeof('adjustSlider') === 'function') {
        adjustSlider(sim);
      }

      // just draw the links if similarity is higher than the threshold
      // or the nodes exist
      if( sim >= similarityThreshold/100.0 && newMapping[link.source] != -1 && newMapping[link.target] != -1 ) {
        var newLink = { source : newMapping[link.source], target : newMapping[link.target], weight : sim, color : '#000' };
        networkChart.links.push(newLink);
      }
    }

    // link labels to circles
    for(var i = 0; i < networkChart.nodes.length; i++) {
      networkChart.labelAnchorLinks.push({ source : i * 2, target : i * 2 + 1, weight : 1 });
    }
  }

  function showInformation(onetSocCode) {
    var url = "http://www.onetonline.org/link/summary/" + onetSocCode;
    var n = nodesHash[onetSocCode];

    if ($('#occupation_information').length) {
      $('#occupation_information').html(nodesArray[n].desc);
    }
  }

  restart();
}).call(this, jQuery, d3, window);
