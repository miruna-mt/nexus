console.log('Script cargado');

const instancesConfig = {
    'logistics_delivery': {
        name: 'Logistics - Agri-food Delivery',
        problem_type: 'routing',
        description: 'Delivery of agricultural products to platforms and markets.',
        parametric: {
            parameters: [
                { name: 'num_vehiculos', label: 'Number of vehicles', type: 'slider', min: 1, max: 4, default: 4, unit: '' },
                { name: 'num_clientes', label: 'Number of customers to visit', type: 'slider', min: 5, max: 14, default: 14, unit: '' }
            ]
        },
        expert: {
            expectedSchema: ['vehiculos', 'clientes', 'deposito'],
            example: 'routing_madrid.json'
        }
    },
    'proyectos_equipos': {
        name: 'Assignment - Projects to Teams',
        problem_type: 'assignment',
        description: 'Assign projects to specialized teams maximizing total value.',
        parametric: {
            parameters: [
                { name: 'capacidad_equipos', label: 'Team capacity (%)', type: 'slider', min: 50, max: 200, default: 100, unit: '%' },
                { name: 'bonus_gran_empresa', label: 'Large company bonus (EUR)', type: 'slider', min: 0, max: 20000, default: 0, unit: 'EUR', step: 1000 }
            ]
        },
        expert: {
            expectedSchema: ['proyectos', 'equipos'],
            example: 'assignment_consultora.json'
        }
    },
    'supermercado': {
        name: 'Inventory - Supermarket',
        problem_type: 'inventory',
        description: 'Optimize orders and stock of perishable products.',
        parametric: {
            parameters: [
                { name: 'coste_pedido', label: 'Order cost (EUR)', type: 'slider', min: 10, max: 200, default: 50, unit: 'EUR', step: 5 },
                { name: 'coste_almacenaje', label: 'Storage cost (EUR/unit/week)', type: 'slider', min: 0.01, max: 0.20, default: 0.05, unit: 'EUR', step: 0.01 },
                { name: 'coste_rotura', label: 'Out-of-stock cost (EUR/unit)', type: 'slider', min: 0.5, max: 5.0, default: 2.0, unit: 'EUR', step: 0.1 }
            ]
        },
        expert: {
            expectedSchema: ['horizonte_semanas', 'capacidad_almacen', 'productos'],
            example: 'inventory_supermercado.json'
        }
    },
    'cartera_markowitz': {
        name: 'Portfolio - Markowitz Portfolio',
        problem_type: 'portfolio',
        description: 'Optimize an investment portfolio maximizing risk-adjusted return.',
        parametric: {
            parameters: [
                { name: 'aversion_riesgo', label: 'Risk aversion', type: 'slider', min: 0, max: 10, default: 2, unit: '' },
                { name: 'rentabilidad_tech', label: 'Tech return (%)', type: 'slider', min: 5, max: 25, default: 12, unit: '%' }
            ]
        },
        expert: {
            expectedSchema: ['capital_total', 'aversion_riesgo', 'activos', 'covarianzas'],
            example: 'portfolio_inversor.json'
        }
    }
};

let currentLevel = 'demo';
let map = null;
window.userData = null;

document.addEventListener('DOMContentLoaded', () => {
    setupProblemSelector();
    setupLevelButtons();
    setupInstanceSelector();
    updateLevelContent('demo');
    updateDescription();
});

function setupProblemSelector() {
    const problemSelect = document.getElementById('problemType');
    if (!problemSelect) return;
    problemSelect.addEventListener('change', () => {
        window.userData = null;
        populateInstanceSelect(problemSelect.value);
    });
}

function populateInstanceSelect(problemType) {
    const instanceSelect = document.getElementById('instance');
    const counter = document.getElementById('instance-counter');
    if (!instanceSelect) return;

    while (instanceSelect.options.length > 0) {
        instanceSelect.remove(0);
    }

    const matching = Object.entries(instancesConfig)
        .filter(([key, config]) => config.problem_type === problemType);

    if (matching.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.disabled = true;
        opt.selected = true;
        opt.textContent = 'No scenarios available';
        instanceSelect.appendChild(opt);
        instanceSelect.disabled = true;
        if (counter) counter.textContent = '';
        return;
    }

    matching.forEach(([key, config]) => {
        const opt = document.createElement('option');
        opt.value = key;
        opt.textContent = config.name;
        instanceSelect.appendChild(opt);
    });

    instanceSelect.disabled = false;
    instanceSelect.selectedIndex = 0;

    updateInstanceCounter();
    window.userData = null;
    updateDescription();
    updateLevelContent(currentLevel);
}

