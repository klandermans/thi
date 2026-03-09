async function init() {
    try {
        const response = await fetch('data/stations.json');
        const stations = await response.json();
        const select = document.getElementById('station-select');
        
        stations.forEach(station => {
            const option = document.createElement('option');
            option.value = station.file;
            option.textContent = station.name;
            if (station.name === "Leeuwarden") option.selected = true;
            select.appendChild(option);
        });

        // Load default station
        loadStation('leeuwarden.json');
    } catch (e) {
        console.error("Error initializing stations:", e);
    }
}

async function loadStation(filename) {
    try {
        const response = await fetch(`data/${filename}`);
        const data = await response.json();
        updateUI(data);
    } catch (e) {
        console.error("Error loading station data:", e);
    }
}

function updateUI(data) {
    // Update status box
    const maxTHI = Math.max(...data.forecast.map(f => f.THI_In));
    const statusBox = document.getElementById('status-box');
    
    if (maxTHI < 68) {
        statusBox.className = 'status-box status-green';
        statusBox.textContent = 'Geen stress';
    } else if (maxTHI < 72) {
        statusBox.className = 'status-box status-orange';
        statusBox.textContent = 'Stress in aantocht';
    } else {
        statusBox.className = 'status-box status-red';
        statusBox.textContent = 'Stress!';
    }

    // Update Chart
    renderChart(data.forecast);

    // Update Table
    const tbody = document.querySelector('#forecast-table tbody');
    tbody.innerHTML = '';
    data.forecast.forEach(f => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${f.Tijd}</td>
            <td>${f.Temp_Out}</td>
            <td>${f.RH}</td>
            <td>${f.THI_Out}</td>
            <td>${f.THI_In}</td>
            <td>${f.Advies}</td>
        `;
        tbody.appendChild(tr);
    });

    // Update Buienradar
    const iframe = document.getElementById('buienradar-iframe');
    iframe.src = `https://gadgets.buienradar.nl/gadget/zoommap/?lat=${data.lat}&lng=${data.lon}&overname=2&zoom=8&naam=${data.station}&size=3&voor=0`;

    // Update Footer
    document.getElementById('last-updated').textContent = `Laatst bijgewerkt: ${data.updated_at}`;
}

function renderChart(forecast) {
    const times = forecast.map(f => f.Tijd);
    const thiIn = forecast.map(f => f.THI_In);
    const thiOut = forecast.map(f => f.THI_Out);

    const traceIn = {
        x: times,
        y: thiIn,
        name: 'THI Binnen',
        mode: 'lines+markers',
        line: { color: 'black' }
    };

    const traceOut = {
        x: times,
        y: thiOut,
        name: 'THI Buiten',
        mode: 'lines',
        line: { color: 'blue', dash: 'dash' }
    };

    const layout = {
        yaxis: { range: [30, 85], title: 'THI' },
        hovermode: 'x unified',
        legend: { orientation: 'h', y: -0.2 },
        margin: { t: 20, b: 50, l: 50, r: 20 },
        shapes: [
            { type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: 0, y1: 68, fillcolor: 'lightgreen', opacity: 0.2, line: {width: 0}, layer: 'below' },
            { type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: 68, y1: 72, fillcolor: 'yellow', opacity: 0.2, line: {width: 0}, layer: 'below' },
            { type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: 72, y1: 78, fillcolor: 'orange', opacity: 0.2, line: {width: 0}, layer: 'below' },
            { type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: 78, y1: 82, fillcolor: 'red', opacity: 0.2, line: {width: 0}, layer: 'below' },
            { type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: 82, y1: 100, fillcolor: 'darkred', opacity: 0.2, line: {width: 0}, layer: 'below' }
        ]
    };

    Plotly.newPlot('thi-chart', [traceIn, traceOut], layout, {responsive: true});
}

function showPage(pageId) {
    document.getElementById('page-home').style.display = pageId === 'home' ? 'block' : 'none';
    document.getElementById('page-register').style.display = pageId === 'register' ? 'block' : 'none';
    document.getElementById('page-about').style.display = pageId === 'about' ? 'block' : 'none';
}

function handleRegister(event) {
    event.preventDefault();
    const name = event.target.name.value;
    document.getElementById('register-msg').innerHTML = `
        <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin-top: 20px;">
            Bedankt voor je inschrijving, ${name}! Je ontvangt binnenkort een maatwerk alert.
        </div>
    `;
}

init();
