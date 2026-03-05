document.getElementById('optimizeBtn').addEventListener('click', async () => {
    const problemType = document.getElementById('problemType').value;
    const instance = document.getElementById('instance').value;
    const output = document.getElementById('output');
    
    output.innerHTML = '<div style="text-align: center; color: #667eea;">⏳ Optimizando...</div>';
    
    try {
        const response = await fetch('/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                problem_type: problemType,
                instance: instance
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'optimal') {
            let html = `
                <div style="background: #f0f9ff; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                    <div style="font-size: 1.2rem; color: #1e293b;">🎯 Beneficio total esperado</div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: #059669; margin: 10px 0;">${data.objective_value} €</div>
                    <div style="font-size: 0.9rem; color: #64748b;">en un horizonte de 7 días, considerando ingresos, costes y penalizaciones por caducidad</div>
                </div>
                <h4 style="color: #1e293b; margin-bottom: 15px;">📦 Asignaciones óptimas</h4>
            `;
            
            if (data.asignaciones && data.asignaciones.length > 0) {
                html += '<table style="width: 100%; border-collapse: collapse;">';
                html += '<tr style="background: #e2e8f0; font-weight: 600;"><th style="padding: 12px; text-align: left;">Producto</th><th style="padding: 12px; text-align: left;">Tienda</th><th style="padding: 12px; text-align: right;">Unidades</th><th style="padding: 12px; text-align: right;">Exceso</th></tr>';
                
                data.asignaciones.forEach(a => {
                    html += `<tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 12px;">${a.producto}</td>
                        <td style="padding: 12px;">${a.tienda}</td>
                        <td style="padding: 12px; text-align: right;">${a.unidades}</td>
                        <td style="padding: 12px; text-align: right; color: ${a.exceso > 0 ? '#dc2626' : '#059669'};">${a.exceso}</td>
                    </tr>`;
                });
                
                html += '</table>';
            } else {
                html += '<p style="color: #64748b;">No hay asignaciones para mostrar</p>';
            }
            
            output.innerHTML = html;
        } else {
            output.innerHTML = `<div style="color: #dc2626; padding: 20px; background: #fee2e2; border-radius: 12px;">
                ❌ Error: No se pudo encontrar una solución óptima.
            </div>`;
        }
    } catch (error) {
        output.innerHTML = `<div style="color: #dc2626; padding: 20px; background: #fee2e2; border-radius: 12px;">
            ❌ Error de conexión: ${error.message}
        </div>`;
    }
});
