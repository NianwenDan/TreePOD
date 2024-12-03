// 树形决策树数据
let total_samples = 0
//d3.json("../../../example/api/tree/structure.json").then(function(data) {
d3.json("http://127.0.0.1:5500/api/v1/tree/structure?treeId=2")
    .then(function(data) {
        total_samples = data.data.data.training_samples_reached
        console.log(data.data.data.training_samples_reached)
        const treeData  = process_treeData(data.data, "All sample", 1, 1)
        console.log(treeData)
        // SVG 尺寸设置
        const width = 2000;
        const height = 800;

        // 创建层次结构数据
        const root = d3.hierarchy(treeData);

        // color = d3.scaleOrdinal(d3.schemeSet3)
        color = ["#002F6C", "#EBBE4D", "#CD1C18", "#00965F"]
        // console.log(treeData)
        // console.log(treeData.data)
        // console.log(treeData.data.left)
        // 创建树形布局
        const treeLayout = d3.tree()
            .size([width - 200, height - 100])
            .nodeSize([150, 200])
            .separation((a, b) => a.parent === b.parent ? 1 : 1); // 设置同一父节点的子节点间隔
        treeLayout(root);

        // 创建 SVG 元素
        const svg = d3.select("#decision-tree-svg")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            // .style("pointer-events", "all");
            // .attr("transform", "rotate(90, 200, 200)")
        svg.append("rect")
            .attr("width", width)
            .attr("height", height)
            .attr("fill", "transparent")
            .style("pointer-events", "all");

        const g = svg.append("g")
            .attr("transform", "rotate(90, 200, 200) translate(100, -200)")

        // 添加连线并根据 proportion 调整宽度
        root.links().forEach(link => {
            const parentValues = link.source.data.value;
            link_width = 50 * (link.target.data.samples / total_samples)

            // let xOffset = 0;
    
            parentValues.forEach((v, i) => {
                g.append("line")
                    .attr("class", "link")
                    .attr("x1", link.source.y) // 起点 x 坐标
                    .attr("y1", link.source.x + v*link_width) // 起点 y 坐标，偏移用于分段
                    .attr("x2", link.target.y) // 终点 x 坐标
                    .attr("y2", link.target.x + v*link_width) // 终点 y 坐标
                    .attr("stroke", color[i]) // 动态颜色
                    .attr("stroke-width", v*link_width); // 动态宽度
                // xOffset += v*link_width
                });
        });
        
        // svg.selectAll(".link")
        // .data(root.links())
        // .enter()
        // .append("line")
        // .attr("class", "link")
        // .attr("x1", d => d.source.y)
        // .attr("y1", d => d.source.x)
        // .attr("x2", d => d.target.y)
        // .attr("y2", d => d.target.x)
        // .attr("stroke-width", d => d.target.data.proportion * 50)
        // .attr("stroke", "#ccc");

        // 添加节点
        const node = g.selectAll(".node")
            .data(root.descendants())
            .enter()
            .append("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${d.y}, ${d.x}) rotate(-90)`);

        // 在每个节点上显示矩形
        node.each(function(d){
            value = d.data.value
            rect_width = 100
            rect_height = 40
            let xOffset = 0;
            d.data.value.forEach((v, i) => {
                d3.select(this).append("rect")
                    .attr("x", xOffset-50)
                    .attr("y", -10)
                    .attr("width", v*rect_width)
                    .attr("height", rect_height)
                    .attr("fill", color[i])
                xOffset += v*rect_width;
            });
        })
        node.append("rect")
            .attr("x", -50)
            .attr("y", 5)
            .attr("width", 100)
            .attr("height", 40)
            .attr("fill","white")
            .attr("stroke","black")
            .attr("stroke-width",2)
        node.append("rect")
            .attr("x", -50)
            .attr("y", -10)
            .attr("width", 100)
            .attr("height", 15)
            .attr("fill","transparent")
            .attr("stroke","black")
            .attr("stroke-width",2)
        // 显示节点名称
        node.append("text")
        .attr("dy", 20)
        .attr("text-anchor", "middle")
        .text(d => d.data.name);

        node.append("text")
        .attr("dy", 40)
        .attr("text-anchor", "middle")
        .text(d => {
            if(d.data.position == "right"){
                return ">"+d.data.threshold
            }
            if(d.data.position == "left"){
                return "<="+d.data.threshold
            }
        });

        const zoom = d3.zoom()
            // .scaleExtent([0.5, 5])
            .on("zoom", (event) => {
                // console.log("zoom")
                const zoomTransform = event.transform;
                const rotateTransform = "rotate(90, 200, 200)"; // 固定旋转 90 度
                const combinedTransform = `${zoomTransform} ${rotateTransform}`;
            
                // 应用组合变换
                g.attr("transform", combinedTransform);        });

        // 绑定缩放行为到 svg
        svg.call(zoom);
    })
    .catch(error => {
        console.error("Error loading data:", error);
        d3.select("#decision-tree-svg")
            .append("text")
            .attr("x", 100)
            .attr("y", 100)
            .text("Failed to load tree data.");
    });

function process_treeData(input, nodename, nodethreshold, nodeproportion, nodeposition){
    const original = input
    // const original = input.data.data.feature
    const feature = original.data.feature
    const threshold = original.data.threshold
    // New
    const value = original.data.value[0]
    const labels = original.data.labels

    const training = original.data.training_samples_reached
    const testing = original.data.testing_samples_reached

    // const proportion_right = original.data.value[0][0]
    // const proportion_left = original.data.value[0][1]

    const leftNode = original.left
    const rightNode = original.right
    if(leftNode == null || rightNode == null){
        const transformedData = {
            name: nodename,
            proportion: nodeproportion,
            position: nodeposition,
            threshold: nodethreshold,
            value: value,
            samples: training         
        }
        return transformedData
    }
    else{
        const proportion_right = rightNode.data.training_samples_reached / total_samples
        const proportion_left = leftNode.data.training_samples_reached / total_samples
        const transformedData = {
            name:nodename,
            proportion: nodeproportion,
            threshold: nodethreshold,
            position: nodeposition,
            value: value,
            samples: training,         
            children: [
                process_treeData(rightNode, feature, threshold, proportion_right, "right"),
                process_treeData(leftNode, feature, threshold, proportion_left, "left")
            ]
        }
        return transformedData
    }
    // console.log(rightNode)
}
// d3.json("example.json").then(function(treeData) {
//     data = process_treeData(treeData.data, "All sample", 1, 1)
//     console.log(data)
// })
