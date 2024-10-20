from flask import Flask, request, jsonify
import random
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import threading

app = Flask(__name__)

ZONE_SIZE = 10.0  # Зона розміром 10x10 метрів
SENSOR_THRESHOLD_DISTANCE = 0.5  # Мінімальна відстань для виявлення об'єкта
MAX_ITERATIONS = 9

# Глобальний список для збереження сенсорів та даних
sensor_handles = []
all_sensor_data = []


@app.route('/start_mapping', methods=['POST'])
def start_mapping():
    try:
        client = RemoteAPIClient()
        sim = client.require('sim')

        sim.loadScene('C:/Users/denis/Desktop/Diploma/scene/SLAM.ttt')

        request_data = request.get_json()
        print(request_data)

        dencity = request_data['dencity']
        create_obstacles(sim, dencity)

        sim.startSimulation()

        camera_handle = sim.getObjectHandle('Vision_sensor')
        print(camera_handle)

        # Start a new thread for saving images
        image_saving_thread = threading.Thread(target=save_images, args=(sim, camera_handle, 30))
        image_saving_thread.start()

        time.sleep(30)

        

        # data=sim.getStringSignal("measuredDataAtThisTime")
        # print(data)
        # measuredData=sim.unpackFloatTable(data)

        sim.stopSimulation()
        # return jsonify({ "status": "Scan complete", "data": measuredData }), 200
        return jsonify({ "status": "Scan complete" }), 200
    except Exception as e:
        return jsonify({ "status": "Error", "message": str(e) }), 500

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


def save_images(sim, camera_handle, times):
    i = 0
    while i < times:
        try:
            i = i + 1
            imageBuffer, resolutionX, resolutionY = sim.getVisionSensorCharImage(camera_handle)
            sim.saveImage(imageBuffer, [resolutionX, resolutionY], 0, f'C:/Users/denis/Desktop/Diploma/images/imageTest{i}.png', 100)
            time.sleep(1)  # Wait for 1 second before capturing the next image
        except Exception as e:
            print(e)

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


