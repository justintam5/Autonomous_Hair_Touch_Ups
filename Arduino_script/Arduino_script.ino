#include "I2Cdev.h"
#include "MPU6050.h"
#include <SoftwareSerial.h>

SoftwareSerial hc06(5,4);

// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif


MPU6050 accelgyro;
//MPU6050 accelgyro(0x69); // <-- use for AD0 high

int16_t ax, ay, az;
int16_t gx, gy, gz;

#define OUTPUT_READABLE_ACCELGYRO

//potentially faster implemenatation
//#define OUTPUT_BINARY_ACCELGYRO


#define LED_PIN 13
bool blinkState = false;

void setup() {
    // join I2C bus (I2Cdev library doesn't do this automatically)
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif

    // initialize serial communication

    Serial.begin(57600);
    hc06.begin(57600);

    // initialize device
    accelgyro.initialize();
    
    accelgyro.setXGyroOffset(220);
    accelgyro.setYGyroOffset(76);
    accelgyro.setZGyroOffset(-85);

    pinMode(LED_PIN, OUTPUT);
}

void loop() {

    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    #ifdef OUTPUT_READABLE_ACCELGYRO
        hc06.print(ax); hc06.print(",");
        hc06.print(ay); hc06.print(",");
        hc06.print(az); hc06.print(",");
        hc06.print(gx); hc06.print(",");
        hc06.print(gy); hc06.print(",");
        hc06.print(gz); hc06.print(",");
        hc06.println(micros());
    #endif

    // blink LED to indicate activity
    blinkState = !blinkState;
    digitalWrite(LED_PIN, blinkState);
}
