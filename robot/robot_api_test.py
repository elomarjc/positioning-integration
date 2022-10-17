import robot_api


def test_get_robots():
    robots = robot_api.get_robots()
    for robot in robots:
        print(robot["id"], robot)
        info = robot_api.get_robot_info(str(robot["id"]))
        if info["fleet_state"] != 1:
            print(robot["id"], "is not unavailable")


if __name__ == "__main__":
    test_get_robots()