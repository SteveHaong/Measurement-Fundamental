#ifndef SENSOR_RAW_H
#define SENSOR_RAW_H

#include <stdint.h>

void MQ7_Cycle_Manager(void);
uint16_t Get_MQ135_Raw(void);
uint16_t Get_MQ7_Current_Raw(void);

#endif
