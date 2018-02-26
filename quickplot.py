# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 15:11:45 2018

@author: WalshTJ
"""

import sys
from PyQt4 import QtGui, QtCore
import math
import threading
import random
import pandas as pd
import cProfile
import time
import csv

global_frames = dict()



def round_to_1(x):
    if x == 0:
        return 0
    return round(x, -int(math.floor(math.log10(abs(x)))))

def rand_3d_unit(scale = 1):
    theta = 2*math.pi*random.randint(0, 360)/360.0
    phi = math.pi*random.randint(0, 180)/180.0
    x = scale*math.sin(phi)*math.cos(theta)
    y = scale*math.sin(phi)*math.sin(theta)
    z = scale*math.cos(phi)
    return (x,y,z)

class plot_data():
    def __init__(self, plot_type, data_x, data_y, title = "X vs Y"):
        self.data_lock = threading.Lock()
        self.plot_type = plot_type
        self.data_x = data_x
        self.data_y = data_y
        self.title = title
        self.point_size = 6
        self.line_width = 2
        
    def add_point(self, x, y):
        self.data_lock.acquire()
        self.data_x.append(x)
        self.data_y.append(y)
        self.data_lock.release()
        
    def get_data_x(self):
        self.data_lock.acquire()
        data_x_copy = list(self.data_x)
        self.data_lock.release()
        return data_x_copy
        
    def set_data_x(self, in_x):
        self.data_lock.acquire()
        self.data_x = list(in_x)
        self.data_lock.release()
        
    def get_data_y(self):
        self.data_lock.acquire()
        data_y_copy = list(self.data_y)
        self.data_lock.release()
        return data_y_copy
        
    def set_data_y(self, in_x):
        self.data_lock.acquire()
        self.data_y = list(in_y)
        self.data_lock.release()
        
    def get_max_x(self):
        self.data_lock.acquire()
        max_x = max(self.data_x)
        self.data_lock.release()
        return max_x

    def get_max_y(self):
        self.data_lock.acquire()
        max_y = max(self.data_y)
        self.data_lock.release()
        return max_y
        
    def get_min_x(self):
        self.data_lock.acquire()
        min_x = min(self.data_x)
        self.data_lock.release()
        return min_x

    def get_min_y(self):
        self.data_lock.acquire()
        min_y = min(self.data_y)
        self.data_lock.release()
        return min_y
        
    def set_data(self, x, y):
        self.data_lock.acquire()
        self.data_x = list(x)
        self.data_y = list(y)
        self.data_lock.release()


class menu_plot(QtGui.QWidget):
    def __init__(self, in_plot, win_size_x = 700, win_size_y = 500):
        super(menu_plot, self).__init__()
        self.top_plot = in_plot
        
        self.grid = QtGui.QGridLayout(self)
        self.grid.setSpacing(0)
        self.grid.setMargin(2)
        self.grid.addWidget(in_plot,0,0,1,6)
        self.setGeometry(100,100,win_size_x,win_size_y)
        
        self.set = 0

    def add_plot(self):
        pdata = plot_data("line",[0],[0])
        self.top_plot.add_plot(pdata)
        self.plot_data_list.clear()
        
        for i, p in enumerate(self.top_plot.plots):
            self.plot_data_list.addItem("Plot " + str(i))

    def apply_props(self):
        self.top_plot.x_axis_title = self.x_axis_prop_textbox.text()
        self.top_plot.y_axis_title = self.y_axis_prop_textbox.text()
        self.top_plot.plot_label_text = self.title_prop_textbox.text()
        self.properties_widget.hide()

    def show_properties(self):
        self.properties_widget = QtGui.QWidget()
        self.properties_grid = QtGui.QGridLayout(self.properties_widget)
        self.title_prop_textbox = QtGui.QLineEdit()
        self.title_prop_label = QtGui.QLabel()
        self.title_prop_label.setText("Plot Title")
        self.properties_grid.addWidget(self.title_prop_textbox,0,0)
        self.properties_grid.addWidget(self.title_prop_label,0,1)
        
        self.x_axis_prop_textbox = QtGui.QLineEdit()
        self.x_axis_prop_label = QtGui.QLabel()
        self.x_axis_prop_label.setText("X Axis Label")
        self.properties_grid.addWidget(self.x_axis_prop_textbox,1,0)
        self.properties_grid.addWidget(self.x_axis_prop_label,1,1)

        self.y_axis_prop_textbox = QtGui.QLineEdit()
        self.y_axis_prop_label = QtGui.QLabel()
        self.y_axis_prop_label.setText("Y Axis Label")
        self.properties_grid.addWidget(self.y_axis_prop_textbox,2,0)
        self.properties_grid.addWidget(self.y_axis_prop_label,2,1)          
        
        self.apply_button = QtGui.QPushButton()
        self.apply_button.setText("Apply")
        self.apply_button.clicked.connect(self.apply_props)
        self.apply_button.setMaximumWidth(100)  
        self.properties_grid.addWidget(self.apply_button,3,0)
        
        self.properties_widget.show()
        #self.grid.addWidget(self.properties_widget,2,0,1,6)
        #self.properties_grid.setRowStretch(0,0)
        #self.grid.setRowStretch(2,0)

    def start_timer(self):
        self.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.loop_event)
        self.timer.start(1000/60)
        
    def loop_event(self):
        self.top_plot.draw_plot(self.top_plot.last_size_x, self.top_plot.last_size_y)
                       
        if global_frames and not self.set:
            max_box_width = 300
            self.add_plot_button = QtGui.QPushButton()
            self.add_plot_button.setText("Add Plot")
            self.add_plot_button.clicked.connect(self.add_plot)
            self.add_plot_button.setMaximumWidth(100)
            self.grid.addWidget(self.add_plot_button,1,0)
            
            self.plot_data_list = QtGui.QComboBox()
            self.plot_data_list.addItem("Plot 1")
            self.plot_data_list.addItem("Plot 2")
            self.grid.addWidget(self.plot_data_list,1,1)    
            self.plot_data_list.setMaximumWidth(max_box_width)
            
            self.file_list = QtGui.QComboBox()
            self.file_list.addItems(global_frames.keys())
            self.grid.addWidget(self.file_list,1,2)
            self.file_list.setMaximumWidth(max_box_width)
            
            self.column_list_x = QtGui.QComboBox()
            self.column_list_x.addItems(list(global_frames[str(self.file_list.currentText())].columns.values))
            self.grid.addWidget(self.column_list_x,1,3)
            self.column_list_x.setMaximumWidth(max_box_width)
            
            self.column_list_x.currentIndexChanged.connect(self.on_column_change)
            
            self.column_list_y = QtGui.QComboBox()
            self.column_list_y.addItems(list(global_frames[str(self.file_list.currentText())].columns.values))
            self.grid.addWidget(self.column_list_y,1,4)
            self.column_list_y.setMaximumWidth(max_box_width)
            self.set = 1
            
            self.column_list_y.currentIndexChanged.connect(self.on_column_change)
            
            self.edit_button = QtGui.QPushButton()
            self.edit_button.setText("Edit")
            self.edit_button.clicked.connect(self.show_properties)
            self.edit_button.setMaximumWidth(100)
            self.grid.addWidget(self.edit_button,1,5)
            
    def on_column_change(self):
        plot_num = self.plot_data_list.currentIndex()
        current_file = self.file_list.currentText()
        col_x = self.column_list_x.currentText()
        col_y = self.column_list_y.currentText()
        self.top_plot.plots[plot_num].set_data(global_frames[current_file][col_x], global_frames[current_file][col_y])
        self.top_plot.paths[plot_num] = self.top_plot.create_path_from_plot_data(self.top_plot.plots[plot_num])
        self.top_plot.refresh_plot = 1


class multi_plot(QtGui.QWidget):
    def __init__(self, in_plots, win_size_x = 700, win_size_y = 500):
        super(multi_plot, self).__init__()
        self.plots = in_plots
        self.grid = QtGui.QGridLayout(self)
        self.grid.setSpacing(0)
        self.grid.setMargin(2)
        self.setGeometry(100,100,win_size_x,win_size_y)
        self.last_time = time.time()
        self.second_average = 0
        self.time_count = 0
        for i in range(0,len(in_plots)):
            for j in range(0,len(in_plots[0])):
                if in_plots[i][j] != None:
                    self.grid.addWidget(in_plots[i][j],i,j)
                    #in_plots[i][j].start_timer()
        self.show()
                    
    def start_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.loop_event)
        self.timer.start(1000*1.0/30)
        
    def loop_event(self):
        self.second_average += time.time() - self.last_time
        self.time_count += 1
        if self.second_average > 1.0:
            print "FPS", 1.0/(self.second_average/self.time_count)
            self.time_count = 0
            self.second_average = 0
        
        for i in range(0,len(self.plots)):
            for j in range(0,len(self.plots[0])):
                if self.plots[i][j] != None:
                    self.plots[i][j].loop_event()
        self.last_time = time.time()
                  

class view_plot(QtGui.QGraphicsView):
    def __init__(self, scene, parent):
        super(view_plot, self).__init__(scene, parent)
        self.mouse_press_active_left = 0
        self.mouse_press_point = None
        self.unprocessed_release = 0
        self.mouse_release_point = None
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.frames = []
        self.files = []
        self.scale(1,-1)
        #self.setRenderHint(QtGui.QPainter.Antialiasing)
    
    def mousePressEvent(self, event):
        self.mouse_press_point = event.pos()
        if event.button() == 1:
            self.mouse_press_active_left = 1
            
            
    def mouseReleaseEvent(self, event):
        if event.button() == 1:
            self.mouse_press_active_left = 0
            self.unprocessed_release = 1
            self.mouse_release_point = event.pos()
            
    def mouseMoveEvent(self, event):
        self.mouse_current_point = event.pos()
        
    def process_release(self):
        if self.unprocessed_release:
            self.unprocessed_release = 0
            return 1
        return 0
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:                
            event.accept()
    
    def dropEvent(self, event):
        event.accept()
        if event.mimeData().hasUrls:
            for url in event.mimeData().urls():
                fname = str(url.toLocalFile())
                print fname
                #try:
                
                for i in range(0,5):
                        if fname.endswith(".csv"):
                            try:
                                frm = pd.read_csv(fname,skiprows=i,low_memory=False)
                            except:
                                continue
                            print frm.columns.values
                        elif fname.endswith(".xls") or fname.endswith("xlsx"):
                            frm = pd.read_excel(fname,skiprows=i)
                        if list(frm.columns.values)[-1].startswith("Unnamed:"):
                            continue
                        else:
                            break
                            
                    
                global_frames[fname] = frm
                self.files.append(fname)
                break
                #except:
                #    print "Failed pandas read"
                    
    def fitInView(self, rect, flags = QtCore.Qt.IgnoreAspectRatio):
        if self.scene() is None or rect.isNull():
            return
        self.last_scene_roi = rect
        unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        self.scale(1/unity.width(), 1/unity.height())
        viewRect = self.viewport().rect()
        sceneRect = self.transform().mapRect(rect)
        xratio = viewRect.width() / sceneRect.width()
        yratio = viewRect.height() / sceneRect.height()
        if flags == QtCore.Qt.KeepAspectRatio:
            xratio = yratio = min(xratio, yratio)
        elif flags == QtCore.Qt.KeepAspectRatioByExpanding:
            xratio = yratio = max(xratio, yratio)
        self.scale(xratio, yratio)
        self.centerOn(rect.center())  
                        
class plot(QtGui.QWidget):
    def __init__(self, in_plot, win_size_x = 500, win_size_y = 400):

        super(plot, self).__init__()
        
        self.last_size_x = win_size_x
        self.last_size_y = win_size_y 
        
        self.show_point = 0
        
        self.setMouseTracking(True)
        self.plots = [in_plot]
        self.paths = [self.create_path_from_plot_data(in_plot)]
        self.auto_axis_x = True
        self.auto_axis_y = True
        self.max_axis_x = 1
        self.min_axis_x = 0
        self.max_axis_y = 1
        self.min_axis_y = 0
        self.auto_x_axis_division = True
        self.auto_y_axis_division = True
        self.x_axis_div = 0.1
        self.y_axis_div = 0.1
        
        self.max_tick_font_size = 22
        self.min_tick_font_size = 10
        
        self.point_font_size = 12
        
        self.x_axis_title = "X Axis (units)"
        self.y_axis_title = "Y Axis (units)"
        self.plot_label_text = "X vs Y"
        
        self.textboxes = dict()
        
        self.axis_menu = False
        
        self.win_size_x = win_size_x
        self.win_size_y = win_size_y   
        
        
        self.plot_scene = QtGui.QGraphicsScene()
        self.bg_brush = QtGui.QBrush(QtGui.QColor(200,200,200))
        self.ext_surface = QtGui.QGraphicsScene(0,0,win_size_x,win_size_y)
        self.ext_surface.setBackgroundBrush(self.bg_brush)
        self.initUI()
        
        self.set = 0
        self.menu_height = 0
        self.btn = None
        self.refresh_plot = 1
        self.draw_plot_flag = 1
        self.hud_items = []
            
    def initUI(self):
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        
        self.setToolTip('This is a <b>QWidget</b> widget')
        
        
        self.view = QtGui.QGraphicsView(self.ext_surface, self)
        self.view.setAcceptDrops(True)
        self.plot_view = view_plot(self.plot_scene, self.view)
        self.plot_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.plot_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.view.move(0,0)
        #self.view.resize(300,200)
        #self.view.setHorizontalScrollBarPolicy(QtGui.)
        
        #btn = QtGui.QPushButton('Button', self)
        #btn.setToolTip('This is a <b>QPushButton</b> widget')
        #btn.resize(btn.sizeHint())
        #btn.move(50, 50)       
        
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Tooltips')
        
    def add_plot(self, in_plot):
        self.plots.append(in_plot)
        self.paths.append(self.create_path_from_plot_data(in_plot))
        
    def create_path_from_plot_data(self, in_plot_data):
        
        x_data = in_plot_data.get_data_x()
        y_data = in_plot_data.get_data_y()
        path = QtGui.QPainterPath(QtCore.QPointF(x_data[0],y_data[0]))
        for i in range(1, len(x_data)):
            path.lineTo(x_data[i],y_data[i])
            
        return path
    
    def create_plot_scene(self, in_path):
        scene = QtGui.QGraphicsScene()
        scene.addPath(in_path)
        
        return scene
        
    def create_plot_viewer(self, in_scene, in_x_min, in_x_max, in_y_min, in_y_max):
        view = QtGui.QGraphicsView(in_scene)
        view.fitInView(in_x_min, in_y_min, in_x_max - in_x_min, in_y_max - in_y_min)

      
    
    def draw_plot(self, size_x = 500, size_y = 400):

        self.draw_plot_flag = 0
        self.last_size_x = size_x
        self.last_size_y = size_y
        self.ext_surface = QtGui.QGraphicsScene(0,0,size_x-2,size_y-2)
        self.view.setScene(self.ext_surface)
        self.ext_surface.setBackgroundBrush(self.bg_brush)
        self.view.move(0,0)
        
        self.view.resize(size_x,size_y)        
        
        for hi in self.hud_items:
            self.plot_scene.removeItem(hi)
        self.hud_items = []
        
        
        
        if self.refresh_plot:
            self.plot_scene.clear()
            random.seed(0)
            for i,p in enumerate(self.paths):
                
                raw_color = rand_3d_unit(255)
                color = (abs(raw_color[0]),abs(raw_color[1]),abs(raw_color[2]))
                plot_pen = QtGui.QPen()
                plot_pen.setCosmetic(True)
                plot_pen.setWidth(self.plots[i].line_width)
                plot_pen.setColor(QtGui.QColor(color[0],color[1],color[2]))
                self.plot_scene.addPath(p,plot_pen)
            self.refresh_plot = 0
        
        plot_width = int(size_x*0.8)
        plot_height = int(size_y*0.8)
        
        y_tick_size = max([plot_width*0.03,3])
        x_tick_size = max([plot_height*0.04,4])
        y_tick_size = x_tick_size*0.75
        
        tick_font_size = int(plot_height*0.03)
        axis_font_size = min([int(plot_height*0.05),18])
        title_font_size = min([int(plot_height*0.1),26])
        point_font_size = 8
        
        
        #self.plot_view.setScene(self.plot_surface)
        self.plot_view.move(size_x/2 - plot_width/2, size_y/2 - plot_height/2)
        self.plot_view.resize(plot_width,plot_height)
        
        # set up the text
        # set up fonts
        
        #self.title_font_path = pygame.font.match_font("couriernew", True)
        #self.title_font = pygame.font.Font(self.title_font_path,28)
        self.title_font = QtGui.QFont("Courier New", title_font_size)
        self.title_font.setBold(True)
        

        self.axis_font = QtGui.QFont("Courier New", axis_font_size)
        self.axis_font.setBold(True)
        
        self.point_font = QtGui.QFont("Courier New", point_font_size)
        
        self.point_font = QtGui.QFont("Courier New", point_font_size)
        
        if tick_font_size > self.max_tick_font_size:
            tick_font_size = self.max_tick_font_size
        if tick_font_size < self.min_tick_font_size:
            tick_font_size = self.min_tick_font_size
        self.tick_font = QtGui.QFont("Courier New", tick_font_size)
        
        #text = self.title_font.render(self.plots[0].title, True, BLACK)
        #textRect = text.get_rect()
        #textRect.centerx = self.ext_surface.get_rect().centerx
        #textRect.centery = self.ext_surface.get_rect().centery - int(size_y*0.9)/2
        title_text = self.ext_surface.addSimpleText(self.plot_label_text ,self.title_font)
        title_pos_y = size_y/2 - title_text.boundingRect().height()/2 - int(size_y*0.9)/2
        if title_pos_y < 0:
            title_pos_y = 0
        title_text.setPos(size_x/2 - title_text.boundingRect().width()/2, title_pos_y)
        

        # main plot rectangle
        #self.plot_rect = QtGui.QRectF(self.ext_surface.get_rect().centerx - plot_width/2, self.ext_surface.get_rect().centery - plot_height/2, plot_width, plot_height)
        #self.plot_rect = pygame.Rect(self.ext_surface.get_rect().centerx - plot_width/2, self.ext_surface.get_rect().centery - plot_height/2, plot_width, plot_height)
        plot_left = size_x/2 - plot_width/2
        plot_top = size_y/2 - plot_height/2
        
        
        
        if self.auto_axis_x:
            x_max = max([pl.get_max_x() for pl in self.plots])
        else:
            x_max = self.max_axis_x
        if self.auto_axis_y:
            y_max = max([pl.get_max_y() for pl in self.plots])
        else:
            y_max = self.max_axis_y
            
        if self.auto_axis_x:
            x_min = min([pl.get_min_x() for pl in self.plots])
        else:
            x_min = self.min_axis_x
        if self.auto_axis_y:
            y_min = min([pl.get_min_y() for pl in self.plots])
        else:
            y_min = self.min_axis_y
            
        if not self.auto_x_axis_division:
            x_div = self.x_axis_div
        else:
            x_div = round_to_1((x_max - x_min)/(plot_width/100.0))
            #x_min = round_to_1(x_min)
            #x_max = round_to_1(x_max)
        if not self.auto_y_axis_division:
            y_div = self.y_axis_div
        else:
            y_div = round_to_1((y_max - y_min)/(plot_height/100.0))
            #y_min = round_to_1(y_min)
            #y_max = round_to_1(y_max)

        if x_max == x_min:
            x_max = x_min + 1
        if x_div == 0:
            x_div = 1

        if y_max == y_min:
            y_max = y_min + 1
        if y_div == 0:
            y_div = 1
        
        
        self.plot_view.fitInView(QtCore.QRectF(x_min, y_min, x_max - x_min, y_max - y_min))  
        
        #self.plot_scene.addLine(self.plot_view.mapToScene(0,0).x(), self.plot_view.mapToScene(0,0).y(), self.plot_view.mapToScene(plot_width,plot_height).x(), self.plot_view.mapToScene(plot_width,plot_height).y())
        text_size = max([min([1.0*plot_width*x_div/(x_max - x_min)/(0.8*len(str(x_min+x_div))),18]),12])
        self.tick_font.setPixelSize(text_size)

        for tick in range(int(x_min/x_div),int(x_max/x_div)+2):

            if abs(tick*x_div - x_max) < (x_max - x_min)*1.0/plot_width:
                tick_position = plot_width+1
            elif abs(tick*x_div - x_min) < (x_max - x_min)*1.0/plot_width: 
                tick_position = -1
            elif tick*x_div > x_max or tick*x_div < x_min:
                continue
            else:
                tick_position = plot_width*(tick-(x_min/x_div))/(x_max/x_div-x_min/x_div)
            self.hud_items.append(self.plot_scene.addLine(tick*x_div, self.plot_view.mapToScene(0,plot_height).y(), tick*x_div, self.plot_view.mapToScene(0,plot_height - x_tick_size).y()))
            if len(str(tick*x_div)) > 6:
                tick_string = "{:.3e}".format(tick*y_div)
            else:
                tick_string = str(tick*x_div)
            
            tick_text = self.ext_surface.addSimpleText(tick_string ,self.tick_font)
            tick_pos_y = plot_top + plot_height + 5
            tick_pos_x = tick_position + plot_left - tick_text.boundingRect().width()/2

            tick_text.setPos(tick_pos_x, tick_pos_y)

        
        axis_text = self.ext_surface.addSimpleText(self.x_axis_title ,self.axis_font)

        axis_pos_y = (plot_top + plot_height + 5 + axis_font_size + size_y)/2 - axis_text.boundingRect().height()/2
        axis_pos_x = size_x/2 - axis_text.boundingRect().width()/2
        axis_text.setPos(axis_pos_x, axis_pos_y)
            
        for tick in range(int(y_min/y_div),int(y_max/y_div)+2):
            if abs(tick*y_div - y_max) < (y_max - y_min)*1.0/plot_height:
                tick_position = plot_height+1
            elif abs(tick*y_div - y_min) < (y_max - y_min)*1.0/plot_height: 
                tick_position = -1
            elif tick*y_div > y_max or tick*y_div < y_min:
                continue
            else:
                tick_position = plot_height*(tick-(y_min/y_div))/(y_max/y_div-y_min/y_div)
            self.hud_items.append(self.plot_scene.addLine(self.plot_view.mapToScene(0,0).x(), tick*y_div, self.plot_view.mapToScene(y_tick_size,0).x(), tick*y_div))
            
            #self.plot_surface.addLine(-1, plot_height - tick_position, y_tick_size, plot_height - tick_position)
            if len(str(tick*y_div)) > 6:
                tick_string = "{:.2e}".format(tick*y_div)
            else:
                tick_string = str(tick*y_div)
            tick_text = self.ext_surface.addSimpleText(tick_string ,self.tick_font)
            tick_pos_x = plot_left - 5 - tick_text.boundingRect().width()
            tick_pos_y = plot_height - tick_position + plot_top - tick_text.boundingRect().height()/2

            tick_text.setPos(tick_pos_x, tick_pos_y)
        

        axis_text = self.ext_surface.addSimpleText(self.y_axis_title ,self.axis_font)
        axis_text.rotate(-90)
        axis_pos_y = size_y/2 + axis_text.boundingRect().width()/2
        axis_pos_x = max([(plot_left - 5 - tick_text.boundingRect().width())/2 - axis_text.boundingRect().height()/2,0])
        axis_text.setPos(axis_pos_x, axis_pos_y)        
    

        if self.show_point:
            mouse_pos_coord_x = (1.0*self.plot_view.mouse_current_point.x()/plot_width)*(x_max - x_min) + x_min
            mouse_pos_coord_y = ((plot_height - 1.0*self.plot_view.mouse_current_point.y())/plot_height)*(y_max - y_min) + y_min
            axis_text = self.plot_surface.addSimpleText("%.2f" % mouse_pos_coord_x + ", " + "%.2f" % mouse_pos_coord_y ,self.point_font)
            
            axis_pos_y = self.plot_view.mouse_current_point.y() - axis_text.boundingRect().height()
            axis_pos_x = self.plot_view.mouse_current_point.x() - axis_text.boundingRect().width()
            axis_text.setPos(axis_pos_x, axis_pos_y)
            box_pen = QtGui.QPen()
            box_brush = QtGui.QBrush(QtGui.QColor(255,255,255))
            #box_pen.setStyle(QtCore.Qt.DashLine)
            box_box = self.plot_surface.addRect(axis_pos_x,
                                      axis_pos_y,
                                      axis_text.boundingRect().width(), 
                                      axis_text.boundingRect().height(),
                                      box_pen, box_brush)
            axis_text.setZValue(box_box.zValue()+1)

        if self.plot_view.mouse_press_active_left:
            box_pen = QtGui.QPen()
            box_pen.setStyle(QtCore.Qt.DashLine)
            self.hud_items.append(self.plot_scene.addRect(self.plot_view.mapToScene(self.plot_view.mouse_press_point.x(),0).x(),
                                      self.plot_view.mapToScene(0,self.plot_view.mouse_press_point.y()).y(),
                                      self.plot_view.mapToScene(self.plot_view.mouse_current_point.x(),0).x() - self.plot_view.mapToScene(self.plot_view.mouse_press_point.x(),0).x(), 
                                      self.plot_view.mapToScene(0,self.plot_view.mouse_current_point.y()).y() - self.plot_view.mapToScene(0,self.plot_view.mouse_press_point.y()).y(),
                                      box_pen))
        if self.plot_view.process_release():
            self.auto_axis_x = False
            self.auto_axis_y = False
            window_relative_min_x = min([self.plot_view.mouse_press_point.x(), self.plot_view.mouse_release_point.x()])
            window_relative_max_x = max([self.plot_view.mouse_press_point.x(), self.plot_view.mouse_release_point.x()])
            window_relative_min_y = min([plot_height - self.plot_view.mouse_press_point.y(), plot_height - self.plot_view.mouse_release_point.y()])
            window_relative_max_y = max([plot_height - self.plot_view.mouse_press_point.y(), plot_height - self.plot_view.mouse_release_point.y()])
            self.min_axis_x = x_min + 1.0*(x_max - x_min)*window_relative_min_x/plot_width
            self.max_axis_x = x_min + 1.0*(x_max - x_min)*window_relative_max_x/plot_width
            self.min_axis_y = y_min + 1.0*(y_max - y_min)*window_relative_min_y/plot_height
            self.max_axis_y = y_min + 1.0*(y_max - y_min)*window_relative_max_y/plot_height
            
        
        return
        
    def resizeEvent(self, event):
        self.draw_plot_flag = 1
        self.draw_plot(event.size().width(),
                       event.size().height())
                       
    def mouseMoveEvent(self, event):
        print event.pos()
        
    def keyPressEvent(self, event):
        if event.key() == 0x01000000:
            self.auto_axis_x = 1
            self.auto_axis_y = 1
            self.draw_plot_flag = 1
        elif event.key() == 0x5a:
            self.show_point = 1
            
    def keyReleaseEvent(self, event):

        if event.key() == 0x5a:
            self.show_point = 0
        
    def loop_event(self):
        self.draw_plot(self.last_size_x,
                       self.last_size_y)
    

def main():
    
    app = QtGui.QApplication(sys.argv)

    #test_plot = plot(plot_data("scatter",[x/10.0 for x in range(-50,50,2)],[math.sin(x/10.0) for x in range(-50,50,2)]))
    #test_plot.add_plot(plot_data("line",[x/10.0 for x in range(-50,50,2)],[0.7071*math.cos(x/10.0) for x in range(-50,50,2)]))
    #test_plot.add_plot(plot_data("line",[x/10.0 for x in range(-5000,5000,2)],[0.7071*math.cos(x/10.0-2) for x in range(-5000,5000,2)]))

    ex = plot(plot_data("line",[x/10.0 for x in range(0,100,2)],[5+math.sin(x/10.0) for x in range(0,100,2)]))
    ex.add_plot(plot_data("line",[x/10.0 for x in range(0,100,2)],[5+0.7071*math.cos(x/10.0) for x in range(0,100,2)]))
    ex2 = plot(plot_data("line",[x/10.0 for x in range(0,100,2)],[math.sin(x/10.0) for x in range(0,100,2)]))
    ex2.add_plot(plot_data("line",[x/10.0 for x in range(0,100,2)],[0.7071*math.cos(x/10.0) for x in range(0,100,2)]))
    menu_p = menu_plot(ex)
    menu_p2 = menu_plot(ex2)
    #ex.start()
    menu_p.start_timer()
    #mp = multi_plot([[menu_p,menu_p2]])
    #mp.start_timer()
    sys.exit(app.exec_())


if __name__ == '__main__':
    #cProfile.run('main()')
    main()
