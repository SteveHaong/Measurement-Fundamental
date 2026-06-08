#include "fan_pwm.h"
#include "stm32f4xx_hal.h"

static TIM_HandleTypeDef *pwm_htim = NULL;
static const uint32_t pwm_channel = TIM_CHANNEL_1;

void FanPWM_Init(TIM_HandleTypeDef *htim)
{
  pwm_htim = htim;
  HAL_TIM_PWM_Start(pwm_htim, pwm_channel);
}

void FanPWM_SetDuty(uint8_t percent)
{
  if (pwm_htim == NULL) return;
  if (percent > 100) percent = 100;
  uint32_t arr = pwm_htim->Instance->ARR;
  uint32_t pulse = (arr + 1) * percent / 100;
  __HAL_TIM_SET_COMPARE(pwm_htim, pwm_channel, pulse);
}
