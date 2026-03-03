from fastapi import FastAPI
import random

app = FastAPI()

class VehicleHealthSystem:

    def __init__(self):
        self.vehicle_id = "Fortuner 0001"
        self.health = 80.0
        self.call_count = 0

        self.engine_load = 40
        self.brake_load = 30
        self.gear_stress = 25
        self.battery_load = 35
        self.battery_health = 85
        self.engine_temp = 85

    # -----------------------------
    # Controlled Sensor Progression
    # -----------------------------
    def generate_sensor_data(self):
        self.call_count += 1

        self.engine_load += random.randint(1, 6)
        self.brake_load += random.randint(1, 5)
        self.gear_stress += random.randint(1, 4)
        self.battery_load += random.randint(1, 4)

        if self.call_count % 3 == 0:
            self.battery_health -= random.randint(1, 3)

        self.engine_temp = 80 + int(self.engine_load * 0.5)

        self.engine_load = min(self.engine_load, 95)
        self.brake_load = min(self.brake_load, 95)
        self.gear_stress = min(self.gear_stress, 95)
        self.battery_load = min(self.battery_load, 95)
        self.battery_health = max(self.battery_health, 50)

        return {
            "engine_load": self.engine_load,
            "brake_load": self.brake_load,
            "gear_stress": self.gear_stress,
            "battery_load": self.battery_load,
            "battery_health": self.battery_health,
            "engine_temp": self.engine_temp
        }

    # -----------------------------
    # Smooth Health Degradation + Oscillation
    # -----------------------------
    def calculate_health(self):

        # Phase 1: Degrade until 55
        if self.health > 55:
            drop = random.randint(1, 8)
            self.health -= drop
            self.health = max(self.health, 55)

        # Phase 2: Oscillate between 55 and 64
        else:
            change = random.randint(1, 5)

            if random.choice([True, False]):
                self.health += change
            else:
                self.health -= change

            self.health = max(55, min(self.health, 64))

        return round(self.health, 2)

    # -----------------------------
    # Alert Logic
    # -----------------------------
    def generate_alerts(self, data, health):
        alerts = []

        if self.call_count > 4:

            if data["engine_temp"] > 105:
                alerts.append("Engine Overheating - Immediate inspection required")

            if data["brake_load"] > 80:
                alerts.append("Brake Issue Detected - Service recommended")

            if data["gear_stress"] > 75:
                alerts.append("Clutch Plate Issue - Possible gear slipping")

            if data["battery_health"] < 60:
                alerts.append("Battery Degrading - Replacement advised")

            if health <= 60:
                alerts.append("Critical Vehicle Health - Urgent service required")

        return alerts

    # -----------------------------
    # RUL Logic
    # -----------------------------
    def calculate_rul(self, data, health):
        base_life_days = 365

        remaining_life = int((health / 100) * base_life_days)

        engine_rul = int((100 - data["engine_load"]) * health / 100)
        brake_rul = int((100 - data["brake_load"]) * health / 100)
        gear_rul = int((100 - data["gear_stress"]) * health / 100)
        battery_rul = int(data["battery_health"] * (100 - data["battery_load"]) / 100)

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
    data = system.generate_sensor_data()
    health = system.calculate_health()
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