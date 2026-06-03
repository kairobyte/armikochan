/*******************************************************************************
 * FILENAME:    as5600_test.ino
 * DESCRIPTION: Use this to test AS5600 encoder individually
 * AUTHOR:      Sushant Thakur
 * DATE:        202-05-29
 * VERSION:     1.0.0
 * 
 * COPYRIGHT:   Copyright (c) 2026 Sushant Thakur. All rights reserved.
 ******************************************************************************/

// ============================================================================
// File: as5600_test.ino
// Auto-added section markers and high-level comments
// ============================================================================

// ====== Includes ======
#include <AS5600.h>
#include "freertos/semphr.h"


AS5600 as5600;   //  use default Wire


// Function: setup

// ====== Functions ======
void setup()
{
  // while(!Serial);
  Serial.begin(115200);
  Serial.println();
  Serial.println(__FILE__);
  Serial.print("AS5600_LIB_VERSION: ");
  Serial.println(AS5600_LIB_VERSION);
  Serial.println();

  Wire.begin(15,16);
  Wire.setClock(50000); // can be set as low as 1k but is very slow 

  as5600.begin(4);  //  set direction pin.
  as5600.setDirection(AS5600_CLOCK_WISE);  //  default, just be explicit.

  Serial.println(as5600.getAddress());

  //  as5600.setAddress(0x40);  //  AS5600L only

// ====== Globals ======
  int b = as5600.isConnected();
  Serial.print("Connect: ");
  Serial.println(b);

  delay(1000);
}


// Function: loop

void loop()
{
  static uint32_t lastTime = 0;

  //  set initial position
  as5600.getCumulativePosition();

  //  update every 100 ms
  //  should be enough up to ~200 RPM
  if (millis() - lastTime >= 100)
  {
    lastTime = millis();
    Serial.print(as5600.getCumulativePosition());
    Serial.print("\t");
    Serial.println(as5600.getRevolutions());
  }

  //  just to show how reset can be used
  if (as5600.getRevolutions() >= 10)
  {
    as5600.resetPosition();
  }
}


//  -- END OF FILE --