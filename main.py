from fastapi import FastAPI
import random

app = FastAPI()

class VehicleHealthSystem:

    def __init__(self):
        self.vehicle_id = "Fortuner 0001"
        self.current_health = 69
        self.phase = "increasing"

    # -----------------------------
    # Health Simulation
    # -----------------------------
    def update_health(self):

        if self.phase == "increasing":
            self.current_health += random.randint(1, 4)

            if self.current_health >= 80:
                self.current_health = 80
                self.phase = "decreasing"

        else:  # decreasing phase
            self.current_health -= random.randint(1, 3)

            if self.current_health <= 55:
                self.current_health = 55  # minimum limit

        return round(self.current_health, 2)

    # -----------------------------
    # Sensor Generation Based on Health
    # -----------------------------
    def generate_sensor_data(self, health):

        engine_load = int(100 - health + random.randint(5, 12))
        brake_load = int(100 - health + random.randint(5, 10))
        gear_stress = int(100 - health + random.randint(5, 8))
        battery_load = int(100 - health + random.randint(5, 10))
        engine_temp = int(75 + (100 - health) + random.randint(0, 5))
        battery_health = int(health + random.randint(5, 10))

        return {
            "engine_load": min(engine_load, 95),
            "brake_load": min(brake_load, 95),
            "gear_stress": min(gear_stress, 95),
            "battery_load": min(battery_load, 95),
            "battery_health": min(battery_health, 100),
            "engine_temp": min(engine_temp, 120)
        }

    # -----------------------------
    # Alert Logic
    # -----------------------------
    def generate_alerts(self, data, health):
        alerts = []

        if data["engine_temp"] > 110:
            alerts.append("Engine Overheating - Immediate inspection required")

        if data["brake_load"] > 85:
            alerts.append("Brake Issue Detected - Service recommended")

        if data["gear_stress"] > 80:
            alerts.append("Clutch Plate Issue - Possible gear slipping")

        if data["battery_health"] < 60:
            alerts.append("Battery Degrading - Replacement advised")

        if health <= 60:
            alerts.append("Vehicle Health Dropping - Service Required")

        return alerts

    # -----------------------------
    # RUL Calculation
    # -----------------------------
    def calculate_rul(self, data, health):
        base_life_days = 365

        remaining_life = int((health / 100) * base_life_days)

        engine_factor = (100 - data["engine_load"]) / 100
        temp_penalty = max(0, data["engine_temp"] - 90) / 100
        engine_rul = int(base_life_days * engine_factor * (health / 100) * (1 - temp_penalty))

        brake_factor = (100 - data["brake_load"]) / 100
        brake_rul = int(base_life_days * brake_factor * (health / 100))

        gear_factor = (100 - data["gear_stress"]) / 100
        gear_rul = int(base_life_days * gear_factor * (health / 100))

        battery_factor = data["battery_health"] / 100
        battery_load_penalty = data["battery_load"] / 100
        battery_rul = int(base_life_days * battery_factor * (1 - battery_load_penalty))

        return (
            max(remaining_life, 0),
            max(engine_rul, 0),
            max(brake_rul, 0),
            max(gear_rul, 0),
            max(battery_rul, 0)
        )


system = VehicleHealthSystem()

@app.get("/")
def home():
    return {"message": "Vehicle Health API Running"}

@app.get("/vehicle")
def get_vehicle_data():

    health = system.update_health()
    data = system.generate_sensor_data(health)
    alerts = system.generate_alerts(data, health)

    remaining_life, engine_rul, brake_rul, gear_rul, battery_rul = system.calculate_rul(data, health)

    return {
        "vehicle_id": system.vehicle_id,
        "vehicle_health": health,
        "remaining_life_days": remaining_life,
        "engine_rul_days": engine_rul,
        "brake_rul_days": brake_rul,
        "gear_rul_days": gear_rul,
        "battery_rul_days": battery_rul,
        "engine_load": data["engine_load"],
        "brake_load": data["brake_load"],
        "gear_stress": data["gear_stress"],
        "battery_load": data["battery_load"],
        "battery_health_remaining": data["battery_health"],
        "engine_temperature": data["engine_temp"],
        "alerts": alerts
    }