function updateInstanceCounter() {
    const instanceSelect = document.getElementById('instance');
    const counter = document.getElementById('instance-counter');
    if (!instanceSelect || !counter) return;
    const total = instanceSelect.options.length;
    const current = instanceSelect.selectedIndex + 1;
    if (total > 0 && instanceSelect.value) {
        counter.textContent = 'Scenario ' + current + ' of ' + total;
    } else {
        counter.textContent = '';
    }
}

function setupLevelButtons() {
    document.querySelectorAll('.level-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.level-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentLevel = btn.dataset.level;
            window.userData = null;
            updateLevelContent(currentLevel);
            updateDescription();
        });
    });
}

function setupInstanceSelector() {
    const instanceSelect = document.getElementById('instance');
    if (instanceSelect) {
        instanceSelect.addEventListener('change', () => {
            window.userData = null;
            updateInstanceCounter();
            updateDescription();
            updateLevelContent(currentLevel);
        });
    }
}

function updateLevelContent(level) {
    const instance = document.getElementById('instance').value;
    const container = document.getElementById('level-content');
    if (!instance) {
        container.innerHTML = '<p style="color: #64748b; text-align: center;">Select a scenario first</p>';
        return;
    }
    const config = instancesConfig[instance];
    if (!config) {
        container.innerHTML = '<p style="color: #dc2626; text-align: center;">Configuration not found</p>';
        return;
    }
    if (level === 'demo') {
        container.innerHTML = generateDemoHTML(config);
        attachOptimizeEvent(false, false);
    } else if (level === 'parametric') {
        container.innerHTML = generateParametricHTML(config);
        attachParametricEvents();
    } else if (level === 'expert') {
        container.innerHTML = generateExpertHTML(config);
        attachExpertEvents();
    }
}

function generateDemoHTML(config) {
    return '<div class="demo-container"><p style="color: #475569; margin-bottom: 15px;">Predefined scenario with sample data.</p><button id="optimizeBtn" class="optimize-btn">Optimize with demo data</button></div>';
}

function generateParametricHTML(config) {
    let html = '<div class="parametric-container"><h4 style="margin-bottom: 20px;">Adjust parameters:</h4>';
    if (config.parametric && config.parametric.parameters && config.parametric.parameters.length > 0) {
        config.parametric.parameters.forEach(param => {
            const step = param.step || 1;
            html += '<div class="parameter-item"><div class="parameter-label"><span>' + param.label + '</span><span class="parameter-value" data-param="' + param.name + '">' + param.default + ' ' + (param.unit || '') + '</span></div><input type="range" class="parameter-slider" data-param="' + param.name + '" min="' + param.min + '" max="' + param.max + '" value="' + param.default + '" step="' + step + '"></div>';
        });
    } else {
        html += '<p>No adjustable parameters</p>';
    }
    html += '<button id="optimizeBtn" class="optimize-btn" style="margin-top: 20px;">Optimize with these values</button></div>';
    return html;
}

function generateExpertHTML(config) {
    const exampleFile = config.expert && config.expert.example ? config.expert.example : null;
    let exampleLink = '';
    if (exampleFile) {
        exampleLink = '<div style="margin-top: 15px; text-align: center;"><a href="/examples/' + exampleFile + '" download style="color: #667eea; text-decoration: none; font-size: 0.9rem;">Download example file</a></div>';
    }
    return '<div class="expert-container"><h4 style="margin-bottom: 15px;">Upload your own JSON file</h4><div class="file-upload-area" id="fileUploadArea"><div class="upload-icon">Folder</div><div class="upload-text">Drag your JSON file or click to select</div><div class="upload-hint">Expected fields: ' + (config.expert && config.expert.expectedSchema ? config.expert.expectedSchema.join(', ') : 'definir') + '</div><input type="file" id="fileInput" accept=".json" style="display: none;"></div>' + exampleLink + '<div id="validationResult" style="margin-top: 15px;"></div><button id="optimizeBtn" class="optimize-btn" style="margin-top: 20px; display: none;">Optimize with my data</button></div>';
}

