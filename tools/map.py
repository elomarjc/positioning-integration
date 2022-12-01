from PIL import Image, ImageTk
import tkinter

# open the image of the lab map
'''image_file = Image.open("images/Raw_smart_lab(6).png")
map_width = image_file.width  # pixel
map_height = image_file.height  # pixel

person_icon = Image.open(
    "images/person_icons_created_by_Trazobanana_from_www.flaticon.com.png")
uwbtag_icon = Image.open(
    "images/tag_created_by_Pixel_perfect_www.flaticon.com.png")
robot_icon = Image.open(
    "images/robot_created_by_Good_Ware_from_www.flaticon.com.png")
position_icon = Image.open(
    "images/position_created_by_Pause08_www.flaticon.com.png")
letter_a_icon = Image.open(
    "images/Letter_A_by_Hight_Quality_Icons_www.flaticon.com.png")
letter_b_icon = Image.open(
    "images/Letter_B_by_Hight_Quality_Icons_www.flaticon.com.png")

icon_width = 20
icon_height = 20

new_person_icon = person_icon.resize((icon_width, icon_height),
                                     Image.Resampling.LANCZOS)
new_uwbtag_icon = uwbtag_icon.resize((icon_width, icon_height),
                                     Image.Resampling.LANCZOS)
new_robot_icon = robot_icon.resize((icon_width, icon_height),
                                   Image.Resampling.LANCZOS)
new_position_icon = position_icon.resize((icon_width, icon_height),
                                         Image.Resampling.LANCZOS)
new_letter_a_icon = letter_a_icon.resize((icon_width, icon_height),
                                         Image.Resampling.LANCZOS)
new_letter_b_icon = letter_b_icon.resize((icon_width, icon_height),
                                         Image.Resampling.LANCZOS)

# This module is for map positioning
# Our positioning systems only work on the right part of Smart Lab,
# so we cut the map and only show the right part of the map
# left top of the cut map is (678,19)
# right bottom of the cut map is (1004,865)
# cut_map_width = 1004 - 678 = 326
# cut_map_height = 865 - 19 = 846
top_cut = 19
left_cut = 678
right_cut = map_width - 100
bottom_cut = map_height - 865
cut_map_width = map_width - right_cut - left_cut
cut_map_height = map_height - bottom_cut - top_cut

# The systems of CV, UWB, and Robot may have bias, so when we receive the data we should calibrate them.
# We cannot put a Robot and a Person at a same position, and we can only make a Person carry a UWBtag, or make a Robot carry a UWBtag.
# Therefore, we should calibrage CV and Robot positions based on the UWB positions.

# Explanation------------------------
# from (1)our test; and (2)Allan's code: pozyx-positioning\plot_tags_in_lab_v2.py
# the original offset values are:
# cv_x_offset = 860
# cv_y_offset = 435
# uwb_x_offset = 860
# uwb_y_offset = 435
# robot_x_offset = 5
# robot_y_offset = 52
# We used these values to convert the input positions to the coordinates on the map.
# Now we are changing our policy, and we will only use the offset of UWB, and we will convert the CV positions and Robot positions to UWB positions before the conversion using the offset values.
# uwbx+uwbxoffset = robotx+robotxoffset
# uwbx = robotx + robotxoffset - uwbxoffset
# So, robot2uwb_x = robot_x_offset - uwb_x_offset = -855 pixel'''
# ---------------------------------

# unit pixel
uwb_x_offset = 860
uwb_y_offset = 435

# For calibration, we convert the CV and Robot positions to UWB positions, and then do other operations
# Use the unit of UWB: milimeter
cv2uwb_x = 0 + (-385.277) + (40.053) + (68.452)
cv2uwb_y = 0 + (-774.309) + (423.999) + (-25.196)
robot2uwb_x = -855 * 5 * 10 + 147.116 + (-22.013
                                         )  # 855 is pixel, *5*10 to milimeter
robot2uwb_y = -383 * 5 * 10 + 32.335 + (-1.077
                                        )  # 383 is pixel, *5*10 to milimeter


# calibrate cv input based on uwb
def calibrate_input_cv2uwb(x: float, y: float):
    return x + cv2uwb_x, y + cv2uwb_y


def reverse_calibrate_input_cv2uwb(uwb_x: float, uwb_y: float):
    return uwb_x - cv2uwb_x, uwb_y - cv2uwb_y


# calibrate Robot input based on uwb
def calibrate_input_robot2uwb(x: float, y: float):
    x_milimeter = x * 1000
    y_milimeter = y * 1000
    return x_milimeter + robot2uwb_x, y_milimeter + robot2uwb_y


def reverse_calibrate_input_robot2uwb(x: float, y: float):
    original_x_milimeter = x - robot2uwb_x
    original_y_milimeter = y - robot2uwb_y
    original_x = original_x_milimeter / 1000
    original_y = original_y_milimeter / 1000
    return original_x, original_y


