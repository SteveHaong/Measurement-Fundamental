#include "temp_sensor.h"

// Định nghĩa các trạng thái của quá trình đọc cảm biến
typedef enum {
    SHT30_STATE_TRIGGER_MEAS,
    SHT30_STATE_WAIT_CONVERSION,
    SHT30_STATE_READ_DATA
} SHT30_State_t;

HAL_StatusTypeDef SHT30_Init(I2C_HandleTypeDef *hi2c) {
    /* Kiểm tra xem thiết bị có sẵn sàng trên bus I2C hay không */
    return HAL_I2C_IsDeviceReady(hi2c, SHT30_I2C_ADDR, 3, 100);
}

HAL_StatusTypeDef SHT30_Read_Temp_Humidity_NonBlocking(I2C_HandleTypeDef *hi2c, SHT30_Data_t *data) {
    static SHT30_State_t state = SHT30_STATE_TRIGGER_MEAS;
    static uint32_t timestamp = 0;
    HAL_StatusTypeDef status;

    uint8_t cmd[2] = {SHT30_CMD_MEAS_HIGH_H, SHT30_CMD_MEAS_HIGH_L};
    uint8_t rx_buf[6] = {0};

    switch (state) {
        case SHT30_STATE_TRIGGER_MEAS:
            /* 1. Phát lệnh yêu cầu đo xuống SHT30 */
            status = HAL_I2C_Master_Transmit(hi2c, SHT30_I2C_ADDR, cmd, 2, 10); // giảm timeout xuống 10ms
            if (status == HAL_OK) {
                timestamp = HAL_GetTick(); // Lưu lại thời điểm phát lệnh
                state = SHT30_STATE_WAIT_CONVERSION; // Chuyển sang trạng thái đợi
            }
            break;

        case SHT30_STATE_WAIT_CONVERSION:
            /* 2. Kiểm tra xem đã đủ 20ms chưa. Nếu chưa đủ, thoát ra làm việc khác */
            if (HAL_GetTick() - timestamp >= 20) {
                state = SHT30_STATE_READ_DATA; // Đủ thời gian rồi thì chuyển sang đọc dữ liệu
            }
            break;

        case SHT30_STATE_READ_DATA:
            /* 3. Đọc 6 bytes dữ liệu từ cảm biến */
            status = HAL_I2C_Master_Receive(hi2c, SHT30_I2C_ADDR, rx_buf, 6, 10);

            // Dù đọc thành công hay thất bại cũng quay về trạng thái ban đầu để chuẩn bị cho lần đo sau
            state = SHT30_STATE_TRIGGER_MEAS;

            if (status == HAL_OK) {
                /* 4. Tính toán giá trị vật lý */
                uint16_t raw_temp = (rx_buf[0] << 8) | rx_buf[1];
                uint16_t raw_humi = (rx_buf[3] << 8) | rx_buf[4];

                data->temperature = -45.0f + 175.0f * ((float)raw_temp / 65535.0f);
                data->humidity = 100.0f * ((float)raw_humi / 65535.0f);

                if (data->humidity > 100.0f) data->humidity = 100.0f;
                if (data->humidity < 0.0f)   data->humidity = 0.0f;

                return HAL_OK; // Chỉ trả về HAL_OK khi đã hoàn thành trọn vẹn chu trình đọc
            }
            break;
    }

    // Trả về HAL_BUSY hoặc HAL_ERROR để main biết là cảm biến đang trong quá trình xử lý, chưa có dữ liệu mới
    return HAL_BUSY;
}