function attachOptimizeEvent(isParametric, isExpert) {
    const btn = document.getElementById('optimizeBtn');
    if (!btn) return;
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);

    newBtn.addEventListener('click', async () => {
        const instance = document.getElementById('instance').value;
        const config = instancesConfig[instance];
        const output = document.getElementById('output');
        if (!config) return;

        output.innerHTML = '<div style="text-align: center; color: #667eea;">Optimizing...</div>';

        const payload = { problem_type: config.problem_type, instance: instance };

        if (isParametric) {
            const params = {};
            document.querySelectorAll('.parameter-slider').forEach(slider => {
                params[slider.dataset.param] = slider.value;
            });
            payload.params = params;
        }

        if (isExpert && window.userData) {
            payload.user_data = window.userData;
        }

        try {
            const response = await fetch('/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error('Error HTTP: ' + response.status);
            const data = await response.json();

            if (data.status === 'optimal') {
                let html = '';

                if (data.narrative) {
                    html += '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 16px; margin-bottom: 25px;">';
                    html += '<div style="font-size: 1.3rem; font-weight: 700; margin-bottom: 12px; line-height: 1.4;">' + data.narrative.titular + '</div>';
                    html += '<div style="font-size: 0.95rem; margin-bottom: 10px; opacity: 0.95; line-height: 1.5;"><strong>Comparison:</strong> ' + data.narrative.comparacion + '</div>';
                    html += '<div style="font-size: 0.95rem; opacity: 0.95; line-height: 1.5;"><strong>Insight:</strong> ' + data.narrative.insight + '</div>';
                    html += '</div>';
                }

                if (config.problem_type === 'routing') {
                    html += '<div style="background: #f0f9ff; padding: 20px; border-radius: 12px; margin-bottom: 20px;"><div style="font-size: 1.2rem; color: #1e293b;">Total distance traveled</div><div style="font-size: 2.5rem; font-weight: 700; color: #059669; margin: 10px 0;">' + data.objective_value + ' km</div></div>';
                    html += '<h4 style="color: #1e293b; margin-bottom: 15px;">Assigned routes</h4><div style="display: flex; flex-direction: column; gap: 15px;">';
                    if (data.rutas && data.rutas.length > 0) {
                        data.rutas.forEach(ruta => {
                            html += '<div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px;"><div style="font-weight: 700; color: #1e293b; margin-bottom: 8px;">' + ruta.vehiculo + '</div><div style="color: #475569; margin-bottom: 8px;">Stops: ' + ruta.paradas.join(' -> ') + '</div><div style="color: #059669; font-weight: 600;">Distance: ' + ruta.distancia + ' km</div></div>';
                        });
                    }
                    html += '</div>';
                    html += '<div id="map" style="height: 450px; margin-top: 20px; border-radius: 12px; background: #e2e8f0;"></div>';
                } else if (config.problem_type === 'assignment') {
                    html += '<div style="background: #f0f9ff; padding: 20px; border-radius: 12px; margin-bottom: 20px;"><div style="font-size: 1.2rem; color: #1e293b;">Total assigned value</div><div style="font-size: 2.5rem; font-weight: 700; color: #059669; margin: 10px 0;">' + data.objective_value.toLocaleString('en-US') + ' EUR</div></div>';
                    html += '<h4 style="color: #1e293b; margin-bottom: 15px;">Assignments</h4><table style="width: 100%; border-collapse: collapse;"><tr style="background: #e2e8f0; font-weight: 600;"><th style="padding: 10px; text-align: left;">Project</th><th style="padding: 10px; text-align: left;">Team</th><th style="padding: 10px; text-align: right;">Hours</th><th style="padding: 10px; text-align: right;">Value</th></tr>';
                    data.asignaciones.forEach(a => {
                        html += '<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px;">' + a.proyecto + '</td><td style="padding: 10px;">' + a.equipo + '</td><td style="padding: 10px; text-align: right;">' + a.horas + '</td><td style="padding: 10px; text-align: right; color: #059669; font-weight: 600;">' + a.valor.toLocaleString('en-US') + ' EUR</td></tr>';
                    });
                    html += '</table>';
                } else if (config.problem_type === 'inventory') {
                    html += '<div style="background: #fef3c7; padding: 20px; border-radius: 12px; margin-bottom: 20px;"><div style="font-size: 1.2rem; color: #1e293b;">Total inventory cost</div><div style="font-size: 2.5rem; font-weight: 700; color: #d97706; margin: 10px 0;">' + data.objective_value.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' EUR</div></div>';
                    html += '<h4 style="color: #1e293b; margin-bottom: 15px;">Product summary</h4><table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;"><tr style="background: #e2e8f0; font-weight: 600;"><th style="padding: 10px; text-align: left;">Product</th><th style="padding: 10px; text-align: right;">Total ordered</th><th style="padding: 10px; text-align: right;">Out-of-stock</th><th style="padding: 10px; text-align: right;">Final stock</th></tr>';
                    data.resumen.forEach(r => {
                        const color = r.total_rotura > 0 ? '#dc2626' : '#059669';
                        html += '<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px;">' + r.producto + '</td><td style="padding: 10px; text-align: right;">' + r.total_pedido + ' units</td><td style="padding: 10px; text-align: right; color: ' + color + ';">' + r.total_rotura + ' units</td><td style="padding: 10px; text-align: right;">' + r.stock_final + ' units</td></tr>';
                    });
                    html += '</table>';
                } else if (config.problem_type === 'portfolio') {
                    html += '<div style="background: #ecfdf5; padding: 20px; border-radius: 12px; margin-bottom: 20px;"><div style="font-size: 1.2rem; color: #1e293b;">Expected portfolio return</div><div style="font-size: 2.5rem; font-weight: 700; color: #059669; margin: 10px 0;">' + data.rentabilidad_esperada_pct + ' %</div><div style="font-size: 0.9rem; color: #64748b;">with an estimated risk of ' + data.riesgo_estimado_pct + '%</div></div>';
                    html += '<h4 style="color: #1e293b; margin-bottom: 15px;">Portfolio composition</h4><table style="width: 100%; border-collapse: collapse;"><tr style="background: #e2e8f0; font-weight: 600;"><th style="padding: 10px; text-align: left;">Asset</th><th style="padding: 10px; text-align: right;">Weight</th><th style="padding: 10px; text-align: right;">Investment</th><th style="padding: 10px; text-align: right;">Return</th><th style="padding: 10px; text-align: right;">Risk</th></tr>';
                    data.cartera.forEach(c => {
                        html += '<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px;">' + c.activo + '</td><td style="padding: 10px; text-align: right; font-weight: 600;">' + c.peso_pct + ' %</td><td style="padding: 10px; text-align: right;">' + c.inversion.toLocaleString('en-US') + ' EUR</td><td style="padding: 10px; text-align: right; color: #059669;">' + c.rentabilidad_pct + ' %</td><td style="padding: 10px; text-align: right; color: #dc2626;">' + c.riesgo_pct + ' %</td></tr>';
                    });
                    html += '</table>';
                }

                output.innerHTML = html;

                if (config.problem_type === 'routing' && data.rutas && data.rutas.length > 0) {
                    setTimeout(() => dibujarMapa(data.rutas), 100);
                }
            } else {
                output.innerHTML = '<div style="color: #dc2626;">Error: ' + (data.error || 'Optimization failed') + '</div>';
            }
        } catch (error) {
            console.error('Error:', error);
            output.innerHTML = '<div style="color: #dc2626;">Connection error: ' + error.message + '</div>';
        }
    });
}

