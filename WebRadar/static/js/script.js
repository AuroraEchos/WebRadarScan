setInterval(function() {
    displayTime();
    displayScanRange();
    displayScanPeriod();
}, 1000);
function displayTime() {
    var date = new Date();
    var dateText = document.getElementById('currentTime');
    dateText.innerHTML =  "当前时间: " + date.toLocaleDateString() + " " + date.toLocaleTimeString();
}
function displayScanRange() {
    var ScanRange = document.getElementById('scanRange');
    ScanRange.innerHTML = "扫描半径: " + "4000" + " mm";
}
function displayScanPeriod() {
    var ScanPeriod = document.getElementById('scanPeriod');
    ScanPeriod.innerHTML = "扫描周期: " + "10" + " s";
}
function displayDistanceAndAngle(distance, angle) {
    var tableBody = document.getElementById('distanceAndAngleTableBody');
    
    if (tableBody.rows.length >= 20) {
        tableBody.deleteRow(0);
    }
    
    var newRow = tableBody.insertRow();
    var distanceCell = newRow.insertCell(0);
    var angleCell = newRow.insertCell(1);
    
    if (distance === 0 && angle === 0) {
        distanceCell.innerHTML = '<span style="color: red;">' + distance + '</span>';
        angleCell.innerHTML = '<span style="color: red;">' + angle + '</span>';
    } else {
        distanceCell.innerHTML = distance;
        angleCell.innerHTML = angle;
    }
}

const ctx = document.getElementById('lineChart').getContext('2d');
const lineChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Distance',
            data: [],
            borderColor: 'green',
            borderWidth: 1,
            fill: false
        },
        {
            label: 'Angle',
            data: [],
            borderColor: 'blue',
            borderWidth: 1,
            fill: false
        }]
    },
    
    options: {
        scales: {
            x : {
                type: 'linear',
                position: 'bottom',
                min: 0,
                max: 50,
            },
            y: {
                min: 0,
                max: 500,
            }
        }
    }
});

const scanLineCanvas = document.getElementById('scanLineCanvas');
const scanLineCtx = scanLineCanvas.getContext('2d');
const radar = document.querySelector('.radar');
const radarRect = radar.getBoundingClientRect();
const pageWidth = document.documentElement.clientWidth;
const pageHeight = document.documentElement.clientHeight;

scanLineCanvas.width = pageWidth/2 + radarRect.width/2;
scanLineCanvas.height = pageHeight/2 + radarRect.height/8;

const radarCenterX = radarRect.left + radarRect.width / 2;
const radarCenterY = radarRect.top + radarRect.height / 2;

const lineLength = 330;

function drawScanLine(angle) {
    scanLineCtx.clearRect(0, 0, scanLineCanvas.width, scanLineCanvas.height);
    const endX = radarCenterX - lineLength * Math.cos(angle * Math.PI / 180);
    const endY = radarCenterY - lineLength * Math.sin(angle * Math.PI / 180);
    
    const gradient = scanLineCtx.createLinearGradient(radarCenterX, radarCenterY, endX, endY);
    gradient.addColorStop(0, 'rgba(0, 255, 0, 1)');
    gradient.addColorStop(0.5, 'rgba(0, 255, 0, 0.5)');
    gradient.addColorStop(1, 'rgba(0, 255, 0, 0)');

    scanLineCtx.beginPath();
    scanLineCtx.moveTo(radarCenterX + 1, radarCenterY - 3);
    scanLineCtx.lineTo(endX, endY);
    scanLineCtx.strokeStyle = gradient;
    scanLineCtx.lineWidth = 3;
    scanLineCtx.stroke();
}












const targetsContainer = document.querySelector('.targets-container');
let pointsArray = [];

function displayPoints() {
    targetsContainer.innerHTML = '';

    pointsArray.forEach(point => {
        displayTarget(point.distance, point.angle);
    });
}

function displayTarget(distance, angle) {

    var radar = document.querySelector('.radar');
    var radarRect = radar.getBoundingClientRect();

    var radarCenterX = (radarRect.left + radarRect.width / 2).toFixed(1);
    var radarCenterY = (radarRect.top + radarRect.height / 2).toFixed(1);

    var radius = distance / 1000 * (radarRect.width / 2);

    var targetX = Number(radarCenterX) - Number(radius * Math.cos(angle * Math.PI / 180));
    var targetY = Number(radarCenterY) - Number(radius * Math.sin(angle * Math.PI / 180));

    var target = document.createElement('div');
    target.className = 'target';

    target.style.left = (targetX - 4) + 'px';
    target.style.top = (targetY - 5) + 'px';

    target.style.display = 'block';

    targetsContainer.appendChild(target);
}

const ws = new WebSocket("ws://localhost:8000/ws");
ws.onopen = function (event) {
    console.log("Connected to WebSocket.");
};

ws.onmessage = function (event) {
    const data = JSON.parse(event.data);
    displayDistanceAndAngle(data.distance, data.angle);

    const distance = data.distance;
    const angle = data.angle;

    /* if (distance !== 0) {

        drawScanLine(data.angle);
        if (angle > 0 && angle < 180) {
            pointsArray.push({ distance, angle });
            displayPoints();
        }
        if (angle === 0 || angle === 180) {
            pointsArray = [];
            displayPoints();
        }
    } */
    drawScanLine(angle);


    if (angle > 0 && angle < 180) {
        pointsArray.push({ distance, angle });
        if (distance !== 0) {
            displayPoints();
        }
    }
    else {
        pointsArray = [];
        console.log('清空');
        displayPoints();
    }

    const distance_forlineChart = data.distance / 2000 * 500;
    const angle_forlineChart = data.angle;

    lineChart.data.datasets[0].data.push(distance_forlineChart);
    lineChart.data.datasets[1].data.push(angle_forlineChart);
    if (lineChart.data.labels.length < 50) {
        lineChart.data.labels.push(lineChart.data.labels.length);
    } else {
        for (let i = 0; i < lineChart.data.labels.length; i++) {
            lineChart.data.labels[i] = i + 1;
        }
    }
    if (lineChart.data.datasets[0].data.length >= 50) {
        lineChart.data.datasets[0].data.shift();
        lineChart.data.datasets[1].data.shift();
    }
    lineChart.update();

};









ws.onerror = function (error) {
    console.error("WebSocket error: ", error);
};

ws.onclose = function (event) {
    if (event.wasClean) {
        console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
        console.log('[close] Connection died');
    }
};

