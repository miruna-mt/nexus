document.getElementById('optimizeBtn').addEventListener('click', async () => {
    const problemType = document.getElementById('problemType').value;
    const instance = document.getElementById('instance').value;
    const output = document.getElementById('output');
    
    output.textContent = 'Optimizando...';
    
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
        output.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        output.textContent = 'Error: ' + error.message;
    }
});
