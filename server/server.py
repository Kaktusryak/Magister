from flask import Flask, request, jsonify
import random
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import threading
from roboflow import Roboflow
from queue import Queue
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

ZONE_SIZE = 10.0  # Зона розміром 10x10 метрів
SENSOR_THRESHOLD_DISTANCE = 0.5  # Мінімальна відстань для виявлення об'єкта
MAX_ITERATIONS = 9

# Глобальний список для збереження сенсорів та даних
sensor_handles = []
all_sensor_data = []


@app.route('/start_mapping', methods=['POST'])
async def start_mapping():
    try:
        client = RemoteAPIClient()
        sim = client.require('sim')

        sim.loadScene('C:/Users/denis/Desktop/Diploma/Magister/scene/SLAM.ttt')

        position_queue = Queue()

        request_data = request.get_json()
        print(request_data)

        dencity = request_data['dencity']
        workingTime = request_data['time']
        create_obstacles(sim, dencity)

        sim.startSimulation()

        camera_handle = sim.getObjectHandle('Vision_sensor')
        robot_handle = sim.getObjectHandle('Pioneer_p3dx')
        print(camera_handle)
        print(robot_handle)

        # Start a new thread for saving images
        image_saving_thread = threading.Thread(
            target=save_images, 
            args=(
                sim, 
                camera_handle, 
                robot_handle, 
                workingTime, 
                position_queue
                )
                )
        image_saving_thread.start()

        time.sleep(workingTime)

        sim.stopSimulation()
        time.sleep(1)
        predictions = await objectDetection(workingTime)
        # return jsonify({ "status": "Scan complete", "data": measuredData }), 200
        return jsonify({ "status": "Scan complete", "predictions": predictions, "positions": position_queue.get() }), 200
    except Exception as e:
        return jsonify({ "status": "Error", "message": str(e) }), 500
    

@app.route('/get_images', methods=['GET'])
def list_images():
    images = [f"prediction_imageTest{i}.png" for i in range(1, 31)]
    return jsonify(images)


async def objectDetection(times):
    rf = Roboflow(api_key="AxJQTHdmCRqWytYDXxOs")
    project = rf.workspace().project("environment_cubes")
    model = project.version(1).model
    results = []
    for i in range(1, times + 1):
            print(f'image {i}')
            model.predict(f'C:/Users/denis/Desktop/Diploma/Magister/images/imageTest{i}.png', confidence=40, overlap=30).save(f'C:/Users/denis/Desktop/Diploma/Magister/diploma/public/assets/images/prediction_imageTest{i}.png')
            result = model.predict(f'C:/Users/denis/Desktop/Diploma/Magister/images/imageTest{i}.png', confidence=40, overlap=30).json()
            results.append(result)

    print('OD')
    return results


def save_images(sim, camera_handle, robot_handle, times, position_queue):
    positions = []
    i = 0
    while i < times:
        try:
            i = i + 1

            position = sim.getObjectPosition(robot_handle)
            positions.append(position)

            imageBuffer, resolutionX, resolutionY = sim.getVisionSensorCharImage(camera_handle)
            sim.saveImage(imageBuffer, [resolutionX, resolutionY], 0, f'C:/Users/denis/Desktop/Diploma/Magister/diploma/public/assets/images/imageTest{i}.png', 100)
            
            position_queue.put(positions)
            time.sleep(1)  # Wait for 1 second before capturing the next image
        except Exception as e:
            print(e)
    return positions


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


if __name__ == '__main__':
    app.run(debug=True)
