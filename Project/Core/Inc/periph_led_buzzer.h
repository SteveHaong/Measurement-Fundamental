/*
 * periph_led_buzzer.h
 * Simple LED and Buzzer helper API
 */
#ifndef PERIPH_LED_BUZZER_H
#define PERIPH_LED_BUZZER_H

#include "main.h"

void LedBuzzer_Init(void);
void Led_On(void);
void Led_Off(void);
void Buzzer_Beep(uint32_t ms);

#endif // PERIPH_LED_BUZZER_H
