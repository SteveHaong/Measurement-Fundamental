#include "periph_led_buzzer.h"
#include "stm32f4xx_hal.h"

void LedBuzzer_Init(void)
{
  /* GPIOs already configured in MX_GPIO_Init(); nothing additional required */
}

void Led_On(void)
{
  HAL_GPIO_WritePin(GPIOC, Led_Pin, GPIO_PIN_SET);
}

void Led_Off(void)
{
  HAL_GPIO_WritePin(GPIOC, Led_Pin, GPIO_PIN_RESET);
}

void Buzzer_Beep(uint32_t ms)
{
  HAL_GPIO_WritePin(GPIOC, Buzzer_Pin, GPIO_PIN_SET);
  HAL_Delay(ms);
  HAL_GPIO_WritePin(GPIOC, Buzzer_Pin, GPIO_PIN_RESET);
}