# to convert the (x,y) positions in UWB system into the (x,y) positions on the map. This should be the same with convert_cv.
def convert_tags(x: float, y: float, proportion: float):
    # the scaling rates and offsets are from Allan's code: pozyx-positioning\plot_tags_in_lab_v2.py
    # x is mm, x/10 is cm, so 5cm is one pixel
    converted_x = (float(x) / 10 / 5 + uwb_x_offset - left_cut) * proportion
    converted_y = (map_height -
                   (float(y) / 10 / 5 + uwb_y_offset - top_cut)) * proportion
    return converted_x, converted_y


# to convert the (x,y) positions in CV system into the (x,y) positions on the map.
def convert_cv(x: float, y: float, proportion: float):
    x_uwb, y_uwb = calibrate_input_cv2uwb(x, y)
    return convert_tags(x_uwb, y_uwb, proportion)


# to convert the (x,y) positions in Robot system into the (x,y) positions on the map.
def convert_robot(x: float, y: float, proportion: float):
    x_uwb, y_uwb = calibrate_input_robot2uwb(x, y)
    return convert_tags(x_uwb, y_uwb, proportion)


# unify the positions to show them on the map and to store them into influxdb.
# the input of uwb unit is milimeter, we convert it to meter
def convert_uwb_position_for_unification(x: float, y: float):
    x_meter = x / 1000
    y_meter = y / 1000
    # only accurate to 3 decimal places, to save the storage
    x_meter = float("{:.3f}".format(x_meter))
    y_meter = float("{:.3f}".format(y_meter))
    return x_meter, y_meter


def reverse_convert_uwb_position_for_unification(x: float, y: float):
    return x * 1000, y * 1000


# the input of cv unit is milimeter, we convert it to meter
def convert_cv_position_for_unification(x: float, y: float):
    x_uwb, y_uwb = calibrate_input_cv2uwb(x, y)
    return convert_uwb_position_for_unification(x_uwb, y_uwb)


def reverse_convert_cv_position_for_unification(x: float, y: float):
    x_uwb, y_uwb = reverse_convert_uwb_position_for_unification(x, y)
    x_cv, y_cv = reverse_calibrate_input_cv2uwb(x_uwb, y_uwb)
    return x_cv, y_cv


# the input of robot unit is meter
def convert_robot_position_for_unification(x: float, y: float):
    x_uwb, y_uwb = calibrate_input_robot2uwb(x, y)
    return convert_uwb_position_for_unification(x_uwb, y_uwb)


def reverse_convert_robot_position_for_unification(x: float, y: float):
    x_uwb, y_uwb = reverse_convert_uwb_position_for_unification(x, y)
    x_robot, y_robot = reverse_calibrate_input_robot2uwb(x_uwb, y_uwb)
    return x_robot, y_robot


# show a position on the map
def show_position(canvas_map,
                  proportion,
                  x,
                  y,
                  canvas_tag,
                  color,
                  text_head,
                  convert_func,
                  convert_for_unification_func,
                  text_offset_x=0.0,
                  text_offset_y=-20.0):
    # match the (x,y) to the map
    converted_x, converted_y = convert_func(float(x), float(y), proportion)
    unified_x, unified_y = convert_for_unification_func(float(x), float(y))

    # draw this point
    x1 = converted_x - 5
    y1 = converted_y - 5
    x2 = converted_x + 5
    y2 = converted_y + 5
    # a function to draw a oval dot on the map
    canvas_map.create_oval(x1,
                           y1,
                           x2,
                           y2,
                           outline="{}".format(color),
                           fill="{}".format(color),
                           tag=canvas_tag)
    canvas_map.create_text(converted_x + text_offset_x,
                           converted_y + text_offset_y,
                           text=text_head +
                           "\n({:.2f},{:.2f})".format(unified_x, unified_y),
                           tag=canvas_tag)


# show a position on the map using a icon
def show_position_icon(canvas_map,
                       proportion,
                       x,
                       y,
                       canvas_tag,
                       icon: ImageTk.PhotoImage,
                       text_head,
                       convert_func,
                       convert_for_unification_func,
                       text_offset_x=0.0,
                       text_offset_y=-22.5,
                       print_text=True):
    # match the (x,y) to the map
    converted_x, converted_y = convert_func(float(x), float(y), proportion)
    unified_x, unified_y = convert_for_unification_func(float(x), float(y))

    # put the icon on the map
    canvas_map.create_image(converted_x,
                            converted_y,
                            image=icon,
                            anchor=tkinter.CENTER,
                            tag=canvas_tag)
    if not print_text:
        return
    canvas_map.create_text(converted_x + text_offset_x,
                           converted_y + text_offset_y,
                           text=text_head +
                           "\n({:.2f},{:.2f})".format(unified_x, unified_y),
                           tag=canvas_tag)
