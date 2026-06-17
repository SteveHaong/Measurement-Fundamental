import dearpygui.dearpygui as dpg
import serial
import serial.tools.list_ports
import threading
import time
import math
import json

# Khởi tạo tham số toàn cục để lưu dữ liệu
data_length = 100
sensor_data_y = [0.0] * data_length  # Dữ liệu nhiệt độ
pwm_data_y = [0.0] * data_length    # Dữ liệu PWM
sensor_data_x = list(range(data_length))  # Trục X (thời gian)

last_chart_update = 0.0
current_temp = 0.0
current_hum = 0.0
current_mq135 = 0
current_mq7 = 0
current_pwm = 0
current_rpm = 0

serial_port = None
is_running = True
is_connected = False
fan_angle = 0.0

def set_visual_theme():
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 35, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (45, 45, 55, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (60, 60, 100, 255))
    dpg.bind_theme(global_theme)

def serial_thread():
    global current_temp, current_hum, current_mq135, current_mq7, current_pwm, current_rpm, is_connected
    while is_running:
        if serial_port and serial_port.is_open:
            try:
                line = serial_port.readline().decode('utf-8').strip()
                if line.startswith("{") and line.endswith("}"):
                    data = json.loads(line)
                    
                    
                    current_temp = float(data.get("T", 0.0))
                    current_hum = float(data.get("H", 0.0))
                    current_mq135 = int(data.get("M135", 0))
                    current_mq7 = int(data.get("M7", 0))
                    current_pwm = int(data.get("PWM", 0))
                    
                  
                    current_rpm = current_pwm * 10 
            except Exception as e:
                pass 
        else:
            time.sleep(0.1)

def toggle_connection():
    global serial_port, is_connected
    if is_connected:
        if serial_port:
            serial_port.close()
        is_connected = False
        dpg.set_value("status_text", "Status: Disconnected")
        dpg.configure_item("connect_btn", label="Connect")
    else:
        com_port = dpg.get_value("com_port_combo")
        try:
            port_name = com_port.split()[0]
            serial_port = serial.Serial(port_name, 115200, timeout=1)
            is_connected = True
            dpg.set_value("status_text", f"Status: Connected to {port_name}")
            dpg.configure_item("connect_btn", label="Disconnect")
        except Exception as e:
            dpg.set_value("status_text", f"Lỗi: {e}")

def scan_ports():
    ports = serial.tools.list_ports.comports()
    port_list = [f"{port.device} - {port.description}" for port in ports]
    if port_list:
        dpg.configure_item("com_port_combo", items=port_list)
        dpg.set_value("com_port_combo", port_list[0])
    else:
        dpg.configure_item("com_port_combo", items=["Không tìm thấy COM"])
        dpg.set_value("com_port_combo", "Không tìm thấy COM")

def update_fan_animation():
    global fan_angle
    fps = dpg.get_frame_rate()
    delta = 1.0 / fps if fps > 0 else 0.016
    rps = current_rpm / 60.0
    fan_angle += rps * delta * 2 * math.pi
    
    dpg.delete_item("fan_drawlist", children_only=True)
    center = (100, 100)
    radius = 60
    
    dpg.draw_circle(center, radius + 10, color=[100, 100, 100], thickness=4, parent="fan_drawlist")
    
    blades = 3
    color_modifier = int((current_pwm / 100.0) * 155)
    blade_color = [100 + color_modifier, 200 - color_modifier, 250, 200]
    
    for i in range(blades):
        theta = fan_angle + i * (2 * math.pi / blades)
        p1 = center
        p2 = (center[0] + radius * math.cos(theta - 0.4), center[1] + radius * math.sin(theta - 0.4))
        p3 = (center[0] + radius * math.cos(theta + 0.4), center[1] + radius * math.sin(theta + 0.4))
        dpg.draw_triangle(p1, p2, p3, color=[200, 200, 200], fill=blade_color, parent="fan_drawlist")
        
    dpg.draw_circle(center, 15, color=[150, 150, 150], fill=[50, 50, 50], parent="fan_drawlist")

def update_thermo_animation():
    dpg.delete_item("thermo_drawlist", children_only=True)
    dpg.draw_rectangle((40, 20), (70, 150), color=[200, 200, 200], thickness=2, rounding=15, parent="thermo_drawlist")
    dpg.draw_circle((55, 160), 25, color=[200, 200, 200], thickness=2, parent="thermo_drawlist")
    
    temp_clamped = min(max(current_temp, 0), 100)
    h = (temp_clamped / 100.0) * 115
    
    if temp_clamped < 40:
        fill_color = [50, 200, 255]
    elif temp_clamped < 70:
        fill_color = [255, 200, 50]
    else:
        fill_color = [255, 50, 50]
        
    dpg.draw_rectangle((44, 142 - h), (66, 150), color=fill_color, fill=fill_color, rounding=0, parent="thermo_drawlist")
    dpg.draw_circle((55, 160), 20, color=fill_color, fill=fill_color, parent="thermo_drawlist")

