console.log('Selector de problemas:', document.getElementById('problemType').innerHTML);

// Configuración de las instancias (se cargará dinámicamente)
let instancesConfig = {};

// Nivel activo
let currentLevel = 'demo';

// Cargar configuración al iniciar
document.addEventListener('DOMContentLoaded', async () => {
    await loadInstancesConfig();
    setupEventListeners();
    updateLevelContent('demo');
    updateScenarioDescription();
});

// Cargar configuración de todas las instancias
async function loadInstancesConfig() {
    instancesConfig = {
        'fmcg_productos_tiendas': {
            name: 'Supermercado · Productos a Tiendas',
            parametric: {
                parameters: [
                    { name: 'stock_leche', label: 'Stock de leche', type: 'slider', min: 1000, max: 20000, default: 5000, unit: 'uds' },
                    { name: 'capacidad_hiper', label: 'Capacidad Hiper Centro', type: 'slider', min: 5000, max: 50000, default: 20000, unit: 'uds' }
                ]
            },
            expert: {
                expectedSchema: ['productos', 'tiendas', 'demanda_estimada']
            }
        },
        'defense_missions': {
            name: 'Defensa · Asignación de Misiones',
            parametric: {
                parameters: [
                    { name: 'prioridad_rescate', label: 'Prioridad rescate', type: 'slider', min: 1, max: 10, default: 10, unit: '' },
                    { name: 'num_helicopteros', label: 'Número de helicópteros', type: 'slider', min: 1, max: 5, default: 2, unit: '' }
                ]
            },
            expert: {
                expectedSchema: ['resources', 'missions']
            }
        },
        'cloud_vms': {
            name: 'Cloud · Asignación de VMs',
            parametric: {
                parameters: [
                    { name: 'cpu_web', label: 'CPU servidores web', type: 'slider', min: 2, max: 16, default: 4, unit: 'cores' },
                    { name: 'ram_db', label: 'RAM base de datos', type: 'slider', min: 8, max: 64, default: 32, unit: 'GB' }
                ]
            },
            expert: {
                expectedSchema: ['servers', 'vms']
            }
        }
    };
}

// Configurar event listeners
function setupEventListeners() {
    // Selector de nivel
    document.querySelectorAll('.level-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.level-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentLevel = btn.dataset.level;
            updateLevelContent(currentLevel);
        });
    });

    // Selectores de problema/instancia
    document.getElementById('problemType').addEventListener('change', updateScenarioDescription);
    document.getElementById('instance').addEventListener('change', () => {
        updateScenarioDescription();
        updateLevelContent(currentLevel);
    });
}

// Actualizar contenido según nivel
function updateLevelContent(level) {
    const instance = document.getElementById('instance').value;
    const container = document.getElementById('level-content');
    
    if (!instance) {
        container.innerHTML = '<p style="color: #64748b; text-align: center;">Selecciona un escenario primero</p>';
        return;
    }
    
    const config = instancesConfig[instance];
    if (!config) return;
    
    switch(level) {
        case 'demo':
            container.innerHTML = generateDemoHTML(config);
            attachDemoEvents();
            break;
        case 'parametric':
            container.innerHTML = generateParametricHTML(config);
            attachParametricEvents();
            break;
        case 'expert':
            container.innerHTML = generateExpertHTML(config);
            attachExpertEvents();
            break;
    }
}

// Generar HTML para cada nivel
function generateDemoHTML(config) {
    return `
        <div class="demo-container">
            <p style="color: #475569; margin-bottom: 15px;">Escenario predefinido con datos de ejemplo.</p>
            <button id="optimizeBtn" class="optimize-btn">⚡ Optimizar con datos demo</button>
        </div>
    `;
}

function generateParametricHTML(config) {
    let html = '<div class="parametric-container"><h4 style="margin-bottom: 20px;">Ajusta los parámetros:</h4>';
    
    config.parametric.parameters.forEach(param => {
        html += `
            <div class="parameter-item">
                <div class="parameter-label">
                    <span>${param.label}</span>
                    <span class="parameter-value" data-param="${param.name}">${param.default} ${param.unit || ''}</span>
                </div>
                <input type="range" class="parameter-slider" 
                    data-param="${param.name}"
                    min="${param.min}" max="${param.max}" value="${param.default}" 
                    step="1">
            </div>
        `;
    });
    
    html += '<button id="optimizeBtn" class="optimize-btn" style="margin-top: 20px;">🔧 Optimizar con estos valores</button></div>';
    return html;
}

