function slider(_min, _max)
{
    var margin = {top: 10, left: 15, right: 10, bottom: 5},
        width  = 400 - margin.left - margin.right,
        height = 30  - margin.top  - margin.bottom,

        handle,
        slider,
        value  = 0,
        // 更新handle值時要call的函數
        // 會設定value的值
        upd = function(d){value = d;},
        // 單純是函式指標的的callback
        cback = function(d){};

    var x = d3.scaleLinear()
        .domain([_min, _max])
        .range([0, width-80])
        .clamp(true);

    // el就是從外面傳進來的svg
    function chart(el){
        svg = el;

        // 新增圖層
        slider = el.attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        slider.append("line")
            .attr("class", "track")
            .attr("x1", x.range()[0])
            .attr("x2", x.range()[1])
            .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
            .attr("class", "track-inset")
            .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
            .attr("class", "track-overlay")
            .call(d3.drag()
                .on("start.interrupt", function() { slider.interrupt(); })
                .on("start drag", function() { setHandle(x.invert(d3.event.x)); })
                .on('end', function() { ended(); })
            );

        slider.insert("g", ".track-overlay")
            .attr("class", "ticks")
            .attr("transform", "translate(0," + 18 + ")")
            .selectAll("text")
            .data(x.ticks(10))
            .enter().append("text")
            .attr("x", x)
            .attr("text-anchor", "middle")
            .text(function(d) { return d; });

        handle = slider.insert("circle", ".track-overlay")
            .attr("class", "handle")
            .attr("r", 8)
            .attr('style', "stroke: #099; stroke-width: 2");

        function setHandle(h) {
            // 如果發生了事件，就把滑鼠的x座標資料轉換為value
            if (d3.event.sourceEvent) value = h;
            // 更新value
            upd(value);
            // 沒有做啥事的callback
            cback();
        }

        // 得到value值以後更新handle的位置
        upd = function (v) {
            // console.log("handle cx: ",x(v),", round value:",x(Math.round(v)));
            value = v;
            // 設定handle的cx值，也就是實際座標值
            handle.attr("cx", x(v));
        }


    }

    chart.margin = function (_) {
        // return margin;
        if (!arguments.length) return margin;
        margin = _;
        return chart;
    };
    chart.callback = function (_) {
        if (!arguments.length) return cback;
        cback = _;
        return chart;
    };
    chart.value = function (_) {
        if (!arguments.length) return value;
        upd(_);
        return chart;
    };

    return chart;
}