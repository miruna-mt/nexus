console.log('Script cargado');

const instancesConfig = {
    'logistics_delivery': {
        name: 'Logistica - Reparto Agroalimentario',
        problem_type: 'routing',
        description: 'Reparto de productos agricolas a plataformas y mercados.',
        parametric: {
            parameters: [
                { name: 'num_vehiculos', label: 'Numero de vehiculos', type: 'slider', min: 1, max: 4, default: 4, unit: '' },
                { name: 'num_clientes', label: 'Numero de clientes a visitar', type: 'slider', min: 5, max: 14, default: 14, unit: '' }
            ]
        },
        expert: { expectedSchema: ['vehiculos', 'clientes', 'distancias'] }
    },
    'proyectos_equipos': {
        name: 'Asignacion - Proyectos a Equipos',
        problem_type: 'assignment',
        description: 'Asigna proyectos a equipos especializados maximizando el valor total.',
        parametric: {
            parameters: [
                { name: 'capacidad_equipos', label: 'Capacidad de los equipos (%)', type: 'slider', min: 50, max: 200, default: 100, unit: '%' },
                { name: 'bonus_gran_empresa', label: 'Bonus gran empresa (EUR)', type: 'slider', min: 0, max: 20000, default: 0, unit: 'EUR', step: 1000 }
            ]
        },
        expert: { expectedSchema: ['proyectos', 'equipos'] }
    },
    'supermercado': {
        name: 'Inventario - Supermercado',
        problem_type: 'inventory',
        description: 'Optimiza pedidos y stock de productos perecederos.',
        parametric: {
            parameters: [
                { name: 'coste_pedido', label: 'Coste por pedido (EUR)', type: 'slider', min: 10, max: 200, default: 50, unit: 'EUR', step: 5 },
                { name: 'coste_almacenaje', label: 'Coste almacenaje (EUR/ud/sem)', type: 'slider', min: 0.01, max: 0.20, default: 0.05, unit: 'EUR', step: 0.01 },
                { name: 'coste_rotura', label: 'Coste rotura (EUR/ud)', type: 'slider', min: 0.5, max: 5.0, default: 2.0, unit: 'EUR', step: 0.1 }
            ]
        },
        expert: { expectedSchema: ['horizonte_semanas', 'capacidad_almacen', 'productos'] }
    },
    'cartera_markowitz': {
        name: 'Portfolio - Cartera Markowitz',
        problem_type: 'portfolio',
        description: 'Optimiza una cartera de inversion maximizando rentabilidad ajustada por riesgo.',
        parametric: {
            parameters: [
                { name: 'aversion_riesgo', label: 'Aversion al riesgo', type: 'slider', min: 0, max: 10, default: 2, unit: '' },
                { name: 'rentabilidad_tech', label: 'Rentabilidad Tech (%)', type: 'slider', min: 5, max: 25, default: 12, unit: '%' }
            ]
        },
        expert: { expectedSchema: ['capital_total', 'aversion_riesgo', 'activos'] }
    }
};

let currentLevel = 'demo';
let map = null;

document.addEventListener('DOMContentLoaded', () => {
    const instanceSelect = document.getElementById('instance');
    if (instanceSelect) {
        while (instanceSelect.options.length > 1) {
            instanceSelect.remove(1);
        }
        for (const [key, config] of Object.entries(instancesConfig)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = config.name;
            instanceSelect.appendChild(option);
        }
    }
    setupLevelButtons();
    setupInstanceSelector();
    updateLevelContent('demo');
    updateDescription();
});

function setupLevelButtons() {
    document.querySelectorAll('.level-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.level-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentLevel = btn.dataset.level;
            updateLevelContent(currentLevel);
        });
    });
}

function setupInstanceSelector() {
    const instanceSelect = document.getElementById('instance');
    if (instanceSelect) {
        instanceSelect.addEventListener('change', () => {
            updateDescription();
            updateLevelContent(currentLevel);
        });
    }
}

function updateLevelContent(level) {
    const instance = document.getElementById('instance').value;
    const container = document.getElementById('level-content');
    if (!instance) {
        container.innerHTML = '<p style="color: #64748b; text-align: center;">Selecciona un escenario primero</p>';
        return;
    }
    const config = instancesConfig[instance];
    if (!config) {
        container.innerHTML = '<p style="color: #dc2626; text-align: center;">Configuracion no encontrada</p>';
        return;
    }
    if (level === 'demo') {
        container.innerHTML = generateDemoHTML(config);
        attachOptimizeEvent(false);
    } else if (level === 'parametric') {
        container.innerHTML = generateParametricHTML(config);
        attachParametricEvents();
    } else if (level === 'expert') {
        container.innerHTML = generateExpertHTML(config);
        attachExpertEvents();
    }
}

function generateDemoHTML(config) {
    return '<div class="demo-container"><p style="color: #475569; margin-bottom: 15px;">Escenario predefinido con datos de ejemplo.</p><button id="optimizeBtn" class="optimize-btn">Optimizar con datos demo</button></div>';
}

