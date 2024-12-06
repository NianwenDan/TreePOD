// 树形决策树数据
let total_samples = 0
let g
function tree_diagram(id){
    //d3.json("../../../example/api/tree/structure.json").then(function(data) {
    url = `http://127.0.0.1:5500/api/v1/tree/structure?treeId=${id}`
    d3.json(url)
    .then(function(data) {
        total_samples = data.data.data.training_samples_reached
        labels = data.data.data.labels

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

        // 创建树形布局
        const treeLayout = d3.tree()
            .size([width, height])
            .nodeSize([150, 200])
            .separation((a, b) => a.parent === b.parent ? 1 : 1); // 设置同一父节点的子节点间隔
        treeLayout(root);

        // 创建 SVG 元素
        const svg = d3.select("#decision-tree-svg")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
        svg.append("rect")
            .attr("width", width)
            .attr("height", height)
            .attr("fill", "transparent")
            .style("pointer-events", "all")
            .on("click", function(event, d){
                d3.selectAll(".node")
                    .attr("fill", "black")
                    .style("opacity", 1);
            
                d3.selectAll(".link")
                    .attr("opacity",1)
            })

    //Tree Diagram本体
        g = svg.append("g")
            .attr("transform", "rotate(90, 200, 200) translate(100, -200)")
    //Link部分
        const link = g.selectAll(".link")
            .data(root.links())
            .enter()
            .append("g")
            .attr("class", "link")
        link.each(function(d){
            const parentValues = d.target.data.value;
            ty = d.target.x - d.source.x
            tx = d.target.y - d.source.y
            angle = Math.atan2(tx, ty)
            cosValue = Math.cos(Math.PI/2 + angle)
            sinValue = Math.sin(Math.PI/2 + angle)
            link_width = 50 * (d.target.data.samples / total_samples)

            let sumOffset = 0;
            let last = 0;
            if(angle*180/Math.PI < 90){
                cosValue = -cosValue
                sinValue = -sinValue
            }
            parentValues.forEach((v, i) => {
                sumOffset += (last + v*link_width)/2
                d3.select(this).append("line")
                    .attr("class", "link")
                    .attr("x1", d.source.y+sumOffset*sinValue)
                    .attr("y1", d.source.x+sumOffset*cosValue)
                    .attr("x2", d.target.y+sumOffset*sinValue)
                    .attr("y2", d.target.x+sumOffset*cosValue)
                    .attr("stroke", color[i])
                    .attr("stroke-width", v*link_width); // 动态宽度
                last = v*link_width
                // 生成粒子
                sample_num = Math.floor(v*1000*(d.target.data.samples / total_samples))
                for (let j = 1; j <= sample_num; j++) {
                    createParticle(d.source.y+sumOffset*sinValue, d.source.x+sumOffset*cosValue, d.target.y+sumOffset*sinValue, d.target.x+sumOffset*cosValue, color[i], d.source.depth)
                }
            });
        })
        const node = g.selectAll(".node")
            .data(root.descendants())
            .enter()
            .append("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${d.y}, ${d.x}) rotate(-90)`);

    //矩形部分
        rect_width = 100
        rect_height = 40        
        node.each(function(d){
            value = d.data.value
            let xOffset = 0;
            d.data.value.forEach((v, i) => {
                d3.select(this).append("rect")
                    .attr("x", xOffset-rect_width/2)
                    .attr("y", -50)
                    .attr("width", v*rect_width)
                    .attr("height", 20)
                    .attr("fill", color[i])
                xOffset += v*rect_width;
            });
        })
        node.append("rect")
            .attr("x", -rect_width/2)
            .attr("y", -30)
            .attr("width", rect_width)
            .attr("height", rect_height)
            .attr("fill","white")
            .attr("stroke","black")
            .attr("stroke-width",1)
        node.append("rect")
            .attr("x", -rect_width/2)
            .attr("y", -50)
            .attr("width", rect_width)
            .attr("height", 20)
            .attr("fill","transparent")
            .attr("stroke","black")
            .attr("stroke-width",1)
    // 显示节点名称
        text_y = -15
        node.append("text")
            .attr("dy", text_y)
            .attr("text-anchor", "middle")
            .text(d => d.data.name);
        node.append("text")
            .attr("dy", text_y+20)
            .attr("text-anchor", "middle")
            .text(d => {
                if(d.data.position == "right"){
                    return ">"+d.data.threshold
                }
                if(d.data.position == "left"){
                    return "<="+d.data.threshold
                }
            });
        node.each(function(d) {
            let currentNode = d3.select(this);
            d.element = this;
            currentNode.on("click", function(event, d) {
                d3.selectAll(".node")
                    .attr("fill", "black")
                highlightNodes(d);
            });
        });

    //放大缩小
        const zoom = d3.zoom()
            // .scaleExtent([0.5, 5])
            .on("zoom", (event) => {
                // console.log("zoom")
                const zoomTransform = event.transform;
                const rotateTransform = "rotate(90, 200, 200)"; // 固定旋转 90 度
                const combinedTransform = `${zoomTransform} ${rotateTransform}`;
                g.attr("transform", combinedTransform);});
        svg.call(zoom);
    
    // 图例        
        const legendGroup = svg.append("g")
            .attr("class", "legend")
            .attr("transform", "translate(200, 20)");
        const legend = legendGroup.selectAll(".legend-item")
            .data(labels)
            .enter()
            .append("g")
            .attr("class", "legend-item")
            .attr("transform", (d, i) => `translate(${i * 200}, 0)`);
        legend.append("rect")
            .attr("width", 20)
            .attr("height", 20)
            .attr("fill", (d, i) => color[i]);
        legend.append("text")
            .attr("x", 30)
            .attr("y", 15)
            .text(d => d)
            .attr("font-size", "14px")
            .attr("fill", "#000");
    // Notes        
    })
    .catch(error => {
        console.error("Error loading data:", error);
        d3.select("#decision-tree-svg")
            .append("text")
            .attr("x", 100)
            .attr("y", 100)
            .text("Failed to load tree data.");
    });
}

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
function highlightNodes(node) {

    let currentNode = node;

    // 先移除之前的高亮
    d3.selectAll(".node")
        .attr("fill", "grey")
        .style("opacity", 0.3);
    // d3.selectAll(".node rect").style("opacity", 0.3);

    d3.selectAll(".link")
        .attr("opacity",0.3)
    console.log(node)
    while (currentNode) {
        d3.select(currentNode.element)
            .attr("fill", "black")
            .style("opacity", 1);
        d3.selectAll(".link")
            .filter(function(d) {
               return (d.source === currentNode && d.target === currentNode.parent) || (d.source === currentNode.parent && d.target === currentNode);
            })
            .attr("opacity",1)
        currentNode = currentNode.parent;
    }
}
function createParticle(x1, y1, x2, y2, color, depth){
    init = Math.random()
    speed = 1 + Math.random() * 0.3
    // radius = 2 + Math.random() * 3 
    const particle = g.append("circle")
        .attr("cx", x1+ Math.random() * 20-10)
        .attr("cy", y1+ Math.random() * 20-10)
        .attr("r", 3)
        .attr("fill", color)
        .attr("stroke", "black") // 边框颜色
        .attr("stroke-width", 1); // 边框宽度
    particle.transition()
        .duration(speed*8000)
        .delay(init*20000 + depth*10000)
        .ease(d3.easeLinear)
        .attr("cx",  x2+ Math.random() * 20-10)
        .attr("cy", y2+ Math.random() * 20-10)        
        .on("end", function() {
            d3.select(this).remove();
        });
}
tree_diagram(2)