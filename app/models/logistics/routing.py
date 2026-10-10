from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import json
import math


def _normalize_data(data):
    """Accept both English and Spanish field names.
    Returns a dict with Spanish keys (internal canonical format)."""
    def pick(d, *keys):
        for k in keys:
            if k in d:
                return d[k]
        raise KeyError("None of " + str(keys) + " found in " + str(list(d.keys())))

    def norm_vehicle(v):
        return {
            "id": v.get("id"),
            "capacidad": pick(v, "capacity", "capacidad"),
            "costo_km": v.get("cost_per_km", v.get("costo_km", 1.0)),
        }

    def norm_client(c):
        return {
            "id": c.get("id"),
            "nombre": pick(c, "name", "nombre"),
            "demanda": pick(c, "demand", "demanda"),
            "x": pick(c, "lat", "x"),
            "y": pick(c, "lon", "y"),
            "ventana_inicio": c.get("time_window_start", c.get("ventana_inicio", 0)),
            "ventana_fin": c.get("time_window_end", c.get("ventana_fin", 1000)),
        }

    depot_src = data.get("depot", data.get("deposito", {}))

    return {
        "vehiculos": [norm_vehicle(v) for v in pick(data, "vehicles", "vehiculos")],
        "clientes":  [norm_client(c)  for c in pick(data, "clients",  "clientes")],
        "deposito": {
            "id":     depot_src.get("id", 0),
            "nombre": pick(depot_src, "name", "nombre"),
            "x":      pick(depot_src, "lat", "x"),
            "y":      pick(depot_src, "lon", "y"),
        },
    }


