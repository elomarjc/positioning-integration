from PIL import Image, ImageTk  # put a picture (lab map) in the window
import tkinter  # Python GUI tool, to open a window
import tkinter.font  # to change the font size of titles

import sys

from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

import tools.map
import tools.adjustable_text_size

# create a window, because this program needs to show the map
window = tkinter.Tk()
title = "Real-Time Location System (RTLS) for Digital Twin"
window.title(title)
window.geometry("{}x{}+1+1".format(1200, 750))
window.configure(background="white")

# colors
AAU_BLUE = '#211a52'
FRESH_LEAVES = '#99FF4D'
MARIGOLD = '#FF9900'
VERMILION = '#FF4D00'
ALICE_BLUE = '#F0F8FF'
PERIWINKLE = '#CCCCFF'
BABY_BLUE = '#E0FFFF'
RED = '#FF0000'

# The effect of the transparent color is bad, because it will make all layers of this window transparent rather than this single layer, namely, we can directly see another window below this one.
# TRANSPARENTCOLOR = '#F5F5F5'

# # set transparent color
# window.wm_attributes("-transparentcolor", TRANSPARENTCOLOR)

# fonts
map_title_font = tkinter.font.Font(family="Arial",
                                   size=18,
                                   weight=tkinter.font.NORMAL)
main_title_font = tkinter.font.Font(family="Arial",
                                    size=18,
                                    weight=tkinter.font.BOLD)
legend_font = tkinter.font.Font(family="Arial",
                                size=9,
                                weight=tkinter.font.BOLD)
button_font = tkinter.font.Font(family="Arial",
                                size=12,
                                weight=tkinter.font.BOLD)
text_font = tkinter.font.Font(family="Arial",
                              size=12,
                              weight=tkinter.font.BOLD)
text_font_big = tkinter.font.Font(family="Arial",
                                  size=13,
                                  weight=tkinter.font.BOLD)

# This module is for top Bar
frame_top = tkinter.Frame(window, bg=AAU_BLUE, width=700, height=83)
frame_top.pack()
frame_top.place(x=0, y=0)
top_bar_scale = 0.1

# This module is for creating title
title_font = tools.adjustable_text_size.adjustable_text(title, main_title_font)
label_title = tkinter.Label(frame_top,
                            text=title_font.text,
                            fg='white',
                            bg=AAU_BLUE,
                            font=title_font.text_font)
label_title.pack()
label_title.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

# This module is to create AAU logo
aau_logo_image = Image.open("images/AAU_UK_CIRCLE_white_rgb.png")
aau_logo_image_width = aau_logo_image.width  # pixel
aau_logo_image_height = aau_logo_image.height  # pixel
aau_logo_photo = ImageTk.PhotoImage(aau_logo_image)
label_aau_logo = tkinter.Label(frame_top, bg=AAU_BLUE, image=aau_logo_photo)
label_aau_logo.pack()
label_aau_logo.place(x=0, y=0)

# This module is to create AAU Smart Lab logo
smart_lab_logo_image = Image.open("images/AAU5GSmartProduction_logo_white.png")
smart_lab_logo_image_width = smart_lab_logo_image.width
smart_lab_logo_image_height = smart_lab_logo_image.height
smart_lab_logo_photo = ImageTk.PhotoImage(smart_lab_logo_image)
label_smart_lab_logo = tkinter.Label(frame_top,
                                     bg=AAU_BLUE,
                                     image=smart_lab_logo_photo)
label_smart_lab_logo.pack()
label_smart_lab_logo.place(x=0, y=0)

# This module is for control panel
control_panel = tkinter.Frame(window, bg=FRESH_LEAVES, width=700, height=83)
control_panel.pack()
control_panel.place(x=0, y=0)
control_panel_scale = 0.3

# This module is for right control panel
right_control_panel = tkinter.Frame(window,
                                    bg=ALICE_BLUE,
                                    width=700,
                                    height=83)
right_control_panel.pack()
right_control_panel.place(x=0, y=0)
right_control_panel_scale = 0.3

map_area_w_scale = 1.0 - control_panel_scale - right_control_panel_scale


# create legends on canvas_map
def create_legends(canvas_map: tkinter.Canvas):
    canvas_width = max([int(proportion * tools.map.cut_map_width), 1])
    # print the legends
    legend_position = [canvas_width / 2, 20]
    canvas_map.delete("legend")
    # legend for UWB
    legend_uwb = canvas_map.create_text(legend_position[0],
                                        legend_position[1],
                                        text="UWB: blue dot",
                                        fill="blue",
                                        font=legend_font,
                                        tag="legend")
    legend_uwb_bg = canvas_map.create_rectangle(canvas_map.bbox(legend_uwb),
                                                fill="white",
                                                outline="white",
                                                tag="legend")
    canvas_map.tag_lower(legend_uwb_bg, legend_uwb)

    # legend for CV
    legend_cv = canvas_map.create_text(legend_position[0],
                                       legend_position[1] + 15,
                                       text="CV: red dot",
                                       fill="red",
                                       font=legend_font,
                                       tag="legend")
    legend_cv_bg = canvas_map.create_rectangle(canvas_map.bbox(legend_cv),
                                               fill="white",
                                               outline="white",
                                               tag="legend")
    canvas_map.tag_lower(legend_cv_bg, legend_cv)

    # legend for Robot
    legend_robot = canvas_map.create_text(legend_position[0],
                                          legend_position[1] + 30,
                                          text="Robot: green dot",
                                          fill="green",
                                          font=legend_font,
                                          tag="legend")
    legend_robot_bg = canvas_map.create_rectangle(
        canvas_map.bbox(legend_robot),
        fill="white",
        outline="white",
        tag="legend")
    canvas_map.tag_lower(legend_robot_bg, legend_robot)

    # legend for Unit
    explain_unit(canvas_map,
                 legend_position[0],
                 legend_position[1] + 45,
                 color="black")


