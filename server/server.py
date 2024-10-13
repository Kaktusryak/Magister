from flask import Flask, jsonify
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

app = Flask(__name__)

# Константа для розміру зони
ZONE_SIZE = 5.0  # Зона розміром 5x5 метрів
SENSOR_THRESHOLD_DISTANCE = 0.5  # Мінімальна відстань для виявлення об'єкта

@app.route('/start', methods=['GET'])
def start_simulation():
    try:
        # Підключаємося до CoppeliaSim через Remote API
        client = RemoteAPIClient()
        sim = client.require('sim')
        
        # Завантажуємо порожню сцену
        sim.loadScene('')  # Порожня сцена

        # Створюємо стіни навколо зони (квадратна зона)
        wall_thickness = 0.1  # Товщина стін 10 см
        wall_height = 1.0  # Висота стін 1 м

        # Ліва стіна
        left_wall_handle = sim.createPureShape(0, 16, [wall_thickness, ZONE_SIZE, wall_height], 0.0)
        sim.setObjectPosition(left_wall_handle, -1, [-ZONE_SIZE/2, 0, wall_height/2])

        # Права стіна
        right_wall_handle = sim.createPureShape(0, 16, [wall_thickness, ZONE_SIZE, wall_height], 0.0)
        sim.setObjectPosition(right_wall_handle, -1, [ZONE_SIZE/2, 0, wall_height/2])

        # Передня стіна
        front_wall_handle = sim.createPureShape(0, 16, [ZONE_SIZE, wall_thickness, wall_height], 0.0)
        sim.setObjectPosition(front_wall_handle, -1, [0, ZONE_SIZE/2, wall_height/2])

        # Задня стіна
        back_wall_handle = sim.createPureShape(0, 16, [ZONE_SIZE, wall_thickness, wall_height], 0.0)
        sim.setObjectPosition(back_wall_handle, -1, [0, -ZONE_SIZE/2, wall_height/2])

        # Завантажуємо модель робота Pioneer P3DX
        pioneer_handle = sim.loadModel('C:/Program Files/CoppeliaRobotics/CoppeliaSimEdu/models/robots/mobile/pioneer p3dx.ttm')

        # Отримуємо хендли двигунів робота
        left_motor_handle = sim.getObject('/PioneerP3DX/leftMotor')
        right_motor_handle = sim.getObject('/PioneerP3DX/rightMotor')

        # Додаємо куб перед роботом для сканування
        cube_handle = sim.createPureShape(0, 16, [0.2, 0.2, 0.2], 0.0)  # Створюємо куб (0.2 м по кожній осі)
        sim.setObjectPosition(cube_handle, -1, [1.0, 0.0, 0.2])  # Розміщуємо куб на 1 м перед роботом

        # Отримуємо хендли ультразвукових сенсорів (ultrasonicSensor[1] ... ultrasonicSensor[10])
        ultrasonic_sensors = []
        for i in range(1, 11):  # Assuming 10 ultrasonic sensors are named /PioneerP3DX/ultrasonicSensor[1], etc.
            sensor_handle = sim.getObject(f'/PioneerP3DX/ultrasonicSensor[{i}]')
            ultrasonic_sensors.append(sensor_handle)
        
        # Запускаємо симуляцію
        sim.startSimulation()

        # Рухаємо робота вперед
        sim.setJointTargetVelocity(left_motor_handle, 2.0)  # Ліве колесо вперед
        sim.setJointTargetVelocity(right_motor_handle, 2.0)  # Праве колесо вперед

        # Продовжуємо рух робота, поки не завершено сканування
        scanning_complete = False
        sensor_data = []

        while not scanning_complete:
            current_sensor_data = {}
            all_sensors_detected = True  # Перевіримо, чи всі сенсори виявили об'єкти

            for i, sensor in enumerate(ultrasonic_sensors):
                result, distance_data, *_ = sim.readProximitySensor(sensor)  # Отримуємо результат сканування
                if result > 0 and distance_data < SENSOR_THRESHOLD_DISTANCE:
                    current_sensor_data[f"sensor_{i+1}"] = distance_data
                else:
                    current_sensor_data[f"sensor_{i+1}"] = None
                    all_sensors_detected = False  # Якщо хоча б один сенсор не знайшов об'єкта, продовжуємо

            sensor_data.append(current_sensor_data)
            
            # Перевіряємо, чи всі сенсори виявили об'єкти
            if all_sensors_detected:
                scanning_complete = True  # Завершуємо рух, якщо всі сенсори знайшли об'єкти

            time.sleep(1)  # Затримка на 1 секунду між зчитуваннями

        # Зупиняємо рух робота після завершення сканування
        sim.setJointTargetVelocity(left_motor_handle, 0.0)
        sim.setJointTargetVelocity(right_motor_handle, 0.0)
        
        # Зупиняємо симуляцію
        sim.stopSimulation()
        
        # Відповідаємо успішно з результатами сканування
        return jsonify({"status": "Pioneer P3DX completed scan", "sensor_data": sensor_data}), 200

    except Exception as e:
        # Якщо виникла помилка, відправляємо її як відповідь
        return jsonify({"status": "Error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
