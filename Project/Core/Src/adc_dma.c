#include "adc_dma.h"
#include "main.h"

extern ADC_HandleTypeDef hadc1;

uint16_t adc_buffer[3];

void ADC_DMA_Init(void) {
    HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, 3);
}
