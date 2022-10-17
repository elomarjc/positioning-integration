import requests  # python lib to send http requests
import json  # python lib to parse json

# http://192.168.100.123/help/api-documentation
# In the fleet-manager web, help --> api-documentation, we can find the API Documentation of the fleet-manager

manager_ip = "192.168.100.123"
mir_robot_fleet_manager_gateway_url = "http://" + manager_ip + "/api/v2.0.0/"
token = 'RGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA=='

headers = {
    'Accept-Language': 'en-US',
    'Accept': 'application/json',
    'Authorization': 'Basic {}'.format(token),
}


# check whether the resp code is successful
def resp_code_successful(code: int):
    return code >= 200 and code < 300


# use API to get all robots
def get_robots():
    result = dict()
    try:
        response = requests.get(mir_robot_fleet_manager_gateway_url +
                                "robots/",
                                headers=headers).text
        result = json.loads(response)
    except Exception as e:
        print(e)
    return result


# use API to get robot information
def get_robot_info(id: str):
    result = dict()
    try:
        response = requests.get(mir_robot_fleet_manager_gateway_url +
                                "robots/" + id,
                                headers=headers,
                                timeout=1).text
        result = json.loads(response)
    except Exception as e:
        print(e)
    return result


# directly use Robot API instead of fleet-manager API to get Robot status
def robot_status_direct(robot_ip: str):
    result = dict()
    url = "http://" + robot_ip + "/api/v2.0.0/status"
    try:
        response = requests.get(url, headers=headers, timeout=1).text
        result = json.loads(response)
    except Exception as e:
        print(e)
    return result


# get Robot status and HTTP code
def robot_status_with_code(robot_ip: str):
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
def move(robot_ip: str, dst_x: float, dst_y: float):
    url = "http://" + robot_ip + "/api/v2.0.0/mission_queue"
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
        response = requests.post(url, headers=headers, json=move_parameters)
        if not resp_code_successful(response.status_code):
            print("response:[{}] {}, try headless request".format(
                response.status_code, response.text))
            response = requests.post(url,
                                     headers=headers,
                                     json=move_parameters_headless)
    except Exception as e:
        print("Robot move error:", e)
    print("Robot move response code {}, response: {}".format(
        response.status_code, response.text))


# set desired speed of a robot (0.1-1.1 supported by the robot system, but it seems that the speed can only be up to about 8)
def set_desired_speed(robot_ip: str, speed: str):
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
def set_max_speed(robot_ip: str, speed: str):
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


# change the robot state from pause to unpause
def un_pause(robot_ip: str):
    url = "http://" + robot_ip + "/api/v2.0.0/status"
    un_pause_parameters = {'state_id': 3}
    try:
        response = requests.put(url, headers=headers, json=un_pause_parameters)
    except Exception as e:
        print("Robot unpause error:", e)
    print("Robot unpause response:", response)


# if there are errors, clear them
def clear_errors(robot_ip: str):
    status = robot_status_direct(robot_ip)
    print("Robot status:\n{}".format(status))
    if 'errors' not in status:
        print("clear_errors {}, No errors.".format(robot_ip))
        return
    robot_errors = status['errors']
    if ("obstacle" not in str(robot_errors)) and ("Failed"
                                                  not in str(robot_errors)):
        print("clear_errors {}, No obstacle or Failed.".format(robot_ip))
        return
    # errors exist, clear them
    url = "http://" + robot_ip + "/api/v2.0.0/status"
    un_pause_parameters = {'clear_error': True}
    try:
        response = requests.put(url, headers=headers, json=un_pause_parameters)
    except Exception as e:
        print("Robot clear errors error:", e)
    print("Robot clear errors response:", response)


# Abort all the pending and executing missions from the mission queue
def clear_mission_queue(robot_ip: str):
    url = "http://" + robot_ip + "/api/v2.0.0/mission_queue"
    try:
        response = requests.delete(url, headers=headers)
    except Exception as e:
        print("Robot {} clear_mission_queue error:".format(robot_ip), e)
    print("Robot {} clear_mission_queue response:".format(robot_ip), response)
