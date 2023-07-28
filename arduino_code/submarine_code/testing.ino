#include <stdio.h>



void setup() {
  // put your setup code here, to run once:

}


// Functions
void setSyringes(unsigned char) {

}

void setMainMotor(unsigned char) {

}

void setBowThrusters(unsigned char) {

}

void setPitchServo(unsigned char) {

}

void setYawServo(unsigned char) {

}

void setDepth(unsigned char) {

}

void setAngle(unsigned char) {

}

void setGrabber(unsigned char) {

}

void setLights(unsigned char) {

}


void loop() {
    // Array of function pointers
    void (*functionArray[9])() = {
        setSyringes,
        setMainMotor,
        setBowThrusters,
        setPitchServo,
        setYawServo,
        setDepth,
        setAngle,
        setGrabber,
        setLights
    };

    // Call the functions using the function pointers
    for (int i=0; i<9; i++) {
        functionArray[i]();
    }

    return 0;
}
