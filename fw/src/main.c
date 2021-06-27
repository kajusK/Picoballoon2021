/*
 * Copyright (C) 2021 Jakub Kaderka
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

/**
 * @file    app/main.c
 * @brief   Main file for deadbadger.cz picoballoon
 *
 * @addtogroup app
 *
 * @{
 */

#include <types.h>

#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/i2c.h>
#include <libopencm3/stm32/spi.h>

#include <hal/io.h>
#include <hal/adc.h>
#include <hal/i2c.h>
#include <hal/spi.h>
#include <hal/uart.h>
#include <hal/rtc.h>
#include <hal/exti.h>
#include <hal/power.h>
#include <hal/flash.h>
#include <utils/time.h>

#include <modules/log.h>
#include <modules/lora.h>
#include <drivers/gps.h>
#include <drivers/ms5607.h>
#include <drivers/si7020.h>
#include <drivers/rfm.h>

#include "config.h"

/** LoRa packet payload format */
typedef struct {
    uint32_t press_Pa;      /** Air pressure in deca Pascals (*10) */
    int16_t temp_dc;        /** Temperature in deci Celsius (/10) */
    int8_t core_temp_c;     /** MCU core temperature in degrees Celsius */
    uint16_t bat_mv;        /**< Voltage of the battery/supercap */
    uint16_t gps_alt_m;     /** GPS Altitude in meters */
    float lat;              /** Latitude in decimal degrees */
    float lon;              /** Longitude in decimal degrees */
    uint8_t loop_time_s;    /**< Time since wake up until packet creation */
} __attribute__((packed)) telemetry_packet_t;

/** Persistent data stored in the flash memory between consecutive runs */
typedef struct {
    uint32_t counter;       /**< LoRa Packet counter */
    rfm_lora_region_t region;   /**< RFM LoRa region used recently */
} persist_data_t;

/** Memory locations for persistent data defined in linker file */
extern const persist_data_t persist1;
extern const persist_data_t persist2;

static gps_desc_t gps_desc;
static ms5607_desc_t ms5607_desc;
static rfm_desc_t rfm_desc;

/** The Thing Network auth data */
static const uint8_t lora_dev_addr[4] = TTN_DEV_ADDR;
static const uint8_t lora_nwks_key[16] = TTN_NWKSKEY;
static const uint8_t lora_apps_key[16] = TTN_APPSKEY;

/**
 * Get LoRa region based on recent known location
 *
 * @param gps_lat   Latitude
 * @param gps_lon   Longitude
 * @return Selected LoRa region
 */
static rfm_lora_region_t App_GetRegion(nmea_float_t gps_lat,
        nmea_float_t gps_lon)
{
    rfm_lora_region_t region = RFM_REGION_EU863;
    int16_t lat = gps_lat.num / gps_lat.scale;
    int16_t lon = gps_lon.num / gps_lon.scale;

    if (lon > -180 && lon < -50) {
        region = RFM_REGION_US902;
        Log_Info("GPS", "Using US LoRa region");
    /* Australia, New Zealand */
    } else if  (lat > -50 && lat < -7 && lon > 100 && lon < 170) {
        region = RFM_REGION_AU915;
        Log_Info("GPS", "Using AU LoRa region");
    /* Japan, Malaysia, etc. */
    } else if (lon > 87 && lon < 180 && lat < 50) {
        region = RFM_REGION_AS920;
        Log_Info("GPS", "Using AS LoRa region");
    } else {
        Log_Info("GPS", "Using EU LoRa region");
    }

    return region;
}

/**
 * Save persistent data to flash memory
 *
 * @param counter   LoRa tx counter value
 * @param region    RFM LoRaWan region recently used
 */
static void App_SavePersistentData(uint32_t counter, rfm_lora_region_t region)
{
    persist_data_t data;
    uint32_t addr = (uint32_t)&persist1;

    if (persist1.counter == (uint32_t)-1) {
        addr = (uint32_t)&persist1;
    } else if (persist2.counter == (uint32_t)-1) {
        addr = (uint32_t)&persist2;
    } else if (persist1.counter > persist2.counter) {
        addr = (uint32_t)&persist2;
    } else {
        addr = (uint32_t)&persist1;
    }
    data.counter = counter;
    data.region = region;

    Flashd_WriteEnable();
    Flashd_ErasePage(addr);
    Flashd_Write(addr, (uint8_t *)&data, sizeof(data));
    Flashd_WriteDisable();
}

