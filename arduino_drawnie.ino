#include "BasicStepperDriver.h"
#include "Servo.h"

/****************************************************
   stepper variables
*/

/* Motor steps per revolution: 200 steps or 1.8 degrees/step */
#define MOTOR_STEPS 200
#define RPM 120
float PULLEY_MM_PER_REV = 12*PI; //diameter of our pulley wheel is 12 mm

/* Since microstepping is set externally, make sure this matches the selected mode
   If it doesn't, the motor will move at a different RPM than chosen
   1=full step, 2=half step etc. */
#define MICROSTEPS 1

/* Mapping Arduino pins to stepper motors control pins: This mapping corresponds to RepRap Arduino Mega Pololu shield (for Arduino 2560)
*/
//motor left
#define STEP_1 A0
#define DIR_1 A1
#define ENABLE_1 38

//motor right
#define STEP_2 A6
#define DIR_2 A7
#define ENABLE_2 A2

#define sdelay 15//100
#define step_angle 1.8 

// 2-wire basic config, microstepping is hardwired on the driver
BasicStepperDriver stepperLeft(MOTOR_STEPS, DIR_1, STEP_1);
BasicStepperDriver stepperRight(MOTOR_STEPS, DIR_2, STEP_2);

//servo motor
Servo myservo;

String inData;
String motor;
String steps;
String third;

unsigned long time;

/* servo commands */
const int servoUp = 0; 
const int servoDown = 90;

/* commands for arduino come as 1,0 or -1,1
   where first number identifies the motor 
   and 2nd is the number of steps */
const int leftMotor = 0;
const int rightMotor = 1;
const int servoMotor = 2;

//make sure the "com port" value in python code is matching the "Port" your arduino is connected to
void setup() 
   { 
      Serial.begin(9600); 
      //Serial.println("Connection established...");

      //Set motors RPM
      stepperLeft.begin(RPM, MICROSTEPS);
      stepperRight.begin(RPM, MICROSTEPS);
    
      //init servo motor
      myservo.attach(3);
    
      pinMode(ENABLE_1, OUTPUT);
      pinMode(ENABLE_2, OUTPUT);
    
      digitalWrite(ENABLE_1, HIGH);
      digitalWrite(ENABLE_2, HIGH);
   }
 
void loop() 
   {
     while (Serial.available())
        {
          motor  = Serial.readStringUntil(',');
          Serial.read(); //next character is comma, so skip it using this
          steps = Serial.readStringUntil('\0');
          switch (motor.toInt()) {
            case leftMotor:
              // statements
              digitalWrite(ENABLE_1, LOW);
              delay(sdelay);
              stepperLeft.rotate(step_angle*steps.toInt());
              delay(sdelay);
              digitalWrite(ENABLE_1, HIGH);
              break;
            case rightMotor:
              digitalWrite(ENABLE_2, LOW);
              delay(sdelay);
              stepperRight.rotate((-1)*step_angle*steps.toInt());
              delay(sdelay);
              digitalWrite(ENABLE_2, HIGH);
              break;
            case servoMotor: 
              if (steps.toInt()==0) {
                myservo.write(servoDown);
              } else if (steps.toInt()==1) {
                myservo.write(servoUp);
              }
              delay(sdelay);   
              break;
        }
     }
   }
     //Serial.print("MOTOR : ");
     //Serial.println(motor);
     //Serial.print("STEPS : ");
     //Serial.println(steps);
     //delay(10);