class RoutingModel:
    def __init__(self):
        self.name = "Logistica - Reparto Agroalimentario"
        self.description = "Optimizacion de rutas con multiples vehiculos"
        self.clientes = []
        self.params = None

    def SetParams(self, params):
        self.params = params
        print(f"Parametros recibidos: {params}")

    def cargar_datos(self, filename=None, data_dict=None):
        if data_dict is not None:
            data = data_dict
        elif filename is not None:
            with open(filename, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
        else:
            raise ValueError("cargar_datos necesita 'filename' o 'data_dict'")

        # Normalizar nombres de campos (ES o EN)
        data = _normalize_data(data)

        # Filtrar vehiculos segun parametro
        vehiculos = data["vehiculos"]
        if self.params and "num_vehiculos" in self.params:
            num = int(self.params["num_vehiculos"])
            if num < len(vehiculos):
                vehiculos = vehiculos[:num]
                print(f"Usando {num} vehiculos (de {len(data['vehiculos'])} disponibles)")

        # Filtrar clientes segun parametro
        clientes = data["clientes"]
        if self.params and "num_clientes" in self.params:
            num_cli = int(self.params["num_clientes"])
            if num_cli < len(clientes):
                clientes = clientes[:num_cli]
                print(f"Usando {num_cli} clientes (de {len(data['clientes'])} disponibles)")

        self.num_vehiculos = len(vehiculos)
        self.deposito = 0
        self.clientes = clientes
        self.deposito_lat = data["deposito"]["x"]
        self.deposito_lon = data["deposito"]["y"]

        puntos = [(data["deposito"]["x"], data["deposito"]["y"])]
        for cliente in clientes:
            puntos.append((cliente["x"], cliente["y"]))

        num_puntos = len(puntos)
        self.distancias = [[0] * num_puntos for _ in range(num_puntos)]

        def distancia_haversine(lat1, lon1, lat2, lon2):
            R = 6371
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        for i in range(num_puntos):
            for j in range(num_puntos):
                if i != j:
                    dist = distancia_haversine(puntos[i][0], puntos[i][1], puntos[j][0], puntos[j][1])
                    self.distancias[i][j] = int(dist * 1000)

        self.num_clientes = num_puntos - 1
        self.demandas = [0]
        for cliente in clientes:
            self.demandas.append(cliente["demanda"])
        self.capacidades = [v["capacidad"] for v in vehiculos]

    def build(self):
        print("Construyendo modelo de rutas...")
        self.manager = pywrapcp.RoutingIndexManager(len(self.distancias), self.num_vehiculos, self.deposito)
        self.routing = pywrapcp.RoutingModel(self.manager)

        def distance_callback(from_index, to_index):
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            return self.distancias[from_node][to_node]

        transit_callback_index = self.routing.RegisterTransitCallback(distance_callback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        def demand_callback(from_index):
            from_node = self.manager.IndexToNode(from_index)
            return self.demandas[from_node]

        demand_callback_index = self.routing.RegisterUnaryTransitCallback(demand_callback)
        self.routing.AddDimensionWithVehicleCapacity(demand_callback_index, 0, self.capacidades, True, "Capacity")

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        search_parameters.time_limit.seconds = 5

        self.solution = self.routing.SolveWithParameters(search_parameters)
        return self.solution is not None

    def solve(self):
        return self.solution is not None

    def get_results(self):
        if self.solution is None:
            return {"status": "error", "message": "No solution found"}

        total_distance = 0
        rutas = []

        for vehicle_id in range(self.num_vehiculos):
            index = self.routing.Start(vehicle_id)
            if self.routing.IsEnd(index):
                continue

            ruta = {"vehiculo": f"Vehiculo {vehicle_id+1}", "paradas": [], "coordenadas": []}
            route_distance = 0

            while not self.routing.IsEnd(index):
                node_index = self.manager.IndexToNode(index)
                if node_index != self.deposito:
                    nombre_cliente = self.clientes[node_index - 1]["nombre"]
                    ruta["paradas"].append(nombre_cliente)
                    lat = self.clientes[node_index - 1]["x"]
                    lon = self.clientes[node_index - 1]["y"]
                else:
                    lat = self.deposito_lat
                    lon = self.deposito_lon

                ruta["coordenadas"].append({"lat": lat, "lon": lon})

                next_index = self.solution.Value(self.routing.NextVar(index))
                route_distance += self.routing.GetArcCostForVehicle(index, next_index, vehicle_id)
                index = next_index

            ruta["distancia"] = round(route_distance / 1000, 1)
            total_distance += route_distance
            if ruta["paradas"]:
                rutas.append(ruta)

        total_distance_km = round(total_distance / 1000, 1)
        velocidad_media_kmh = 50
        jornada_maxima_horas = 8
        tiempo_total_horas = total_distance_km / velocidad_media_kmh
        jornadas = math.ceil(tiempo_total_horas / jornada_maxima_horas)

        num_vehiculos_usados = len(rutas)
        num_clientes_visitados = sum(len(r["paradas"]) for r in rutas)
        vehiculos_str = f"{num_vehiculos_usados} of {self.num_vehiculos}"

        insight = "Stops grouped geographically to minimize travel."
        warning = None
        max_hours = 0.0
        max_vehiculo = None
        for r in rutas:
            h = r["distancia"] / 60.0
            if h > max_hours:
                max_hours = h
                max_vehiculo = r["vehiculo"]
        if max_hours > 8:
            warning = f"\u26A0 {max_vehiculo}'s route is ~{round(max_hours, 1)}h \u2014 exceeds a single driving day. Consider multi-day scheduling or additional vehicles."

        narrative = {
            "titular": f"Optimal route \u00B7 {total_distance_km} km \u00B7 {vehiculos_str} vehicles \u00B7 {num_clientes_visitados} stops",
            "comparacion": f"Serving each stop as a separate round trip: ~{round(2 * total_distance_km, 1)} km.",
            "insight": insight,
            "warning": warning
        }

        return {
            "status": "optimal",
            "objective_value": total_distance_km,
            "rutas": rutas,
            "unidad": "km",
            "tiempo_estimado_horas": round(tiempo_total_horas, 1),
            "jornadas_necesarias": jornadas,
            "narrative": narrative
        }
