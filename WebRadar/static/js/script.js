
setInterval(function() {
    updateDataDisplay();
}, 1000);

function updateDataDisplay() {
    // 显示当前日期
    var dynamicText = document.getElementById("Time");
    var now = new Date();
    var dateTimeString = now.toLocaleDateString() + " " + now.toLocaleTimeString();
    dynamicText.innerText = "Date & Time: " + dateTimeString;
    
    // 显示模拟雷达范围
    var radarDimensions = getRadarDimensions();
    var radarDimensionsElement = document.getElementById('radarDimensions');
    radarDimensionsElement.innerText = 'Radar Size: ' + radarDimensions.width + ' x ' + radarDimensions.height;

    // 显示雷达相对坐标点
    var radarCenter = getRadarCenter();
    var radarRelativeCoordinates = document.getElementById('radarCenter');
    radarRelativeCoordinates.innerText = 'Radar Coordinates: ' + '[' + radarCenter.x + ' , ' + radarCenter.y + ']';
};

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