function generateExpertHTML(config) {
    return `
        <div class="expert-container">
            <h4 style="margin-bottom: 15px;">Sube tu propio archivo JSON</h4>
            <div class="file-upload-area" id="fileUploadArea">
                <div class="upload-icon">📁</div>
                <div class="upload-text">Arrastra tu archivo JSON o haz clic para seleccionar</div>
                <div class="upload-hint">Formato esperado: ${config.expert.expectedSchema.join(', ')}</div>
                <input type="file" id="fileInput" accept=".json" style="display: none;">
           </div>
            <div id="validationResult" style="margin-top: 15px;"></div>
            <button id="optimizeBtn" class="optimize-btn" style="margin-top: 20px; display: none;">📁 Optimizar con mis datos</button>
        </div>
    `;
}

// Eventos específicos de cada nivel
function attachDemoEvents() {
    document.getElementById('optimizeBtn')?.addEventListener('click', async () => {
        const instance = document.getElementById('instance').value;
        const output = document.getElementById('output');
        output.innerHTML = '⏳ Optimizando...';
        
        try {
            // 1. Llamar al backend
            const response = await fetch('/optimize', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    problem_type: 'assignment',
                    instance: instance
                })
            });
            
            const data = await response.json();
            
            // 2. Cargar la plantilla correspondiente
            const templateResponse = await fetch(`/templates/${instance}.html`);
            let template = await templateResponse.text();
            
            // 3. Función simple de renderizado
            function renderSimple(template, data) {
                return template.replace(/\{\{([^}]+)\}\}/g, (match, key) => {
                    return data[key.trim()] !== undefined ? data[key.trim()] : match;
                });
            }
            
            // 4. Procesar bucles {{#each ...}} (versión simplificada)
            const eachRegex = /\{\{#each (\w+)\}\}(.*?)\{\{\/each\}\}/gs;
            let match;
            while ((match = eachRegex.exec(template)) !== null) {
                const [fullMatch, arrayName, itemTemplate] = match;
                const array = data[arrayName] || [];
                let itemsHtml = '';
                array.forEach(item => {
                    itemsHtml += renderSimple(itemTemplate, item);
                });
                template = template.replace(fullMatch, itemsHtml);
            }
            
            // 5. Renderizar el resto de variables
            let finalHtml = renderSimple(template, data);
            
            // 6. Mostrar resultados
            output.innerHTML = `<div style="background: #f0f9ff; padding: 20px; border-radius: 12px;">${finalHtml}</div>`;
            
        } catch (error) {
            output.innerHTML = '❌ Error: ' + error.message;
        }
    });
}

function attachParametricEvents() {
    document.querySelectorAll('.parameter-slider').forEach(slider => {
        slider.addEventListener('input', (e) => {
            const param = e.target.dataset.param;
            const value = e.target.value;
            document.querySelector(`.parameter-value[data-param="${param}"]`).textContent = value;
        });
    });
    
    document.getElementById('optimizeBtn')?.addEventListener('click', () => {
        console.log('Optimizar con parámetros personalizados');
        // Aquí irá la lógica de recoger valores y llamar al backend
    });
}

function attachExpertEvents() {
    const uploadArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        handleFileUpload(file);
    });
    
    fileInput.addEventListener('change', (e) => {
        handleFileUpload(e.target.files[0]);
    });
}

function handleFileUpload(file) {
    const validationDiv = document.getElementById('validationResult');
    const optimizeBtn = document.getElementById('optimizeBtn');
    
    if (!file || file.type !== 'application/json') {
        validationDiv.innerHTML = '<div class="format-error">❌ El archivo debe ser JSON</div>';
        optimizeBtn.style.display = 'none';
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const data = JSON.parse(e.target.result);
            validationDiv.innerHTML = '<div class="format-valid">✅ Formato válido. Listo para optimizar.</div>';
            optimizeBtn.style.display = 'block';
        } catch (error) {
            validationDiv.innerHTML = '<div class="format-error">❌ JSON inválido</div>';
            optimizeBtn.style.display = 'none';
        }
    };
    reader.readAsText(file);
}

async function updateScenarioDescription() {
    const instance = document.getElementById('instance').value;
    const container = document.getElementById('scenario-description');
    
    if (!instance) {
        container.innerHTML = '<p>Selecciona una instancia</p>';
        return;
    }
    
    try {
        const response = await fetch(`/descriptions/${instance}.html`);
        if (!response.ok) throw new Error('No encontrada');
        const html = await response.text();
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<p style="color: #dc2626;">Descripción no disponible para ${instance}</p>`;
    }
}

function renderTemplate(template, data) {
    return template.replace(/\{\{([^}]+)\}\}/g, (match, key) => {
        return data[key.trim()] || match;
    });
}