function dibujarMapa(rutas) {
    const mapDiv = document.getElementById('map');
    if (!mapDiv) return;
    if (map) {
        map.remove();
        map = null;
    }
    map = L.map('map').setView([38.5, -1.5], 7);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const colores = ['#dc2626', '#059669', '#2563eb', '#d97706', '#7c3aed', '#db2777'];
    const bounds = [];

    rutas.forEach((ruta, idx) => {
        if (ruta.coordenadas && ruta.coordenadas.length > 0) {
            const coords = ruta.coordenadas.map(c => [c.lat, c.lon]);
            const color = colores[idx % colores.length];
            L.polyline(coords, { color: color, weight: 4, opacity: 0.8 }).addTo(map);
            coords.forEach((coord, i) => {
                const marker = L.circleMarker(coord, {
                    radius: 7, fillColor: color, color: '#fff', weight: 2, fillOpacity: 0.9
                }).addTo(map);
                const punto = ruta.paradas && ruta.paradas[i] ? ruta.paradas[i] : (i === 0 ? 'Depot' : 'Point');
                marker.bindPopup('<b>' + ruta.vehiculo + '</b><br>' + punto);
                bounds.push(coord);
            });
        }
    });
    if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [30, 30] });
    }
    setTimeout(() => map.invalidateSize(), 200);
}

