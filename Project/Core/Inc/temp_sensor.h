#ifndef __TEMP_SENSOR_H
#define __TEMP_SENSOR_H

#include "stm32f4xx_hal.h"

#define SHT30_I2C_ADDR          (0x44 << 1)

#define SHT30_CMD_MEAS_HIGH_H   0x24
#define SHT30_CMD_MEAS_HIGH_L   0x00

typedef struct {
    float temperature;
    float humidity;
} SHT30_Data_t;

HAL_StatusTypeDef SHT30_Init(I2C_HandleTypeDef *hi2c);
HAL_StatusTypeDef SHT30_Read_Temp_Humidity(I2C_HandleTypeDef *hi2c, SHT30_Data_t *data);
HAL_StatusTypeDef SHT30_Read_Temp_Humidity_NonBlocking(I2C_HandleTypeDef *hi2c, SHT30_Data_t *data);
#endif /* __TEMP_SENSOR_H */
