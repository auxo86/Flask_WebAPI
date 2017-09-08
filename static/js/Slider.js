function slider()
{
    var margin = {top: 5, left: 15, right: 10, bottom: 5},
        width  = 300 - margin.left - margin.right,
        height = 40  - margin.top  - margin.bottom,
        brush  = d3.brush(),
        handle, slider,
        value  = 0,
        upd    = function(d){value = d;},
        cback  = function(d){};

    var x = d3.scaleLinear()
        .domain([-1,1])
        .range ([0,width])
        .clamp(true);

    function chart(el)
    {

        d3.brushX(x).extent([0,0])
             .on("brush", brushed);

        var svg = el.attr("width",  width  + margin.left + margin.right)
            .attr("height", height + margin.top  + margin.bottom)
            .append("g").attr("transform","translate(" + margin.left + "," + margin.top + ")");

        svg.append("g")
           .attr("class","x axis")
           //.attr("transform", "translate(0,"+height/2+")")
           .attr("transform", d3.event.transform)
           .call(d3.svg.axis().scale(x).orient("bottom").tickSize(0).tickPadding(12));

        slider = svg.append("g")
            .attr("class","slider")
            .call(brush);

        slider.selectAll(".extent,.resize").remove();
        slider.select(".background").attr("height",height)

        handle = slider.append("circle")
            .attr("class","handle")
            .attr("transform", "translate(0,"+height/2+")")
            .attr("cx",x(value))
            .attr("r",9);

        function brushed()
        {
            if (d3.event.sourceEvent) value = x.invert(d3.mouse(this)[0]);
            upd(value);
            cback();
        }
        upd = function(v)
        {
            brush.extent([v,v]);
            value = brush.extent()[0];
            handle.attr("cx",x(value));
        }
    }

    chart.margin   = function(_) { if (!arguments.length) return margin;  margin = _; return chart; };
    chart.callback = function(_) { if (!arguments.length) return cback;    cback = _; return chart; };
    chart.value    = function(_) { if (!arguments.length) return value;       upd(_); return chart; };

    return chart;
}