function attachParametricEvents() {
    document.querySelectorAll('.parameter-slider').forEach(slider => {
        slider.addEventListener('input', (e) => {
            const param = e.target.dataset.param;
            const value = e.target.value;
            const paramConfig = instancesConfig[document.getElementById('instance').value].parametric.parameters.find(p => p.name === param);
            const unit = paramConfig && paramConfig.unit ? ' ' + paramConfig.unit : '';
            document.querySelector('.parameter-value[data-param="' + param + '"]').textContent = value + unit;
        });
    });
    attachOptimizeEvent(true, false);
}

function attachExpertEvents() {
    const uploadArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('fileInput');
    if (uploadArea) {
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
        uploadArea.addEventListener('dragleave', () => { uploadArea.classList.remove('dragover'); });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            handleFileUpload(e.dataTransfer.files[0]);
        });
    }
    if (fileInput) {
        fileInput.addEventListener('change', (e) => handleFileUpload(e.target.files[0]));
    }
    attachOptimizeEvent(false, true);
}

function handleFileUpload(file) {
    const validationDiv = document.getElementById('validationResult');
    const optimizeBtn = document.getElementById('optimizeBtn');
    if (!file || file.type !== 'application/json') {
        validationDiv.innerHTML = '<div class="format-error">The file must be JSON</div>';
        if (optimizeBtn) optimizeBtn.style.display = 'none';
        return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const parsed = JSON.parse(e.target.result);
            window.userData = parsed;
            validationDiv.innerHTML = '<div class="format-valid">Valid format. Ready to optimize.</div>';
            if (optimizeBtn) optimizeBtn.style.display = 'block';
            updateDescription();
        } catch (error) {
            validationDiv.innerHTML = '<div class="format-error">Invalid JSON</div>';
            if (optimizeBtn) optimizeBtn.style.display = 'none';
        }
    };
    reader.readAsText(file);
}

async function updateDescription() {
    const instance = document.getElementById('instance').value;
    const container = document.getElementById('scenario-description');
    if (!instance) {
        container.innerHTML = '';
        return;
    }
    if (currentLevel === 'expert' && window.userData) {
        container.innerHTML = buildExpertDescription(window.userData);
        return;
    }
    try {
        const response = await fetch('/descriptions/' + instance + '.html?v=' + Date.now());
        if (!response.ok) throw new Error('No encontrada');
        const html = await response.text();
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p>Description not available</p>';
    }
}

function buildExpertDescription(data) {
    const items = [];
    for (const key of Object.keys(data)) {
        const value = data[key];
        if (Array.isArray(value)) {
            items.push(value.length + ' ' + key);
        } else if (typeof value === 'object' && value !== null) {
            items.push(key);
        } else {
            const display = typeof value === 'number' && Math.abs(value) >= 1000
                ? value.toLocaleString('en-US')
                : value;
            items.push(key + ': ' + display);
        }
    }
    const resumen = items.slice(0, 5).join(' | ');
    return '<p><strong>Custom data</strong></p>' +
           '<p>' + resumen + '</p>' +
           '<p style="color:#64748b; font-size:0.9em;">Optimizing with your data. Results appear on the right.</p>';
}