/**
 * Load saved persistent data
 *
 * @param [out] counter     Recently used LoRa TX counter value
 * @param [out] region      Recently used LoRa region
 */
static void App_LoadPersistentData(uint32_t *counter, rfm_lora_region_t *region)
{
    const persist_data_t *data;

    if (persist1.counter == (uint32_t)-1 && persist2.counter == (uint32_t)-1) {
        if (counter != NULL) {
            *counter = 0;
        }
        if (region != NULL) {
            *region = RFM_REGION_EU863;
        }
        return;
    } else if (persist1.counter == (uint32_t)-1) {
        data = &persist2;
    } else if (persist2.counter == (uint32_t)-1) {
        data = &persist1;
    } else if (persist1.counter > persist2.counter) {
        data = &persist1;
    } else {
        data = &persist2;
    }

    if (counter != NULL) {
        *counter = data->counter;
    }
    if (region != NULL) {
        *region = data->region;
    }
}

static void App_GpsOn(void)
{
    IOd_SetLine(LINE_GPS_ON, 1);
}

static void App_GpsOff(void)
{
    IOd_SetLine(LINE_GPS_ON, 0);
    Gps_Backup(&gps_desc);
}

/**
 * Wait for valid GPS data or timeout
 * @param timeout_s     Timeout in seconds for waiting for fix
 * @return True if have valid data, false if timed out
 */
static bool App_WaitGps(uint32_t timeout_s)
{
    uint32_t start_ts;

    Log_Info("App", "Waiting for GPS");

    EXTId_EnableEvent(PAD_GPS_FIX);
    if (IOd_GetLine(LINE_GPS_FIX) != 1) {
        /* Go to sleep until GPS fix is obtained or timeout */
        RTCd_SetAlarmInSeconds(timeout_s, NULL);
        Powerd_Stop();
    }
    EXTId_Disable(PAD_GPS_FIX);

    if (IOd_GetLine(LINE_GPS_FIX) == 0) {
        return false;
    }
    /* Wait for 1,5 second to get the whole NMEA data */
    start_ts = millis();
    while (Gps_Loop(&gps_desc) == NULL && (millis() - start_ts) < 1500) {
        ;
    }

    return Gps_Get(&gps_desc) != NULL;
}

/**
 * Get the time difference between start time and current time from RTC
 *
 * @return time in seconds
 */
static uint32_t time_elapsed_s(struct tm *tm_start)
{
    struct tm tm_now;
    time_t start;
    time_t now;

    RTCd_GetTime(&tm_now);
    start = mktime(tm_start);
    now = mktime(&tm_now);

    return (uint32_t)difftime(now, start);
}

