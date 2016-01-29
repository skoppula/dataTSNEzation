// Rounds a value to [decimals] places
function round(value, decimals) {
  return Number(Math.round(value+'e'+decimals)+'e-'+decimals);
}

// Add d3 TIP object to DOM
function runD3(data_from_server) {
    // Clear any previous graphs created
    console.log('before emptying graph');
    $('#graph').empty();
    console.log('AFTER emptying graph');

    // Setup canvas margins
    var margin = {
            top: 20,
            right: 20,
            bottom: 30,
            left: 40
        },
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var comparison_variable_values = d3.keys(data_from_server[0]).filter(function(key) {
        return key != "category" && key != "series"
    });

    // Setup the axis scales (intervals for X-axis, continuous linear range for y)
    var x0_scale = d3.scale.ordinal() //For the group of rectangles in a category
        .rangeRoundBands([0, width], .1)
        .domain(data_from_server.map(function(d) {
            return d.category;
        }));
    var x1_scale = d3.scale.ordinal() // For individual rectangles
        .domain(comparison_variable_values).rangeRoundBands([0, x0_scale.rangeBand()]);
    var y_scale = d3.scale.linear()
        .range([height, 0]);
    var category_colors = d3.scale.ordinal()
        .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"])
        .domain([0, d3.max(data_from_server, function(d) {
            return d3.max(d.series, function(d) {
                return d.value;
            });
        })]);

    // Sets up the axis: sets orientation and scale of the axis on the canvas
    var xAxis = d3.svg.axis()
        .scale(x0_scale)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y_scale)
        .orient("left")
        .ticks(10, "%");

    // Create a 'tip' canvas on which we put a d3 SVG object on
    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function(d) {
            var val = round((d.value * 100.0), 2);
            return "<div style=\"text-align: center; font-size: 1.25em !important; color: white; background-color: black; opacity: 0.7\"><strong>" + d.name + "</strong><br><strong></strong><span style='color:orange'> " + val + "%</span></div>";
        })


    // Create our graph!
    var svg = d3.select("#graph").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Center graph on canvas
    d3.select("#graph").attr("align", "center");

    svg.call(tip);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)

    // Translate each bar group further and further right (partial black magic)
    var group = svg.selectAll(".group")
        .data(data_from_server)
        .enter().append("g")
        .attr("class", "group")
        .attr("transform", function(d) {
            return "translate(" + x0_scale(d.category) + ",0)";
        });

    // Set properties for each rectangle in a group
    group.selectAll("rect")
        .data(function(d) {
            return d.series;
        })
        .enter().append("rect")
        .attr("class", "rectangle")
        .attr("width", x1_scale.rangeBand())
        .attr("x", function(d) {
            return x1_scale(d.name);
        })
        .attr("y", function(d) {
            return y_scale(d.value);
        })
        .attr("height", function(d) {
            return height - y_scale(d.value);
        })
        .style("fill", function(d) {
            return category_colors(d.name);
        })
        .on("mouseover", tip.show)
        .on("mouseout", tip.hide);

    // Render the legend
    var legend = svg.selectAll(".legend")
        .data(comparison_variable_values.slice().reverse())
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function(d, i) {
            return "translate(0," + i * 20 + ")";
        });

    legend.append("rect")
        .attr("x", width - 18)
        .attr("width", 18)
        .attr("height", 18)
        .style("fill", category_colors);
    legend.append("text")
        .attr("x", width - 24)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function(d) {
            return d;
        });
}