function generateParametricHTML(config) {
    let html = '<div class="parametric-container"><h4 style="margin-bottom: 20px;">Ajusta los parametros:</h4>';
    if (config.parametric && config.parametric.parameters && config.parametric.parameters.length > 0) {
        config.parametric.parameters.forEach(param => {
            const step = param.step || 1;
            html += '<div class="parameter-item"><div class="parameter-label"><span>' + param.label + '</span><span class="parameter-value" data-param="' + param.name + '">' + param.default + ' ' + (param.unit || '') + '</span></div><input type="range" class="parameter-slider" data-param="' + param.name + '" min="' + param.min + '" max="' + param.max + '" value="' + param.default + '" step="' + step + '"></div>';
        });
    } else {
        html += '<p>No hay parametros ajustables</p>';
    }
    html += '<button id="optimizeBtn" class="optimize-btn" style="margin-top: 20px;">Optimizar con estos valores</button></div>';
    return html;
}

function generateExpertHTML(config) {
    return '<div class="expert-container"><h4 style="margin-bottom: 15px;">Sube tu propio archivo JSON</h4><div class="file-upload-area" id="fileUploadArea"><div class="upload-icon">Folder</div><div class="upload-text">Arrastra tu archivo JSON o haz clic para seleccionar</div><div class="upload-hint">Formato esperado: ' + (config.expert && config.expert.expectedSchema ? config.expert.expectedSchema.join(', ') : 'definir') + '</div><input type="file" id="fileInput" accept=".json" style="display: none;"></div><div id="validationResult" style="margin-top: 15px;"></div><button id="optimizeBtn" class="optimize-btn" style="margin-top: 20px; display: none;">Optimizar con mis datos</button></div>';
}

