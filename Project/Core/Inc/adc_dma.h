#ifndef ADC_DMA_H
#define ADC_DMA_H

#include "main.h"

// Mảng 3 phần tử: [0]=MQ135, [1]=MQ7_A, [2]=MQ7_B
extern uint16_t adc_buffer[3];

void ADC_DMA_Init(void);

#endif
