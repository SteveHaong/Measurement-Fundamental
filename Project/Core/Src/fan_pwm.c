#include "fan_pwm.h"
#include "stm32f4xx.h"

void FanPWM_Init(void)
{

    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

    // 2. Cấu hình chân PA15 sang chức năng phụ (Alternate Function - AF1 cho TIM2)
    GPIOA->MODER &= ~(3U << (15 * 2)); // Xóa cấu hình cũ của chân PA15
    GPIOA->MODER |= (2U << (15 * 2));  // Chọn chế độ Alternate Function (10)

    GPIOA->AFR[1] &= ~(0xFU << ((15 - 8) * 4)); // Xóa AF cũ ở byte cao
    GPIOA->AFR[1] |= (1U << ((15 - 8) * 4));  // Chọn AF1 (TIM2) cho chân PA15

    // 3. Cấu hình chế độ PWM Mode 1 cho Channel 1 (Thanh ghi CCMR1)
    TIM2->CCMR1 &= ~TIM_CCMR1_OC1M;
    TIM2->CCMR1 |= (6U << TIM_CCMR1_OC1M_Pos); // 6: PWM mode 1
    TIM2->CCMR1 |= TIM_CCMR1_OC1PE;            // Bật Preload register cho CCR1

    // 4. Cho phép xuất ngõ ra ở Channel 1 (Thanh ghi CCER)
    TIM2->CCER |= TIM_CCER_CC1E;

    // 5. Thiết lập giá trị ARR (Auto-reload) để định nghĩa chu kỳ/tần số PWM
    // Giả sử tần số đặt là 999 để tính toán phần trăm cho dễ (0 - 1000)
    TIM2->ARR = 999;
    TIM2->PSC = 83;

    // 6. Cho phép Timer 2 hoạt động (Bit CEN trong CR1)
    TIM2->CR1 |= TIM_CR1_CEN;
}

void FanPWM_SetDuty(uint8_t percent)
{
    if (percent > 100) percent = 100;

    // Đọc giá trị ARR hiện tại
    uint32_t arr = TIM2->ARR;

    // Tính toán giá trị pulse (CCR1) dựa trên phần trăm
    uint32_t pulse = (arr + 1) * percent / 100;

    // Ghi thẳng vào thanh ghi CCR1 của TIM2 để đổi tốc độ quạt
    TIM2->CCR1 = pulse;
}
