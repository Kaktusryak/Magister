from flask import Flask, jsonify
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time
import math
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)

ZONE_SIZE = 10.0  # Зона розміром 10x10 метрів
SENSOR_THRESHOLD_DISTANCE = 0.5  # Мінімальна відстань для виявлення об'єкта
MAX_ITERATIONS = 9

# Глобальний список для збереження сенсорів та даних
sensor_handles = []
all_sensor_data = []

@app.route('/start', methods=['GET'])
def start_simulation():
    try:
        client = RemoteAPIClient()
        sim = client.require('sim')

        sim.loadScene('')  # Порожня сцена

        # Створюємо стіни
        create_walls(sim)

        # Створюємо куби як перешкоди
        create_obstacles(sim)

        sim.startSimulation()

        for iteration in range(MAX_ITERATIONS):
            # Видаляємо попередні сенсори
            remove_previous_sensors(sim)

            # Створюємо сенсори
            num_sensors = 3 + (iteration % 4)  # Кількість сенсорів від 3 до 6
            create_sensors(sim, num_sensors)

            # Збираємо дані сканування
            sensor_data = scan_environment(sim)
            all_sensor_data.append(sensor_data)

            time.sleep(3)  # Затримка між ітераціями

        sim.stopSimulation()

        ##########################################
       
        return jsonify({"status": "Scan complete", "sensor_data": all_sensor_data}), 200

    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500


def create_walls(sim):
    wall_thickness = 0.1
    wall_height = 1.0

    left_wall = sim.createPureShape(0, 16, [wall_thickness, ZONE_SIZE, wall_height], 0.0)
    sim.setObjectPosition(left_wall, -1, [-ZONE_SIZE / 2, 0, wall_height / 2])

    right_wall = sim.createPureShape(0, 16, [wall_thickness, ZONE_SIZE, wall_height], 0.0)
    sim.setObjectPosition(right_wall, -1, [ZONE_SIZE / 2, 0, wall_height / 2])

    front_wall = sim.createPureShape(0, 16, [ZONE_SIZE, wall_thickness, wall_height], 0.0)
    sim.setObjectPosition(front_wall, -1, [0, ZONE_SIZE / 2, wall_height / 2])

    back_wall = sim.createPureShape(0, 16, [ZONE_SIZE, wall_thickness, wall_height], 0.0)
    sim.setObjectPosition(back_wall, -1, [0, -ZONE_SIZE / 2, wall_height / 2])


def create_obstacles(sim):
    obstacle_positions = [
        [1.0, 1.0, 0.2],
        [-1.0, 1.0, 0.2],
        [1.0, -1.0, 0.2],
        [-1.0, -1.0, 0.2],
        [0.4, 0.3, 0.2]
    ]

    for pos in obstacle_positions:
        cube = sim.createPureShape(0, 16, [0.5, 0.5, 0.5], 0.0)
        sim.setObjectPosition(cube, -1, pos)


def create_sensors(sim, num_sensors):
    global sensor_handles
    angle_step = 2 * math.pi / num_sensors  # Крок кута між сенсорами
    sensor_position = [0, 0, 0.1]  # Всі сенсори в одній точці
    for i in range(num_sensors):
        sensor_type = sim.proximitysensor_ray_subtype  # Type of sensor
        int_params = [32, 32, 0, 0, 0, 0, 0, 0]  # Sensor parameters
        float_params = [0, 20, 0, 0, 0, 0, 0, 1, 1, math.pi / 2, 0, 0, 0.1, 0, 0]  # Range and FOV parameters
        # Create the proximity sensor
        sensor_handle = sim.createProximitySensor(sensor_type, 16, 0, int_params, float_params)
        # Set the sensor's position (all sensors in the same position)
        sim.setObjectPosition(sensor_handle, sensor_position)
        # Rotate the sensor around the global Z-axis
        print( sim.handle_world)
        sim.setObjectOrientation(sensor_handle, [math.pi / 2, i * angle_step, 0])
        # Store the sensor handle
        sensor_handles.append(sensor_handle)





def remove_previous_sensors(sim):
    global sensor_handles
    for sensor in sensor_handles:
        try:
            sim.removeObject(sensor)
        except:
            print(sensor)
    sensor_handles = []



def scan_environment(sim):
    sensor_data = []

    for sensor_handle in sensor_handles:
        result, distance_data, *_ = sim.readProximitySensor(sensor_handle)
        if result > 0:
            sensor_data.append(distance_data)
        else:
            sensor_data.append(None)

    return sensor_data


if __name__ == '__main__':
    app.run(debug=True)
