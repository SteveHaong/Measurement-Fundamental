#include "sensor_raw.h"
#include "adc_dma.h"
#include "stm32f4xx.h"
// Thời gian chu kỳ tổng là 150 giây. Con B chạy lệch pha sau con A 75 giây.
static uint16_t timer_mq7_A = 0;
static uint16_t timer_mq7_B = 75;
static uint16_t final_mq7_value = 0;

// Khởi tạo -1.0 để đánh dấu là chưa có dữ liệu (lần chạy đầu tiên)
static float mq135_ema = -1.0;
static float mq7_A_ema = -1.0;
static float mq7_B_ema = -1.0;

// HÀM LỌC NHIỄU EMA  //
uint16_t Filter_EMA(uint16_t new_val, float *ema_val, float alpha) {
    if (*ema_val < 0.0) {
        *ema_val = (float)new_val; // Gán thẳng giá trị gốc trong lần chạy đầu tiên
    } else {
        *ema_val = (alpha * new_val) + ((1.0 - alpha) * (*ema_val));
    }
    return (uint16_t)(*ema_val);
}

uint16_t Get_MQ135_Raw(void) {
    // Độ mượt 0.15
    return Filter_EMA(adc_buffer[0], &mq135_ema, 0.15);
}

void MQ7_Cycle_Manager(void) {
    // --- 1. QUẢN LÝ CON MQ7_A ---
    timer_mq7_A++;
    if (timer_mq7_A >= 150) timer_mq7_A = 0;

    if (timer_mq7_A < 60) {
        // [Giai đoạn sấy 5V]: 60 giây đầu

    } else {
        // [Giai đoạn đo 1.4V]: 90 giây sau

        if (timer_mq7_A == 148) {
            // Ép qua màng lọc ngay tại thời điểm chốt số liệu (độ mượt 0.3 vì lấy mẫu thưa)
            final_mq7_value = Filter_EMA(adc_buffer[1], &mq7_A_ema, 0.3);
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
            // Ép qua màng lọc ngay tại thời điểm chốt số liệu
            final_mq7_value = Filter_EMA(adc_buffer[2], &mq7_B_ema, 0.3);
        }
    }
}

uint16_t Get_MQ7_Current_Raw(void) {
    // Giá trị này đã được lọc siêu sạch từ pha 148s của 1 trong 2 con MQ-7
    return final_mq7_value;
}