static void App_Loop(void)
{
    telemetry_packet_t packet = {0};
    const gps_info_t *gps;
    int32_t temp_mdeg = 0;
    uint32_t press_Pa = 0;
    struct tm tm;
    uint32_t tx_counter = 0;
    rfm_lora_region_t region = RFM_REGION_EU863;
    bool use_gps = false;
    uint32_t gps_timeout_s = GPS_FIX_TIMEOUT_S;

    RTCd_GetTime(&tm);
    App_LoadPersistentData(&tx_counter, &region);
    if (tx_counter % TELEMETRY_GPS_SKIP == 0) {
        if (tx_counter % (TELEMETRY_GPS_SKIP*TELEMETRY_GPS_FULL_SKIP) == 0) {
            gps_timeout_s = GPS_FULL_TIMEOUT_S;
        }
        Log_Info("App", "Using GPS, timeout %d seconds", gps_timeout_s);
        App_GpsOn();
        use_gps = true;
    }

    Adcd_UpdateVdda();
    packet.bat_mv = Adcd_ReadMv(CHN_VBATT);
    packet.core_temp_c = Adcd_ReadTempDegC();
    Adcd_Sleep();

    if (!MS5607_Read(&ms5607_desc, MS5607_OSR1024, &press_Pa, &temp_mdeg)) {
        packet.press_Pa = 0;
        packet.temp_dc = 0;
    } else {
        packet.press_Pa = press_Pa;
        packet.temp_dc = temp_mdeg / 100;
    }

    /* wait for fix */
    if (use_gps && !App_WaitGps(gps_timeout_s)) {
        Log_Info("App", "Failed to get GPS position");
    }
    gps = Gps_Get(&gps_desc);
    App_GpsOff();

    if (gps != NULL) {
        Log_Info("App", "Got GPS");
        region = App_GetRegion(gps->lat, gps->lon);
        packet.gps_alt_m = gps->altitude_dm/10;
        packet.lat = ((float) gps->lat.num) / gps->lat.scale;
        packet.lon = ((float) gps->lon.num) / gps->lon.scale;
    } else {
        if (use_gps) {
            /* Failed to obtain GPS fix, get default region */
            region = RFM_REGION_EU863;
        }
        packet.gps_alt_m = 0;
        packet.lat = 0;
        packet.lon = 0;
    }

    packet.loop_time_s = time_elapsed_s(&tm);

    Log_Info(NULL, "TX counter %d", tx_counter);
    Log_Info(NULL, "Pressure %d Pa", packet.press_Pa);
    Log_Info(NULL, "Temperature %d C", packet.temp_dc/10);
    Log_Info(NULL, "Core temp %d C", packet.core_temp_c);
    Log_Info(NULL, "Battery voltage %d mV", packet.bat_mv);
    Log_Info(NULL, "Latitude %f", packet.lat);
    Log_Info(NULL, "Longitude %f", packet.lon);
    Log_Info(NULL, "GPS alt %d m", packet.gps_alt_m);
    Log_Info(NULL, "Loop time %d s", packet.loop_time_s);
    Log_Info(NULL, "Sending data");

    /* RFM module initialization postponed here to save power */
    RFM_LoraInit(&rfm_desc);
    RFM_SetLoraParams(&rfm_desc, RFM_BW_125k, RFM_SF_10);
    RFM_SetPowerDBm(&rfm_desc, 17);
    RFM_SetLoraRegion(&rfm_desc, region);

    /* Save LoRa tx counter + 1 (in case, power dies before saving) */
    Lora_SetCounters(0, tx_counter);
    App_SavePersistentData(tx_counter+1, region);

    if (!Lora_Send((uint8_t *) &packet, sizeof(packet))) {
        Log_Error(NULL, "Failed to send data over LoRaWan!");
    }
    Log_Info(NULL, "Powering off");
    RFM_PowerOff(&rfm_desc);
}

static void lora_send_cb(const uint8_t *data, size_t len)
{
    RFM_LoraSend(&rfm_desc, data, len);
}

int main(void)
{
    /* Initialize clock system, IO pins and systick */
    IOd_Init();
    Time_Init();

    /* early init - debug output */
    UARTd_Init(USART_DEBUG_TX, 115200);
    Log_Init(USART_DEBUG_TX);
    Log_Info(NULL, "PicoBalloon Challenge 2021");
    Log_Info(NULL, "Launched from Brno Observatory, Czech Republic");
    Log_Info(NULL, "bal.eadbadger.cz");

    I2Cd_Init(1, false);
    SPId_Init(1, SPID_PRESC_2, SPI_MODE_0);
    RTCd_Init(false);
    Adcd_Init();

    UARTd_Init(USART_GPS_TXD, 9600);
    Gps_Init(&gps_desc, USART_GPS_TXD);

    if (!MS5607_Init(&ms5607_desc, 1, MS5607_ADDR_1)) {
        Log_Error(NULL, "MS5607 pressure sensor not responding");
    }

    if (!RFM_Init(&rfm_desc, 1, LINE_RFM_CS, LINE_RFM_RESET, LINE_RFM_IO0)) {
        Log_Error(NULL, "RFM module not responding!");
        delay_ms(1000);
        /* RFM module is crucial, it makes no sense to continue without it */
        Powerd_Reboot();
    }
    Lora_InitAbp(lora_send_cb);
    Lora_SetAbpKeys(lora_dev_addr, lora_nwks_key, lora_apps_key);

    EXTId_SetMux(LINE_GPS_FIX);
    EXTId_SetEdge(PAD_GPS_FIX, EXTID_RISING);

    Log_Info(NULL, "System initialized, running main loop");
    Log_SetLevel(LOG_ERROR);

    /* ================ TODO ================ */
    /* debugging purposes only, remove for production */
    Log_SetLevel(LOG_DEBUG);
    delay_ms(5000);
    /* ================ TODO ================ */

    while (1) {
        /* set alarm first to ensure precise periods */
        RTCd_SetAlarmInSeconds(TELEMETRY_PERIOD_MIN*60, NULL);
        App_Loop();

        Adcd_Sleep();
        App_GpsOff();
        RFM_PowerOff(&rfm_desc);
        Powerd_Off();
        Log_Error(NULL, "Failed to power off the MCU!");
        delay_ms(1000);
        Powerd_Reboot();
    }
}

/** @} */
