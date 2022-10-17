import requests
import json

robot_ip = "192.168.100.2"
token = 'RGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA=='

headers = {
    'Accept-Language': 'en-US',
    'Accept': 'application/json',
    'Authorization': 'Basic {}'.format(token),
}

def resp_code_successful(code: int):
    return code >= 200 and code < 300


def get_robot_status():
    result = dict()
    result_code = -1
    url = "http://" + robot_ip + "/api/v2.0.0/status"
    try:
        response = requests.get(url, headers=headers, timeout=1)
        result = json.loads(response.text)
        result_code = response.status_code
    except Exception as e:
        print(e)
    return result, result_code


# move a robot to a position
def move(dst_x: float, dst_y: float):
    url = "http://" + robot_ip + "/api/v2.0.0/mission_queue"
    # The mission id is fixed when we move the robot.
    # Robots have two versions, they need different mission_id, in "move_parameters" and "move_parameters_headless", so when I need to move robots, I firstly try to use "move_parameters", if it does not work, I use "move_parameters_headless" to try again.
    move_parameters = {
        'mission_id':
        'db913046-0a06-11eb-8521-0001299f16e3',
        'parameters': [{
            'input_name': 'x',
            'value': dst_x
        }, {
            'input_name': 'y',
            'value': dst_y
        }],
        'message':
        '',
        'priority':
        1
    }
    move_parameters_headless = {
        'mission_id':
        '4b1df642-ac3d-11ec-a190-0001299f04e5',
        'parameters': [{
            'input_name': 'x',
            'value': dst_x
        }, {
            'input_name': 'y',
            'value': dst_y
        }],
        'message':
        '',
        'priority':
        1
    }
    try:
        # Firstly, use "move_parameters" to try.
        response = requests.post(url, headers=headers, json=move_parameters)
        if not resp_code_successful(response.status_code):
            print("response:[{}] {}, try headless request".format(
                response.status_code, response.text))
            # "move_parameters" does not work, try "move_parameters_headless"
            response = requests.post(url,
                                     headers=headers,
                                     json=move_parameters_headless)
    except Exception as e:
        print("Robot move error:", e)
    print("Robot move response code {}, response: {}".format(
        response.status_code, response.text))


def clear_mission_queue():
    url = "http://" + robot_ip + "/api/v2.0.0/mission_queue"
    try:
        response = requests.delete(url, headers=headers)
    except Exception as e:
        print("Robot {} clear_mission_queue error:".format(robot_ip), e)
    print("Robot {} clear_mission_queue response:".format(robot_ip), response)


def un_pause():
    url = "http://" + robot_ip + "/api/v2.0.0/status"
    un_pause_parameters = {'state_id': 3}
    try:
        response = requests.put(url, headers=headers, json=un_pause_parameters)
    except Exception as e:
        print("Robot unpause error:", e)
    print("Robot unpause response:", response)


# set desired speed of a robot (0.1-1.1 supported by the robot system, but it seems that the speed can only be up to about 8)
def set_desired_speed(speed: str):
    print("Set desired speed of Robot {} to {}:".format(robot_ip, speed))
    url = "http://" + robot_ip + "/api/v2.0.0/settings/2078"
    body = {'value': speed}
    try:
        response = requests.put(url, headers=headers, json=body)
    except Exception as e:
        print("Set desired speed of Robot {}:".format(robot_ip), e)
    print(
        "Set desired speed of Robot {}, status code: {}, response: {}".format(
            robot_ip, response.status_code, response.text))


# set maximum allowed speed of a robot (0.1-1.1 supported by the robot system)
def set_max_speed(speed: str):
    print("Set maximum allowed speed of Robot {} to {}:".format(
        robot_ip, speed))
    url = "http://" + robot_ip + "/api/v2.0.0/settings/2077"
    body = {'value': speed}
    try:
        response = requests.put(url, headers=headers, json=body)
    except Exception as e:
        print("Set maximum allowed speed of Robot {}:".format(robot_ip), e)
    print(
        "Set maximum allowed speed of Robot {}, status code: {}, response: {}".
        format(robot_ip, response.status_code, response.text))


if __name__ == "__main__":
    print("---get_robot_status------------------")
    robot_status, status_code = get_robot_status()
    if not resp_code_successful(status_code):
        print("error status code: {}".format(status_code))
    print(robot_status)

    print("---Move the robot------------------")
    # To make sure the robot can be moved, we clear the existing mission firstly
    clear_mission_queue()
    move(42.5, 24)
    # To make sure the robot can be moved, we unpause the robot
    un_pause()

    # The robot system has two parameters: "max allowed speed" and "desired speed", it seems that the real speed is min("max allowed speed", "desired speed").
    # Based on this, In my program, I set the desired speed very high.
    # when a robot is close to an object, I reduce the "max allowed speed" (desired > max), so the real speed will decrease to the "max allowed speed";
    # when the robot is not close to any objects, I increase the "max allowed speed" (max > desired), so the real speed will become the "desired speed".
    print("---set_desired_speed to 0.1m/s ------------------")
    set_desired_speed(0.1)

    print("---set_max_speed to 0.1m/s ------------------")
    set_max_speed(0.1)


# hej og goddag fra Andreas