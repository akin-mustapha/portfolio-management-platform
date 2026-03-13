var dashAgGridComponentFunctions = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dashAgGridComponentFunctions.TrendSparkline = function(props) {
    var prices = props.data.price_series;
    var trend = props.data.trend;
    var color = trend === "Bullish" ? "#26a69a" : "#ef5350";

    var w = 108;
    var h = 28;
    var pad = 2;

    if (!prices || prices.length < 2) {
        return React.createElement(
            "div",
            { style: { fontSize: "11px", color: color, fontWeight: "600" } },
            trend || ""
        );
    }

    var min = Math.min.apply(null, prices);
    var max = Math.max.apply(null, prices);
    var range = max - min || 1;
    var n = prices.length;
    var xStep = (w - pad * 2) / (n - 1);
    var yScale = (h - pad * 2) / range;

    function px(i) { return pad + i * xStep; }
    function py(v) { return h - pad - (v - min) * yScale; }

    var lineParts = [];
    var areaParts = ["M", px(0), py(prices[0])];

    for (var i = 0; i < n; i++) {
        var x = px(i);
        var y = py(prices[i]);
        if (i === 0) {
            lineParts.push("M", x, y);
        } else {
            lineParts.push("L", x, y);
            areaParts.push("L", x, y);
        }
    }
    areaParts.push("L", px(n - 1), h - pad, "L", px(0), h - pad, "Z");

    var linePath = lineParts.join(" ");
    var areaPath = areaParts.join(" ");

    return React.createElement(
        "div",
        { style: { width: "100%", height: "100%", display: "flex", alignItems: "center", padding: "0 2px" } },
        React.createElement(
            "svg",
            { width: w, height: h, viewBox: "0 0 " + w + " " + h, style: { display: "block", overflow: "visible" } },
            React.createElement("path", { d: areaPath, fill: color, fillOpacity: "0.25", stroke: "none" }),
            React.createElement("path", { d: linePath, fill: "none", stroke: color, strokeWidth: "1.5", strokeLinejoin: "round", strokeLinecap: "round" })
        )
    );
};
