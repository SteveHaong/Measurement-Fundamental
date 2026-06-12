#include "sensor_raw.h"
#include "adc_dma.h"
#include "main.h"

static uint16_t timer_mq7_A = 0;
static uint16_t timer_mq7_B = 75;
static uint16_t final_mq7_value = 0;

uint16_t Get_MQ135_Raw(void) {
    return adc_buffer[0]; // Vẫn đọc từ mảng DMA mang về
}

void MQ7_Cycle_Manager(void) {
    // --- 1. QUẢN LÝ CON MQ7_A ---
    timer_mq7_A++;
    if (timer_mq7_A >= 150) timer_mq7_A = 0;

    if (timer_mq7_A < 60) {
        // [Giai đoạn sấy 5V]: Kích HIGH chân PB0 bằng thanh ghi BSRR
        GPIOB->BSRR = (1 << 0);
    } else {
        // [Giai đoạn đo 1.4V]: Hạ LOW chân PB0 (Bit BR0 nằm ở vị trí dịch 16)
        GPIOB->BSRR = (1 << 16);

        if (timer_mq7_A == 148) {
            final_mq7_value = adc_buffer[1];
        }
    }

    // --- 2. QUẢN LÝ CON MQ7_B ---
    timer_mq7_B++;
    if (timer_mq7_B >= 150) timer_mq7_B = 0;

    if (timer_mq7_B < 60) {
        // [Giai đoạn sấy 5V]: Kích HIGH chân PB1
        GPIOB->BSRR = (1 << 1);
    } else {
        // [Giai đoạn đo 1.4V]: Hạ LOW chân PB1
        GPIOB->BSRR = (1 << 17);

        if (timer_mq7_B == 148) {
            final_mq7_value = adc_buffer[2];
        }
    }
}

uint16_t Get_MQ7_Current_Raw(void) {
    return final_mq7_value;
}
