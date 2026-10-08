from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

try:
    from app.models.logistics.routing import RoutingModel
    from app.models.assignment import AssignmentModel
    from app.models.inventory import InventoryModel
    from app.models.portfolio import PortfolioModel
    print("Todos los modelos importados correctamente")
except Exception as e:
    print(f"Error importando modelos: {e}")

MODEL_REGISTRY = {
    ("routing", "logistics_delivery"): {
        "class": RoutingModel,
        "data": "data/logistics/routing/logistics_murcia.json",
    },
    ("assignment", "proyectos_equipos"): {
        "class": AssignmentModel,
        "data": "data/assignment/proyectos_equipos.json",
    },
    ("inventory", "supermercado"): {
        "class": InventoryModel,
        "data": "data/inventory/supermercado.json",
    },
    ("portfolio", "cartera_markowitz"): {
        "class": PortfolioModel,
        "data": "data/portfolio/cartera_markowitz.json",
    },
}

app = FastAPI()

app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
app.mount("/descriptions", StaticFiles(directory="frontend/descriptions"), name="descriptions")
app.mount("/templates", StaticFiles(directory="frontend/templates"), name="templates")
app.mount("/examples", StaticFiles(directory="examples"), name="examples")

@app.get("/style.css")
async def css():
    return FileResponse("frontend/style.css")

@app.get("/script.js")
async def js():
    return FileResponse("frontend/script.js")

@app.get("/")
async def root():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/optimize")
async def optimize(request: Request):
    try:
        body = await request.json()
        problem_type = body.get("problem_type")
        instance = body.get("instance")
        params = body.get("params", None)
        user_data = body.get("user_data", None)

        print(f"Recibido: {problem_type}/{instance}")
        if params:
            print(f"Parametros: {params}")
        if user_data:
            print(f"Datos de usuario: {len(str(user_data))} bytes")

        key = (problem_type, instance)
        if key not in MODEL_REGISTRY:
            return JSONResponse(
                status_code=404,
                content={"error": f"Instancia no encontrada: {problem_type}/{instance}"}
            )

        entry = MODEL_REGISTRY[key]
        ModelClass = entry["class"]
        data_file = entry["data"]

        modelo = ModelClass()
        if params:
            modelo.SetParams(params)

        if user_data:
            modelo.cargar_datos(data_dict=user_data)
        else:
            modelo.cargar_datos(filename=data_file)

        if not modelo.build():
            return JSONResponse(status_code=500, content={"error": "Error construyendo el modelo"})
        if not modelo.solve():
            return JSONResponse(status_code=500, content={"error": "No se encontro solucion"})

        return JSONResponse(content=modelo.get_results())

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
