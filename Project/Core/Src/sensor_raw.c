#include "sensor_raw.h"
#include "adc_dma.h"
#include "stm32f4xx.h"


// Khởi tạo -1.0 để đánh dấu là chưa có dữ liệu (lần chạy đầu tiên)
static float mq135_ema = -1.0;
static float mq7_ema = -1.0;

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
}

uint16_t Get_MQ7_Current_Raw(void) {
    return Filter_EMA(adc_buffer[1],&mq7_ema,0.15);
}
