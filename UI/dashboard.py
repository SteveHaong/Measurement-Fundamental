import dearpygui.dearpygui as dpg
import serial
import serial.tools.list_ports
import threading
import time

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

def update_data():
    if not is_connected:
        return
        
    # Cập nhật mảng biểu đồ
    sensor_data_y.pop(0)
    sensor_data_y.append(current_sensor)
    
    # Cập nhật giao diện Text
    dpg.set_value("sensor_val", f"Sensor: {current_sensor:.2f} *C")
    dpg.set_value("pwm_val", f"PWM: {current_pwm} %")
    dpg.set_value("fan_speed_val", f"Fan Speed: {current_rpm} RPM")
    
    # Cập nhật dữ liệu đồ thị Line
    dpg.set_value("sensor_series", [sensor_data_x, sensor_data_y])

dpg.create_context()

# ---- THIẾT KẾ GIAO DIỆN ----
with dpg.window(label="STM32 Dashboard", tag="main_window"):
    dpg.add_text("SYSTEM MONITOR", color=[0, 255, 0])
    
    with dpg.group(horizontal=True):
        dpg.add_combo([], width=200, tag="com_port_combo")
        dpg.add_button(label="Scan", callback=scan_ports)
        dpg.add_button(label="Connect", tag="connect_btn", callback=toggle_connection)
    
    dpg.add_text("Status: Disconnected", color=[255, 255, 0], tag="status_text")
    dpg.add_separator()
    
    with dpg.group(horizontal=True):
        dpg.add_text("Sensor: 0.00 *C", tag="sensor_val")
        dpg.add_text("   |   ")
        dpg.add_text("PWM: 0 %", tag="pwm_val")
        dpg.add_text("   |   ")
        dpg.add_text("Fan Speed: 0 RPM", tag="fan_speed_val")
        
    dpg.add_separator()
    dpg.add_spacer(height=10)
    
    with dpg.plot(label="Real-time Sensor Data", height=-1, width=-1):
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="Time")
        dpg.add_plot_axis(dpg.mvYAxis, label="Sensor Value", tag="y_axis")
        # Giới hạn trục Y lớn một chút để dễ quan sát (VD: 0 - 150)
        dpg.set_axis_limits("y_axis", 0, 150) 
        dpg.add_line_series(sensor_data_x, sensor_data_y, label="Temperature (*C)", parent="y_axis", tag="sensor_series")

scan_ports()

dpg.create_viewport(title='STM32 Dashboard - DearPyGui', width=800, height=600)
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
