#ifndef __TEMP_SENSOR_H
#define __TEMP_SENSOR_H

#include "stm32f4xx_hal.h"

/* Địa chỉ I2C mặc định của SHT30 (Trạng thái chân ADDR nối GND hoặc bỏ trống) */
/* Trong thư viện HAL, địa chỉ 7-bit cần dịch trái 1 bit: 0x44 << 1 = 0x88 */
#define SHT30_I2C_ADDR          (0x44 << 1)

/* Lệnh đo ở chế độ Single Shot (Độ chính xác cao - High Stretch disabled) */
#define SHT30_CMD_MEAS_HIGH_H   0x24
#define SHT30_CMD_MEAS_HIGH_L   0x00

/* Khai báo cấu trúc dữ liệu trả về */
typedef struct {
    float temperature;
    float humidity;
} SHT30_Data_t;

/**
 * @brief  Khởi tạo hoặc kiểm tra xem cảm biến SHT30 có phản hồi không
 * @param  hi2c: Con trỏ tới cấu hình I2C của HAL (ví dụ: &hi2c1)
 * @retval HAL_StatusTypeDef (HAL_OK nếu thành công)
 */
HAL_StatusTypeDef SHT30_Init(I2C_HandleTypeDef *hi2c);

/**
 * @brief  Đọc dữ liệu và tính toán sơ bộ nhiệt độ, độ ẩm từ SHT30
 * @param  hi2c: Con trỏ tới cấu hình I2C của HAL
 * @param  data: Con trỏ tới struct chứa kết quả trả về
 * @retval HAL_StatusTypeDef (HAL_OK nếu đọc và tính toán thành công)
 */
HAL_StatusTypeDef SHT30_Read_Temp_Humidity(I2C_HandleTypeDef *hi2c, SHT30_Data_t *data);
HAL_StatusTypeDef SHT30_Read_Temp_Humidity_NonBlocking(I2C_HandleTypeDef *hi2c, SHT30_Data_t *data);
#endif /* __TEMP_SENSOR_H */
