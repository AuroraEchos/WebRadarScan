const socket = io();

// 折线图
const ctx = document.getElementById('lineChart').getContext('2d');
const lineChart = new Chart(ctx, {
    type: 'line',
    data: {
        datasets: [{
            label: 'Distance',
            data: [],
            borderColor: 'green',
            fill: false
        },
        {
            label: 'Angle', // 第二个数据集的标签
            data: [],
            borderColor: 'blue', // 第二个数据集的颜色
            fill: false
            }
        ]
    },
    options: {
        scales: {
            x: {
                type: 'linear',
                position: 'bottom',
            },
            y: {
                min: 0,
                max: 500
            }
        }
    }
});


socket.on('update_data', function (data) {
    const distance = data.distance;
    const angle = data.angle;

    document.getElementById('targetDistance').innerText = 'Target Distance: ' + distance;
    document.getElementById('targetAngle').innerText = 'Target Angle: ' + angle;

    lineChart.data.labels.push(lineChart.data.labels.length);
    lineChart.data.datasets[0].data.push(distance);
    lineChart.data.datasets[1].data.push(angle);

    lineChart.update();
});


setInterval(function() {
    updateDataDisplay();
}, 1000);

function updateDataDisplay() {
    // 显示当前日期时间
    var now = getCurrentTime()
    var dynamicText = document.getElementById("currentTime");
    dynamicText.innerText = "Date & Time: " + now.toLocaleDateString() + " " + now.toLocaleTimeString();
    
    // 显示模拟雷达范围
    var radarDimensions = getRadarDimensions();
    var radarDimensionsElement = document.getElementById('radarDimensions');
    radarDimensionsElement.innerText = 'Radar Size: ' + radarDimensions.width + ' x ' + radarDimensions.height;

    // 显示雷达相对坐标点
    var radarCenter = getRadarCenter();
    var radarRelativeCoordinates = document.getElementById('radarCenter');
    radarRelativeCoordinates.innerText = 'Radar Coordinates: ' + '[' + radarCenter.x + ' , ' + radarCenter.y + ']';
};

function getCurrentTime() {
    var now = new Date();
    return now;
}

function getRadarDimensions() {
    var radar = document.querySelector('.radar');
    var radarWidth = radar.offsetWidth;
    var radarHeight = radar.offsetHeight;
    return { width: radarWidth, height: radarHeight };
}

function getRadarCenter() {
    var radar = document.querySelector('.radar');
    var radarRect = radar.getBoundingClientRect();
    var radarCenterX = (radarRect.left + radarRect.width / 2).toFixed(1);
    var radarCenterY = (radarRect.top + radarRect.height / 2).toFixed(1);
    return { x: radarCenterX, y: radarCenterY };
}