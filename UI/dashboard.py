import dearpygui.dearpygui as dpg
import serial
import serial.tools.list_ports
import threading
import time
import math

# Khởi tạo tham số toàn cục để lưu dữ liệu
data_length = 100
sensor_data_y = [0.0] * data_length
sensor_data_x = list(range(data_length))

current_sensor = 0.0
current_pwm = 0
current_rpm = 0

serial_port = None
is_running = True
is_connected = False

fan_angle = 0.0

# Lưu trạng thái theme và font để giao diện đẹp hơn
def set_visual_theme():
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 35, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (45, 45, 55, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (60, 60, 100, 255))
    dpg.bind_theme(global_theme)

# Hàm luồng riêng biệt để đọc Serial
def serial_thread():
    global current_sensor, current_pwm, current_rpm, is_connected
    while is_running:
        if serial_port and serial_port.is_open:
            try:
                line = serial_port.readline().decode('utf-8').strip()
                if line:
                    # Gói tin dự định: "Temp,PWM,RPM" (VD: "25.40,50,1500")
                    parts = line.split(',')
                    if len(parts) == 3:
                        current_sensor = float(parts[0])
                        current_pwm = int(parts[1])
                        current_rpm = int(parts[2])
            except Exception as e:
                print(f"Lỗi đọc Serial: {e}")
                is_connected = False
        else:
            time.sleep(0.1)

# Hàm kết nối/ngắt kết nối COM port
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
            # Lấy tên cổng từ chuỗi COM (Bỏ phần mô tả thiết bị)
            port_name = com_port.split()[0]
            serial_port = serial.Serial(port_name, 115200, timeout=1)
            is_connected = True
            dpg.set_value("status_text", f"Status: Connected to {port_name}")
            dpg.configure_item("connect_btn", label="Disconnect")
        except Exception as e:
            dpg.set_value("status_text", f"Lỗi: {e}")

# Hàm scan cổng COM và cập nhật vào ComboBox
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
    # Lấy thời gian render của frame trước để tính tốc độ quay chuẩn
    fps = dpg.get_frame_rate()
    delta = 1.0 / fps if fps > 0 else 0.016
    
    # Tính góc quay dựa trên RPM (Rotations per minute)
    rps = current_rpm / 60.0
    fan_angle += rps * delta * 2 * math.pi
    
    dpg.delete_item("fan_drawlist", children_only=True)
    center = (100, 100)
    radius = 60
    
    # Vẽ vỏ quạt
    dpg.draw_circle(center, radius + 10, color=[100, 100, 100], thickness=4, parent="fan_drawlist")
    
    # Vẽ cánh quạt
    blades = 3
    # Màu viền đổi theo tốc độ (PWM)
    color_modifier = int((current_pwm / 100.0) * 155)
    blade_color = [100 + color_modifier, 200 - color_modifier, 250, 200]
    
    for i in range(blades):
        theta = fan_angle + i * (2 * math.pi / blades)
        p1 = center
        p2 = (center[0] + radius * math.cos(theta - 0.4), center[1] + radius * math.sin(theta - 0.4))
        p3 = (center[0] + radius * math.cos(theta + 0.4), center[1] + radius * math.sin(theta + 0.4))
        dpg.draw_triangle(p1, p2, p3, color=[200, 200, 200], fill=blade_color, parent="fan_drawlist")
        
    # Vẽ trục giữa quạt
    dpg.draw_circle(center, 15, color=[150, 150, 150], fill=[50, 50, 50], parent="fan_drawlist")

def update_thermo_animation():
    dpg.delete_item("thermo_drawlist", children_only=True)
    
    # Vẽ vỏ nhiệt kế
    dpg.draw_rectangle((40, 20), (70, 150), color=[200, 200, 200], thickness=2, rounding=15, parent="thermo_drawlist")
    dpg.draw_circle((55, 160), 25, color=[200, 200, 200], thickness=2, parent="thermo_drawlist")
    
    # Tính độ cao cột thủy ngân dựa trên nhiệt độ (Thang 0-100 độ)
    temp_clamped = min(max(current_sensor, 0), 100)
    h = (temp_clamped / 100.0) * 115
    
    # Đổi màu cảnh báo theo nhiệt độ: Xanh -> Vàng -> Đỏ
    if temp_clamped < 40:
        fill_color = [50, 200, 255] # Lạnh
    elif temp_clamped < 70:
        fill_color = [255, 200, 50] # Thường / Hơi ấm
    else:
        fill_color = [255, 50, 50]  # Nóng (Cảnh báo)
        
    # Vẽ cột thủy ngân
    dpg.draw_rectangle((44, 142 - h), (66, 150), color=fill_color, fill=fill_color, rounding=0, parent="thermo_drawlist")
    dpg.draw_circle((55, 160), 20, color=fill_color, fill=fill_color, parent="thermo_drawlist")