def update_data():
    global last_chart_update
    
    if is_connected:
        current_time = time.time()
        # "Van xả": Ép đồ thị chỉ cập nhật 1 giây 1 lần
        if current_time - last_chart_update >= 1.0:
            # 1. Cập nhật mảng nhiệt độ
            sensor_data_y.pop(0)
            sensor_data_y.append(current_temp)
            dpg.set_value("sensor_series", [sensor_data_x, sensor_data_y])
            
            # 2. Cập nhật mảng PWM
            pwm_data_y.pop(0)
            pwm_data_y.append(current_pwm)
            dpg.set_value("pwm_series", [sensor_data_x, pwm_data_y])
            
            last_chart_update = current_time

    # Các UI khác (Text, Progress Bar, Animation) cho chạy tốc độ bàn thờ để mượt
    dpg.set_value("temp_val_txt", f"{current_temp:.2f} °C")
    dpg.set_value("rpm_val_txt", f"{current_rpm} RPM")
    dpg.set_value("pwm_val_txt", f"{current_pwm} %")
    dpg.set_value("hum_val_txt", f"{current_hum:.1f} %")
    dpg.set_value("mq7_val_txt", f"{current_mq7} / 4095")
    dpg.set_value("mq135_val_txt", f"{current_mq135} / 4095")
    
    dpg.set_value("pwm_bar", current_pwm / 100.0)
    dpg.set_value("mq7_bar", min(current_mq7 / 4095.0, 1.0))
    dpg.set_value("mq135_bar", min(current_mq135 / 4095.0, 1.0))
    
    update_fan_animation()
    update_thermo_animation()
dpg.create_context()
set_visual_theme()

with dpg.window(label="STM32 Dashboard - Interactive", tag="main_window"):
    dpg.add_text("SYSTEM MONITOR", color=[0, 255, 150])
    
    with dpg.group(horizontal=True):
        dpg.add_combo([], width=200, tag="com_port_combo")
        dpg.add_button(label="Scan", callback=scan_ports)
        dpg.add_button(label="Connect", tag="connect_btn", callback=toggle_connection)
    dpg.add_text("Status: Disconnected", color=[255, 255, 0], tag="status_text")
    dpg.add_separator()
    
    with dpg.group(horizontal=True):
        # 1. Cụm Nhiệt độ
        with dpg.child_window(width=150, height=250):
            dpg.add_text("Temp")
            dpg.add_text("0.00 °C", tag="temp_val_txt", color=[255, 200, 100])
            dpg.add_drawlist(width=150, height=200, tag="thermo_drawlist")
        
        # 2. Cụm Quạt
        with dpg.child_window(width=250, height=250):
            dpg.add_text("Cooling Fan")
            dpg.add_text("0 RPM", tag="rpm_val_txt", color=[100, 255, 255])
            dpg.add_drawlist(width=250, height=200, tag="fan_drawlist")
                
        # 3. Cụm MQ-7, MQ-135 và Độ ẩm (CỘT MỚI THÊM)
        with dpg.child_window(width=250, height=250):
            dpg.add_text("Gas & Air Quality", color=[255, 100, 100])
            
            dpg.add_text("MQ-7 (CO Level):")
            dpg.add_text("0 / 4095", tag="mq7_val_txt", color=[255, 150, 150])
            dpg.add_progress_bar(tag="mq7_bar", default_value=0.0, width=-1, height=15)
            
            dpg.add_spacer(height=10)
            dpg.add_text("MQ-135 (Air Level):")
            dpg.add_text("0 / 4095", tag="mq135_val_txt", color=[150, 255, 150])
            dpg.add_progress_bar(tag="mq135_bar", default_value=0.0, width=-1, height=15)
            
            dpg.add_spacer(height=10)
            dpg.add_text("Humidity:")
            dpg.add_text("0 %", tag="hum_val_txt", color=[100, 200, 255])
        
        # 4. Cụm PWM
        with dpg.child_window(width=-1, height=250):
            dpg.add_text("PWM Duty Cycle")
            dpg.add_text("0 %", tag="pwm_val_txt", color=[255, 100, 255])
            dpg.add_progress_bar(tag="pwm_bar", default_value=0.0, width=-1, height=20)
            
    dpg.add_spacer(height=10)
    
    # ---- KHU VỰC CHART ----
    with dpg.plot(label="PID Response: Temperature vs Fan PWM", height=-1, width=-1):
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="Time")
        
        # TRỤC Y SỐ 1 (Bên trái) - Nhiệt độ
        dpg.add_plot_axis(dpg.mvYAxis, label="Temperature (°C)", tag="y_axis_temp")
        dpg.set_axis_limits("y_axis_temp", 25, 45) 
        dpg.add_line_series(sensor_data_x, sensor_data_y, label="Temp (°C)", parent="y_axis_temp", tag="sensor_series")

        # TRỤC Y SỐ 2 (Bên phải) - Tốc độ quạt
        dpg.add_plot_axis(dpg.mvYAxis, label="PWM (%)", tag="y_axis_pwm")
        dpg.set_axis_limits("y_axis_pwm", -5, 105) # Lấy biên -5 đến 105 để đồ thị không cọ vào mép
        dpg.add_line_series(sensor_data_x, pwm_data_y, label="PWM (%)", parent="y_axis_pwm", tag="pwm_series")

scan_ports()

dpg.create_viewport(title='STM32 Animated Dashboard', width=1000, height=700)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)

thread = threading.Thread(target=serial_thread, daemon=True)
thread.start()

while dpg.is_dearpygui_running():
    update_data()
    dpg.render_dearpygui_frame()

is_running = False
if serial_port and serial_port.is_open:
    serial_port.close()
dpg.destroy_context()