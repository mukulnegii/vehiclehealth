from fastapi import FastAPI
import random

app = FastAPI()

class VehicleHealthSystem:
    
    def __init__(self):
        self.instance_count = 0
        self.last_health = None   # Track previous health
    
    def generate_sensor_data(self):
        return {
            "engine_load": random.randint(20, 100),
            "brake_load": random.randint(10, 100),
            "gear_stress": random.randint(10, 100),
            "battery_load": random.randint(20, 100),
            "battery_health": random.randint(50, 100),
            "engine_temp": random.randint(70, 130)
        }
    
    # ✅ Health restricted 50–70 and never same twice
    def calculate_health(self, data):
        while True:
            penalty = (
                0.3 * data["engine_load"] +
                0.2 * data["brake_load"] +
                0.2 * data["gear_stress"] +
                0.2 * data["battery_load"]
            )
            
            if data["engine_temp"] > 90:
                penalty += 0.5 * (data["engine_temp"] - 90)
                
            health = 100 - penalty
            health = max(50, min(70, health))
            health = round(health, 2)

            # Ensure not same as last value
            if health != self.last_health:
                self.last_health = health
                return health
            
            # Slight random adjustment if same
            data["engine_load"] = random.randint(20, 100)

    # ✅ Alerts only after 5 calls
    def generate_alerts(self, data, health):
        alerts = []
        
        if self.instance_count < 5:
            return alerts
        
        if data["engine_temp"] > 110:
            alerts.append("Engine Overheating - Immediate inspection required")
        
        if data["brake_load"] > 85:
            alerts.append("Brake Issue Detected - Service recommended")
        
        if data["gear_stress"] > 80:
            alerts.append("Clutch Plate Issue - Possible gear slipping")
        
        if data["battery_health"] < 60:
            alerts.append("Battery Degrading - Replacement advised")
        
        if health < 55:
            alerts.append("Critical Vehicle Health - Urgent service required")
        
        return alerts

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
    
    system.instance_count += 1
    
    data = system.generate_sensor_data()
    health = system.calculate_health(data)
    alerts = system.generate_alerts(data, health)

    remaining_life, engine_rul, brake_rul, gear_rul, battery_rul = system.calculate_rul(data, health)

    return {
        "vehicle_id": "Fortuner 0001",
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