# create legend for unit on canvas_map
def create_unit_legend(canvas_map: tkinter.Canvas):
    canvas_width = max([int(proportion * tools.map.cut_map_width), 1])
    # print the legends
    legend_position = [canvas_width / 2, 20]
    canvas_map.delete("legend")
    # legend for Unit
    explain_unit(canvas_map, legend_position[0], legend_position[1])


# explain the unit on canvas_map
def explain_unit(canvas_map: tkinter.Canvas, x: int, y: int, color="blue"):
    # legend for unit
    legend_unit = canvas_map.create_text(x,
                                         y,
                                         text="Unit of coordinates: meter",
                                         fill=color,
                                         font=legend_font,
                                         tag="legend")
    legend_unit_bg = canvas_map.create_rectangle(canvas_map.bbox(legend_unit),
                                                 fill="white",
                                                 outline="white",
                                                 tag="legend")
    canvas_map.tag_lower(legend_unit_bg, legend_unit)


# When users make the window larger or smaller, the canvas and map should be resized automatically. This proportion is for resize.
proportion = 1.0

# This module is for creating titles for maps
# put all map titles into a list, then we can get the number of maps easily
map_titles = []
# Lab map title
lab_map_title_font = tools.adjustable_text_size.adjustable_text(
    "Lab Map", map_title_font)
label_lab_map_title = tkinter.Label(window,
                                    text=lab_map_title_font.text,
                                    fg='black',
                                    bg="white",
                                    font=lab_map_title_font.text_font)
label_lab_map_title.pack()
map_titles.append(label_lab_map_title)
lab_map_title_scale = 0.05

# put all canvases into a list, then we can get the number of canvas easily
canvases = []
# create a canvases of map, to show cv, uwb, and robot positions
canvas_map = tkinter.Canvas(window,
                            width=tools.map.cut_map_width,
                            height=tools.map.cut_map_height,
                            bg='white')
canvas_map.pack()
canvases.append(canvas_map)

photo = ImageTk.PhotoImage(tools.map.image_file)

# resize base window
# record current window size
last_window_width = -1
last_window_height = -1


