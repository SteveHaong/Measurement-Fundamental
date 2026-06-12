/*
 * fan_pwm.h
 * Simple PWM fan control using a timer channel
 */
#ifndef FAN_PWM_H
#define FAN_PWM_H

#include "main.h"

void FanPWM_Init(void);
void FanPWM_SetDuty(uint8_t percent);

#endif // FAN_PWM_H