def update_data():
    if is_connected:
        # Cập nhật mảng data cho biểu đồ
        sensor_data_y.pop(0)
        sensor_data_y.append(current_sensor)
        dpg.set_value("sensor_series", [sensor_data_x, sensor_data_y])
    
    # Cập nhật thông số bằng số
    dpg.set_value("sensor_val_txt", f"{current_sensor:.2f} °C")
    dpg.set_value("pwm_val_txt", f"{current_pwm} %")
    dpg.set_value("rpm_val_txt", f"{current_rpm} RPM")
    
    # Cập nhật Progress Bar (PWM)
    dpg.set_value("pwm_bar", current_pwm / 100.0)
    
    # Gọi hàm vẽ Animation
    update_fan_animation()
    update_thermo_animation()

dpg.create_context()
set_visual_theme() # Áp dụng màu sắc

# ---- THIẾT KẾ GIAO DIỆN ----
with dpg.window(label="STM32 Dashboard - Interactive", tag="main_window"):
    dpg.add_text("SYSTEM MONITOR", color=[0, 255, 150])
    
    with dpg.group(horizontal=True):
        dpg.add_combo([], width=200, tag="com_port_combo")
        dpg.add_button(label="Scan", callback=scan_ports)
        dpg.add_button(label="Connect", tag="connect_btn", callback=toggle_connection)
    dpg.add_text("Status: Disconnected", color=[255, 255, 0], tag="status_text")
    dpg.add_separator()
    
    # ---- KHU VỰC HIỂN THỊ ANIMATIONS ----
    with dpg.group(horizontal=True):
        # 1. Cụm Nhiệt độ
        with dpg.child_window(width=200, height=250):
            dpg.add_text("Temperature")
            dpg.add_text("0.00 °C", tag="sensor_val_txt", color=[255, 200, 100])
            dpg.add_drawlist(width=200, height=200, tag="thermo_drawlist")
        
        # 2. Cụm Quạt và PWM
        with dpg.child_window(width=300, height=250):
            dpg.add_text("Cooling Fan Speed")
            dpg.add_text("0 RPM", tag="rpm_val_txt", color=[100, 255, 255])
            dpg.add_drawlist(width=250, height=200, tag="fan_drawlist")
                
        # 3. Cụm Control Data
        with dpg.child_window(width=-1, height=250):
            dpg.add_text("PWM Duty Cycle")
            dpg.add_text("0 %", tag="pwm_val_txt", color=[255, 100, 255])
            dpg.add_progress_bar(tag="pwm_bar", default_value=0.0, width=-1, height=20, overlay="Current PWM %")
            
    dpg.add_spacer(height=10)
    
    # ---- KHU VỰC CHART ----
    with dpg.plot(label="Real-time Sensor Data", height=-1, width=-1):
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="Time")
        dpg.add_plot_axis(dpg.mvYAxis, label="Sensor Value", tag="y_axis")
        dpg.set_axis_limits("y_axis", 0, 150) 
        dpg.add_line_series(sensor_data_x, sensor_data_y, label="Temperature (°C)", parent="y_axis", tag="sensor_series")

scan_ports()

dpg.create_viewport(title='STM32 Animated Dashboard', width=900, height=700)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)

# Khởi động luồng đọc Serial
thread = threading.Thread(target=serial_thread, daemon=True)
thread.start()

# Vòng lặp giao diện
while dpg.is_dearpygui_running():
    update_data()
    dpg.render_dearpygui_frame()

# Dọn dẹp trước khi thoát
is_running = False
if serial_port and serial_port.is_open:
    serial_port.close()
dpg.destroy_context()
