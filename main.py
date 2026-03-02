from fastapi import FastAPI
import random

app = FastAPI()

class VehicleHealthSystem:
    
    def generate_sensor_data(self):
        return {
            "engine_load": random.randint(20, 100),
            "brake_load": random.randint(10, 100),
            "gear_stress": random.randint(10, 100),
            "battery_load": random.randint(20, 100),
            "battery_health": random.randint(50, 100),
            "engine_temp": random.randint(70, 130)
        }
    
    def calculate_health(self, data):
        penalty = (
            0.3 * data["engine_load"] +
            0.2 * data["brake_load"] +
            0.2 * data["gear_stress"] +
            0.2 * data["battery_load"]
        )
        
        if data["engine_temp"] > 90:
            penalty += 0.5 * (data["engine_temp"] - 90)
            
        health = 100 - penalty
        return max(0, round(health, 2))
    
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
        
        if health < 40:
            alerts.append("Critical Vehicle Health - Urgent service required")
        
        return alerts


system = VehicleHealthSystem()


@app.get("/vehicle")
def get_vehicle_data():
    data = system.generate_sensor_data()
    health = system.calculate_health(data)
    alerts = system.generate_alerts(data, health)

    return {
        "vehicle_health": health,
        "engine_load": data["engine_load"],
        "brake_load": data["brake_load"],
        "gear_stress": data["gear_stress"],
        "battery_load": data["battery_load"],
        "battery_health_remaining": data["battery_health"],
        "engine_temperature": data["engine_temp"],
        "alerts": alerts
    }