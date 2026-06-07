#include "sensor_raw.h"
#include "adc_dma.h"

// Thời gian chu kỳ tổng là 150 giây. Con B chạy lệch pha sau con A 75 giây.
static uint16_t timer_mq7_A = 0;
static uint16_t timer_mq7_B = 75;
static uint16_t final_mq7_value = 0;

uint16_t Get_MQ135_Raw(void) {
    return adc_buffer[0]; // MQ135 đọc liên tục ở kênh 0
}

void MQ7_Cycle_Manager(void) {
    // --- 1. QUẢN LÝ CON MQ7_A ---
    timer_mq7_A++;
    if (timer_mq7_A >= 150) timer_mq7_A = 0;

    if (timer_mq7_A < 60) {
        // [Giai đoạn sấy 5V]: 60 giây đầu
        // Chỗ này sau này ông Nam cấu hình chân GPIO điều khiển sấy thì nhét vào đây
    } else {
        // [Giai đoạn đo 1.4V]: 90 giây sau
        if (timer_mq7_A == 148) { // Lấy mẫu ở giây thứ 148 (cuối chu kỳ đo) để dữ liệu ổn định nhất
            final_mq7_value = adc_buffer[1];
        }
    }

    // --- 2. QUẢN LÝ CON MQ7_B ---
    timer_mq7_B++;
    if (timer_mq7_B >= 150) timer_mq7_B = 0;

    if (timer_mq7_B < 60) {
        // [Giai đoạn sấy 5V] của con B
    } else {
        // [Giai đoạn đo 1.4V] của con B
        if (timer_mq7_B == 148) {
            final_mq7_value = adc_buffer[2]; // Cập nhật dữ liệu từ con B
        }
    }
}

uint16_t Get_MQ7_Current_Raw(void) {
    // Hàm này luôn trả về giá trị mới nhất của con đang trong pha ĐO cho lớp App dùng
    return final_mq7_value;
}