def resize_basewindow():
    window.update()
    global last_window_width, last_window_height
    # get the current size of the window
    current_window_width = window.winfo_width()
    current_window_height = window.winfo_height()
    # Only when the widow size changes, we execute the resize behaviors
    if not (current_window_width == last_window_width
            and current_window_height == last_window_height):
        last_window_width = current_window_width
        last_window_height = current_window_height

        window_w = float(current_window_width)
        window_h = float(current_window_height)

        # resize the top bar
        bar_h = window_h * top_bar_scale
        frame_top.config(width=window_w, height=bar_h)

        # calculate the size and resize the AAU logo
        aau_logo_margin = 5.0
        aau_logo_proportion = min([
            (window_w - aau_logo_margin) / float(aau_logo_image_width),
            (bar_h - aau_logo_margin) / float(aau_logo_image_height)
        ])
        aau_logo_width = max(
            [int(aau_logo_proportion * aau_logo_image_width), 1])
        aau_logo_height = max(
            [int(aau_logo_proportion * aau_logo_image_height), 1])
        new_aau_log_image = aau_logo_image.resize(
            (aau_logo_width, aau_logo_height), Image.Resampling.LANCZOS)
        # Fix bug, the aau_logo_photo must be a global variable, otherwise, after the resize_basewindow finishes, the aau_logo_photo variable will be deleted. If the aau_logo_photo variable is deleted, the picture cannot be shown on the window.
        global aau_logo_photo
        aau_logo_photo = ImageTk.PhotoImage(new_aau_log_image)
        label_aau_logo.configure(image=aau_logo_photo)
        aau_logo_relx = (aau_logo_width + aau_logo_margin) * 0.5 / window_w
        label_aau_logo.place(relx=aau_logo_relx,
                             rely=0.5,
                             anchor=tkinter.CENTER)

        # calculate the size and resize the Smart Lab logo
        smart_lab_logo_margin = 5.0
        smart_lab_logo_proportion = min([(window_w - smart_lab_logo_margin) /
                                         float(smart_lab_logo_image_width),
                                         (bar_h - smart_lab_logo_margin) /
                                         float(smart_lab_logo_image_height)])
        smart_lab_logo_width = max(
            [int(smart_lab_logo_proportion * smart_lab_logo_image_width), 1])
        smart_lab_logo_height = max(
            [int(smart_lab_logo_proportion * smart_lab_logo_image_height), 1])
        new_smart_lab_logo_image = smart_lab_logo_image.resize(
            (smart_lab_logo_width, smart_lab_logo_height),
            Image.Resampling.LANCZOS)
        # Fix bug, the smart_lab_logo_photo must be a global variable, otherwise, after the resize_basewindow finishes, the smart_lab_logo_photo variable will be deleted. If the smart_lab_logo_photo variable is deleted, the picture cannot be shown on the window.
        global smart_lab_logo_photo
        smart_lab_logo_photo = ImageTk.PhotoImage(new_smart_lab_logo_image)
        label_smart_lab_logo.configure(image=smart_lab_logo_photo)
        smart_lab_logo_relx = (
            window_w -
            (smart_lab_logo_margin + smart_lab_logo_width) * 0.5) / window_w
        label_smart_lab_logo.place(relx=smart_lab_logo_relx,
                                   rely=0.5,
                                   anchor=tkinter.CENTER)

        # calculate the size and resize the title
        top_bar_height_margin = 15.0
        top_bar_weight_margin = 30.0
        title_font.adjust_font(
            window_w - aau_logo_width - aau_logo_margin -
            smart_lab_logo_margin - smart_lab_logo_width -
            top_bar_weight_margin, bar_h - top_bar_height_margin)
        label_title.configure(font=title_font.text_font)
        title_relx = ((window_w - aau_logo_margin - aau_logo_width -
                       smart_lab_logo_margin - smart_lab_logo_width) * 0.5 +
                      aau_logo_margin + aau_logo_width) / window_w
        label_title.place(relx=title_relx, rely=0.5, anchor=tkinter.CENTER)

        # resize the control panel
        control_panel_w = window_w * control_panel_scale
        control_panel_h = window_h - bar_h
        control_panel.config(width=control_panel_w, height=control_panel_h)
        control_panel.place(x=0, y=bar_h)

        # resize the right panel
        right_control_panel_w = window_w * right_control_panel_scale
        right_control_panel_h = window_h - bar_h
        right_control_panel.config(width=right_control_panel_w,
                                   height=right_control_panel_h)
        right_control_panel.place(x=window_w - right_control_panel_w, y=bar_h)

        # calculate the weight and height of the map area
        map_area_h = window_h - bar_h
        map_area_w = window_w - control_panel_w - right_control_panel_w

        # calculate the proportion of the map
        global proportion
        margin = 30.0
        proportion = min([((map_area_w - margin) / float(len(canvases))) /
                          float(tools.map.cut_map_width),
                          (map_area_h * (1.0 - lab_map_title_scale) - margin) /
                          float(tools.map.cut_map_height)])

        # calculate the width and height of the photo of map, avoiding witdth or height < 1
        image_width = max([int(proportion * tools.map.map_width), 1])
        image_height = max([int(proportion * tools.map.map_height), 1])

        # resize the map and make it a photo
        new_image = tools.map.image_file.resize((image_width, image_height),
                                                Image.Resampling.LANCZOS)

        # this photo should be a global variable, otherwise, when this variable disappears, the photo will also disappear on the window
        global photo
        photo = ImageTk.PhotoImage(new_image)

        # calculate the width and height of the canvases
        canvas_width = max([int(proportion * tools.map.cut_map_width), 1])
        canvas_height = max([int(proportion * tools.map.cut_map_height), 1])

        # resize the canvases, and recreate the map with the newest size
        for canvas in canvases:
            canvas.config(width=canvas_width, height=canvas_height)
            canvas.delete("map")
            canvas.create_image(
                (image_width / 2 - int(tools.map.left_cut * proportion),
                 image_height / 2 - int(tools.map.top_cut * proportion)),
                image=photo,
                tag="map")

        # put the canvases on the window averagely
        one_width = map_area_w_scale / float(len(canvases))
        first_relx = control_panel_scale + (map_area_w_scale /
                                            float(len(canvases))) / 2.0
        map_title_height = map_area_h - canvas_height
        for index, canvas in enumerate(canvases):
            relx = first_relx + index * one_width
            rely = top_bar_scale + map_title_height / window_h + (
                1 - top_bar_scale - map_title_height / window_h) * 0.5
            canvas.place(relx=relx, rely=rely, anchor=tkinter.CENTER)

        # calculate the size and resize the map titles, based on the label with the longest text
        # When we change the titles, the width should be adjust accordingly to different titles
        # lab_map_title_font.adjust_font(window_w / float(len(map_titles)) * 0.9, map_title_height * 0.5)
        lab_map_title_font.adjust_font(canvas_width * 0.7 * 0.9,
                                       map_title_height * 0.5)
        label_lab_map_title.configure(font=lab_map_title_font.text_font)

        for index, map_title in enumerate(map_titles):
            relx = first_relx + index * one_width
            # put the map titles at the down 1/3 of the gap between the map and the top bar
            rely = top_bar_scale + (map_title_height * 2.0 / 3.0) / window_h
            map_title.place(relx=relx, rely=rely, anchor=tkinter.CENTER)