function attachOptimizeEvent(isParametric) {
    const btn = document.getElementById('optimizeBtn');
    if (!btn) return;
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);

    newBtn.addEventListener('click', async () => {
        const instance = document.getElementById('instance').value;
        const config = instancesConfig[instance];
        const output = document.getElementById('output');
        if (!config) return;

        output.innerHTML = '<div style="text-align: center; color: #667eea;">Optimizando...</div>';

        const payload = { problem_type: config.problem_type, instance: instance };

        if (isParametric) {
            const params = {};
            document.querySelectorAll('.parameter-slider').forEach(slider => {
                params[slider.dataset.param] = slider.value;
            });
            payload.params = params;
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
                    html += '<div style="font-size: 0.95rem; margin-bottom: 10px; opacity: 0.95; line-height: 1.5;"><strong>Comparacion:</strong> ' + data.narrative.comparacion + '</div>';
                    html += '<div style="font-size: 0.95rem; opacity: 0.95; line-height: 1.5;"><strong>Insight:</strong> ' + data.narrative.insight + '</div>';
                    html += '</div>';
                }

                if (config.problem_type === 'routing') {
                    html += '<div style="background: #f0f9ff; padding: 20px; border-radius: 12px; margin-bottom: 20px;"><div style="font-size: 1.2rem; color: #1e293b;">Distancia total recorrida</div><div style="font-size: 2.5rem; font-weight: 700; color: #059669; margin: 10px 0;">' + data.objective_value + ' km</div></div>';
                    html += '<h4 style="color: #1e293b; margin-bottom: 15px;">Rutas asignadas</h4><div style="display: flex; flex-direction: column; gap: 15px;">';
                    if (data.rutas && data.rutas.length > 0) {
                        data.rutas.forEach(ruta => {
                            html += '<div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px;"><div style="font-weight: 700; color: #1e293b; margin-bottom: 8px;">' + ruta.vehiculo + '</div><div style="color: #475569; margin-bottom: 8px;">Paradas: ' + ruta.paradas.join(' -> ') + '</div><div style="color: #059669; font-weight: 600;">Distancia: ' + ruta.distancia + ' km</div></div>';
                        });
                    }
                    html += '</div>';
                    html += '<div id="map" style="height: 450px; margin-top: 20px; border-radius: 12px; background: #e2e8f0;"></div>';
                } else if (config.problem_type === 'assignment') {
                    html += '<div style="background: #f0f9ff; padding: 20px; border-radius: 12px; margin-bottom: 20px;"><div style="font-size: 1.2rem; color: #1e293b;">Valor total asignado</div><div style="font-size: 2.5rem; font-weight: 700; color: #059669; margin: 10px 0;">' + data.objective_value.toLocaleString('es-ES') + ' EUR</div></div>';
                    html += '<h4 style="color: #1e293b; margin-bottom: 15px;">Asignaciones</h4><table style="width: 100%; border-collapse: collapse;"><tr style="background: #e2e8f0; font-weight: 600;"><th style="padding: 10px; text-align: left;">Proyecto</th><th style="padding: 10px; text-align: left;">Equipo</th><th style="padding: 10px; text-align: right;">Horas</th><th style="padding: 10px; text-align: right;">Valor</th></tr>';
                    data.asignaciones.forEach(a => {
                        html += '<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px;">' + a.proyecto + '</td><td style="padding: 10px;">' + a.equipo + '</td><td style="padding: 10px; text-align: right;">' + a.horas + '</td><td style="padding: 10px; text-align: right; color: #059669; font-weight: 600;">' + a.valor.toLocaleString('es-ES') + ' EUR</td></tr>';
                    });
                    html += '</table>';
                } else if (config.problem_type === 'inventory') {
                    html += '<div style="background: #fef3c7; padding: 20px; border-radius: 12px; margin-bottom: 20px;"><div style="font-size: 1.2rem; color: #1e293b;">Coste total de inventario</div><div style="font-size: 2.5rem; font-weight: 700; color: #d97706; margin: 10px 0;">' + data.objective_value.toLocaleString('es-ES', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' EUR</div></div>';
                    html += '<h4 style="color: #1e293b; margin-bottom: 15px;">Resumen por producto</h4><table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;"><tr style="background: #e2e8f0; font-weight: 600;"><th style="padding: 10px; text-align: left;">Producto</th><th style="padding: 10px; text-align: right;">Total pedido</th><th style="padding: 10px; text-align: right;">Roturas</th><th style="padding: 10px; text-align: right;">Stock final</th></tr>';
                    data.resumen.forEach(r => {
                        const color = r.total_rotura > 0 ? '#dc2626' : '#059669';
                        html += '<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px;">' + r.producto + '</td><td style="padding: 10px; text-align: right;">' + r.total_pedido + ' uds</td><td style="padding: 10px; text-align: right; color: ' + color + ';">' + r.total_rotura + ' uds</td><td style="padding: 10px; text-align: right;">' + r.stock_final + ' uds</td></tr>';
                    });
                    html += '</table>';
                } else if (config.problem_type === 'portfolio') {
                    html += '<div style="background: #ecfdf5; padding: 20px; border-radius: 12px; margin-bottom: 20px;"><div style="font-size: 1.2rem; color: #1e293b;">Rentabilidad esperada de la cartera</div><div style="font-size: 2.5rem; font-weight: 700; color: #059669; margin: 10px 0;">' + data.rentabilidad_esperada_pct + ' %</div><div style="font-size: 0.9rem; color: #64748b;">con un riesgo estimado del ' + data.riesgo_estimado_pct + '%</div></div>';
                    html += '<h4 style="color: #1e293b; margin-bottom: 15px;">Composicion de la cartera</h4><table style="width: 100%; border-collapse: collapse;"><tr style="background: #e2e8f0; font-weight: 600;"><th style="padding: 10px; text-align: left;">Activo</th><th style="padding: 10px; text-align: right;">Peso</th><th style="padding: 10px; text-align: right;">Inversion</th><th style="padding: 10px; text-align: right;">Rentabilidad</th><th style="padding: 10px; text-align: right;">Riesgo</th></tr>';
                    data.cartera.forEach(c => {
                        html += '<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px;">' + c.activo + '</td><td style="padding: 10px; text-align: right; font-weight: 600;">' + c.peso_pct + ' %</td><td style="padding: 10px; text-align: right;">' + c.inversion.toLocaleString('es-ES') + ' EUR</td><td style="padding: 10px; text-align: right; color: #059669;">' + c.rentabilidad_pct + ' %</td><td style="padding: 10px; text-align: right; color: #dc2626;">' + c.riesgo_pct + ' %</td></tr>';
                    });
                    html += '</table>';
                }

                output.innerHTML = html;

                if (config.problem_type === 'routing' && data.rutas && data.rutas.length > 0) {
                    setTimeout(() => dibujarMapa(data.rutas), 100);
                }
            } else {
                output.innerHTML = '<div style="color: #dc2626;">Error: ' + (data.error || 'Optimizacion fallida') + '</div>';
            }
        } catch (error) {
            console.error('Error:', error);
            output.innerHTML = '<div style="color: #dc2626;">Error de conexion: ' + error.message + '</div>';
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
                const punto = ruta.paradas && ruta.paradas[i] ? ruta.paradas[i] : (i === 0 ? 'Deposito' : 'Punto');
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
    attachOptimizeEvent(true);
}

function attachExpertEvents() {
    const uploadArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('fileInput');
    if (uploadArea) {
        uploadArea.addEventListener('click', () => fileInput.click());
    }
    if (fileInput) {
        fileInput.addEventListener('change', (e) => handleFileUpload(e.target.files[0]));
    }
    attachOptimizeEvent(false);
}

function handleFileUpload(file) {
    const validationDiv = document.getElementById('validationResult');
    if (!file || file.type !== 'application/json') {
        validationDiv.innerHTML = '<div class="format-error">El archivo debe ser JSON</div>';
        return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            JSON.parse(e.target.result);
            validationDiv.innerHTML = '<div class="format-valid">Formato valido</div>';
        } catch (error) {
            validationDiv.innerHTML = '<div class="format-error">JSON invalido</div>';
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
    try {
        const response = await fetch('/descriptions/' + instance + '.html');
        if (!response.ok) throw new Error('No encontrada');
        const html = await response.text();
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p>Descripcion no disponible</p>';
    }
}
