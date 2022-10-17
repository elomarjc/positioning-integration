import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

import tkinter
from PIL import ImageTk

import tools.map
import tools.basewindow


# right bottom corner
class right_bottom_corner():

    def __init__(self, control_panel: tkinter.Frame):
        self.control_panel = control_panel

        self.person_icon = ImageTk.PhotoImage(tools.map.new_person_icon)
        self.uwbtag_icon = ImageTk.PhotoImage(tools.map.new_uwbtag_icon)
        self.robot_icon = ImageTk.PhotoImage(tools.map.new_robot_icon)

        self.base_rely = 1
        self.spacing = 0.05

        self.create_legend()
        self.create_text_switch()

    # create a legend on the right bottom corner
    def create_legend(self):
        # legend
        legend_spacing = 0.04

        # robot legend
        self.base_rely = self.base_rely - 0.03

        self.robot_icon_label = tkinter.Label(self.control_panel,
                                              image=self.robot_icon)
        self.robot_icon_label.pack()
        self.robot_icon_label.place(relx=0.1,
                                    rely=self.base_rely,
                                    anchor=tkinter.E)

        self.robot_legend_label = tkinter.Label(
            self.control_panel, text="Robot", font=tools.basewindow.text_font)
        self.robot_legend_label.pack()
        self.robot_legend_label.place(relx=0.12,
                                      rely=self.base_rely,
                                      anchor=tkinter.W)

        # uwb legend
        self.base_rely = self.base_rely - legend_spacing

        self.uwbtag_icon_label = tkinter.Label(self.control_panel,
                                               image=self.uwbtag_icon)
        self.uwbtag_icon_label.pack()
        self.uwbtag_icon_label.place(relx=0.1,
                                     rely=self.base_rely,
                                     anchor=tkinter.E)

        self.uwb_legend_label = tkinter.Label(self.control_panel,
                                              text="UWB Safety Tag",
                                              font=tools.basewindow.text_font)
        self.uwb_legend_label.pack()
        self.uwb_legend_label.place(relx=0.12,
                                    rely=self.base_rely,
                                    anchor=tkinter.W)

        # person legend
        self.base_rely = self.base_rely - legend_spacing

        self.legend_person_label = tkinter.Label(self.control_panel,
                                                 image=self.person_icon)
        self.legend_person_label.pack()
        self.legend_person_label.place(relx=0.1,
                                       rely=self.base_rely,
                                       anchor=tkinter.E)
        self.person_legend_label = tkinter.Label(
            self.control_panel, text="Person", font=tools.basewindow.text_font)
        self.person_legend_label.pack()
        self.person_legend_label.place(relx=0.12,
                                       rely=self.base_rely,
                                       anchor=tkinter.W)

    # put a checkbutton on the right bottom to turn on/off the text on the map
    def create_text_switch(self):
        text_switch_spacing = 0.07
        self.text_on = tkinter.BooleanVar()
        self.text_switch = tkinter.Checkbutton(self.control_panel,
                                               text="Show text on the map.",
                                               font=tools.basewindow.text_font,
                                               variable=self.text_on,
                                               onvalue=True,
                                               offvalue=False)
        self.text_switch.pack()
        self.text_switch.place(relx=0.5,
                               rely=self.base_rely - text_switch_spacing,
                               anchor=tkinter.CENTER)
