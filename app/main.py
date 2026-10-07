from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import json

try:
    from app.models.logistics.routing import RoutingModel
    print("RoutingModel importado")
except Exception as e:
    print(f"Error RoutingModel: {e}")
    RoutingModel = None

try:
    from app.models.assignment import AssignmentModel
    print("AssignmentModel importado")
except Exception as e:
    print(f"Error AssignmentModel: {e}")
    AssignmentModel = None

try:
    from app.models.inventory import InventoryModel
    print("InventoryModel importado")
except Exception as e:
    print(f"Error InventoryModel: {e}")
    InventoryModel = None

try:
    from app.models.portfolio import PortfolioModel
    print("PortfolioModel importado")
except Exception as e:
    print(f"Error PortfolioModel: {e}")
    PortfolioModel = None

app = FastAPI()

app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
app.mount("/descriptions", StaticFiles(directory="frontend/descriptions"), name="descriptions")
app.mount("/templates", StaticFiles(directory="frontend/templates"), name="templates")

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

        print(f"Recibido: {problem_type}/{instance}")
        if params:
            print(f"Parametros: {params}")

        if problem_type == "routing" and instance == "logistics_delivery":
            modelo = RoutingModel()
            if params:
                modelo.SetParams(params)
            modelo.cargar_datos("data/logistics/routing/logistics_murcia.json")
            if not modelo.build():
                return JSONResponse(status_code=500, content={"error": "Error build"})
            if not modelo.solve():
                return JSONResponse(status_code=500, content={"error": "No solucion"})
            return JSONResponse(content=modelo.get_results())

        elif problem_type == "assignment" and instance == "proyectos_equipos":
            modelo = AssignmentModel()
            if params:
                modelo.SetParams(params)
            modelo.cargar_datos("data/assignment/proyectos_equipos.json")
            if not modelo.build():
                return JSONResponse(status_code=500, content={"error": "Error build"})
            if not modelo.solve():
                return JSONResponse(status_code=500, content={"error": "No solucion"})
            return JSONResponse(content=modelo.get_results())

        elif problem_type == "inventory" and instance == "supermercado":
            modelo = InventoryModel()
            if params:
                modelo.SetParams(params)
            modelo.cargar_datos("data/inventory/supermercado.json")
            if not modelo.build():
                return JSONResponse(status_code=500, content={"error": "Error build"})
            if not modelo.solve():
                return JSONResponse(status_code=500, content={"error": "No solucion"})
            return JSONResponse(content=modelo.get_results())

        elif problem_type == "portfolio" and instance == "cartera_markowitz":
            modelo = PortfolioModel()
            if params:
                modelo.SetParams(params)
            modelo.cargar_datos("data/portfolio/cartera_markowitz.json")
            if not modelo.build():
                return JSONResponse(status_code=500, content={"error": "Error build"})
            if not modelo.solve():
                return JSONResponse(status_code=500, content={"error": "No solucion"})
            return JSONResponse(content=modelo.get_results())

        else:
            return JSONResponse(status_code=404, content={"error": f"No encontrado: {problem_type}/{instance}"})

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