def create_obstacles(sim, dencity):

    colors = [
        [1, 0, 0],   # Red
        [0, 1, 0],   # Green
        [0, 0, 1],   # Blue
        [1, 1, 0],   # Yellow
        [0, 1, 1],   # Cyan
        [1, 0, 1],   # Magenta
        [1, 0.5, 0], # Orange
        [0.5, 0, 0.5] # Purple
    ]

    obstacle_positions = [
        [1.0, 1.0, 0.2],
        [-1.0, 1.0, 0.2],
        [1.0, -1.0, 0.2],
        [-1.0, -1.0, 0.2],
        [0.4, 0.3, 0.2],
    ]

    

    if (dencity == 1):
        obstacle_positions = [
            [1.0, 1.0, 0.2],  # Перешкода в межах 1 метра від початкової позиції
            [-1.0, 1.0, 0.2],  # Перешкода в межах 1 метра
            [1.0, -1.0, 0.2],  # Перешкода в межах 1 метра
            [-1.0, -1.0, 0.2],  # Перешкода в межах 1 метра
            [0.4, 0.3, 0.2],  # Перешкода ближче до центру
            # Додаємо нові перешкоди для сцени 15x15:
            [5.0, 5.0, 0.2],  # Перешкода в правому верхньому куті
            [-5.0, 5.0, 0.2],  # Перешкода в лівому верхньому куті
            [5.0, -5.0, 0.2],  # Перешкода в правому нижньому куті
            [-5.0, -5.0, 0.2],  # Перешкода в лівому нижньому куті
            [3.0, 3.0, 0.2],  # Перешкода трохи далі від центру
            [-3.0, -3.0, 0.2],  # Перешкода на протилежній стороні
            [4.5, -4.5, 0.2],  # Перешкода ближче до краю сцени
            [-4.5, 0.5, 0.2],  # Перешкода біля протилежного краю[3.0, 3.0, 0.2],  # Перешкода трохи далі від центру
            [-3.0, 0.0, 0.2],  # Перешкода на протилежній стороні
            [4.5, 1.5, 0.2],  # Перешкода ближче до краю сцени
            [-4.5, 0.5, 0.2],  # Перешкода біля протилежного краю
        ]
    elif (dencity == 2):
        obstacle_positions = [
            [1.0, 1.0, 0.2],  # Перешкода в межах 1 метра від початкової позиції
            [-1.0, 1.0, 0.2],  # Перешкода в межах 1 метра
            [1.0, -1.0, 0.2],  # Перешкода в межах 1 метра
            [-1.0, -1.0, 0.2],  # Перешкода в межах 1 метра
            [0.4, 0.3, 0.2],  # Перешкода ближче до центру
            [5.0, 5.0, 0.2],  # Перешкода в правому верхньому куті
            [-5.0, 5.0, 0.2],  # Перешкода в лівому верхньому куті
            [5.0, -5.0, 0.2],  # Перешкода в правому нижньому куті
            [-5.0, -5.0, 0.2],  # Перешкода в лівому нижньому куті
            [3.0, 3.0, 0.2],  # Перешкода трохи далі від центру
            [-3.0, -3.0, 0.2],  # Перешкода на протилежній стороні
            [4.5, -4.5, 0.2],  # Перешкода ближче до краю сцени
            [-5, 0.5, 0.2],  # Перешкода біля протилежного краю
            [-5.0, 0.0, 0.2],  # Перешкода на протилежній стороні
            [4.5, 1.5, 0.2],  # Перешкода ближче до краю сцени
            [-5.5, 0.5, 0.2],  # Перешкода біля протилежного краю
            # Додаткові перешкоди
            [2.0, 2.0, 0.2],  # Додаткова перешкода в центрі
            [-2.0, 2.0, 0.2],  # Додаткова перешкода
            [2.0, -2.0, 0.2],  # Додаткова перешкода
            [-2.0, -2.0, 0.2],  # Додаткова перешкода
            [6.0, 6.0, 0.2],  # Додаткова перешкода в правому верхньому куті
            [-6.0, 6.0, 0.2],  # Додаткова перешкода в лівому верхньому куті
            [6.0, -6.0, 0.2],  # Додаткова перешкода в правому нижньому куті
            [-6.0, -6.0, 0.2],  # Додаткова перешкода в лівому нижньому куті
            [3.5, 3.5, 0.2],  # Додаткова перешкода трохи далі від центру
            [-3.5, -3.5, 0.2],  # Додаткова перешкода на протилежній стороні
        ]
    elif (dencity == 3):
        obstacle_positions = [
            [1.0, 1.0, 0.2],  # Перешкода в межах 1 метра від початкової позиції
            [-1.0, 1.0, 0.2],  # Перешкода в межах 1 метра
            [1.0, -1.0, 0.2],  # Перешкода в межах 1 метра
            [-1.0, -1.0, 0.2],  # Перешкода в межах 1 метра
            [0.4, 0.3, 0.2],  # Перешкода ближче до центру
            [5.0, 5.0, 0.2],  # Перешкода в правому верхньому куті
            [-5.0, 5.0, 0.2],  # Перешкода в лівому верхньому куті
            [5.0, -5.0, 0.2],  # Перешкода в правому нижньому куті
            [-5.0, -5.0, 0.2],  # Перешкода в лівому нижньому куті
            [3.0, 3.0, 0.2],  # Перешкода трохи далі від центру
            [-3.0, -3.0, 0.2],  # Перешкода на протилежній стороні
            [4.5, -4.5, 0.2],  # Перешкода ближче до краю сцени
            [-5.5, 0.5, 0.2],  # Перешкода біля протилежного краю
            [-3.0, 0.0, 0.2],  # Перешкода на протилежній стороні
            [4.5, 1.5, 0.2],  # Перешкода ближче до краю сцени
            [-4.5, 3, 0.2],  # Перешкода біля протилежного краю
            # Додаткові перешкоди
            [2.0, 2.0, 0.2],  # Додаткова перешкода в центрі
            [-3.0, 3.0, 0.2],  # Додаткова перешкода
            [2.0, -2.0, 0.2],  # Додаткова перешкода
            [-2.0, -2.0, 0.2],  # Додаткова перешкода
            [4.0, 3.0, 0.2],  # Додаткова перешкода в правому верхньому куті
            [-2.0, 3.0, 0.2],  # Додаткова перешкода в лівому верхньому куті
            [4.0, -4.0, 0.2],  # Додаткова перешкода в правому нижньому куті
            [-4.5, -3.0, 0.2],  # Додаткова перешкода в лівому нижньому куті
            [3.5, 3.5, 0.2],  # Додаткова перешкода трохи далі від центру
            [-3.5, -3.5, 0.2],  # Додаткова перешкода на протилежній стороні
            [3.5, -3.5, 0.2],  # Додаткова перешкода ближче до краю сцени
            [-5.5, 0.5, 0.2],  # Додаткова перешкода біля протилежного краю
            [-3.5, 0.0, 0.2],  # Додаткова перешкода
            [2.5, 1.5, 0.2],  # Додаткова перешкода ближче до краю
            [-5.5, 1.0, 0.2],  # Додаткова перешкода біля протилежного краю
            # Нові перешкоди на серединах сторін
            [0.0, 5.5, 0.2],  # Перешкода посередині верхньої сторони
            [0.0, -4.5, 0.2],  # Перешкода посередині нижньої сторони
            [4.5, 0.0, 0.2],  # Перешкода посередині правої сторони
            [-3.5, 0.0, 0.2],  # Перешкода посередині лівої сторони
            [3.0, 3.5, 0.2],  # Додаткова перешкода ближче до центру верхньої сторони
            [-1.0, -4.5, 0.2],  # Додаткова перешкода ближче до центру нижньої сторони
            [1.5, 3.0, 0.2],  # Додаткова перешкода ближче до правої сторони
            [-5.5, -3.0, 0.2],  # Додаткова перешкода ближче до лівої сторони
        ]


    for pos in obstacle_positions:
        cube = sim.createPureShape(0, 16, [0.5, 0.5, 0.5], 0.0)
        sim.setObjectPosition(cube, -1, pos)
        random_color = random.choice(colors)  # Choose a random color from the list
        sim.setShapeColor(cube, None, sim.colorcomponent_ambient_diffuse, random_color)  # You can modify the index here based on your requirements


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
