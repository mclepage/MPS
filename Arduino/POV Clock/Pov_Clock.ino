#include <SPI.h>

const unsigned long pixel_count = 120;
const unsigned long pixel_half = pixel_count/2;
const unsigned long pixel_quarter = pixel_count/4;
const unsigned long pixel_threequarter=pixel_quarter + pixel_half;

const int lePin4094 = 9;
const int hour_red = 3;
const int hour_blue = 2;
const int minute_red = 7;
const int minute_blue = 6;
const int second_pin = A3;
const int hall_pin= A4;
const int out_IR = A5;
const int mid_IR = A6;
const int in_IR = A7;

int minute_selected = 0;
int hour_selected = 0;
int rot_count = 0;

int cur_hall = -1;
int new_hall;
int calibrated = 0;

int last_IR=0;

unsigned long time_zero;
unsigned long rev_time;
unsigned long step_time;
unsigned long last_start;
unsigned long run_time = 0;
unsigned long loop_start = 0;
int time;
int to_next_tic = 10;
int to_next_large_tic = 0;

int cur_pixel;
int cur_hour_hand = pixel_threequarter+20; // Super arbitrary.
int cur_minute_hand = 10;
int cur_second_hand = 0;

char spiValue=0xFF;


unsigned long next_pxl_time;

const int pixels_in_hour = pixel_count/12;
const int pixels_in_major_hour = pixel_count/4;
// Pixel locations for the start of number prints
const int start_twelve=pixels_in_hour-7; //4 for the offcentering of the digits, 5 for the 10pxl delay around magnets.
const int start_nine=start_twelve + pixels_in_major_hour+3; /// THIS OFFSET MATTERS
int start_six=start_nine + pixels_in_major_hour-5;
const int start_three=start_six + pixels_in_major_hour+5;

int noon_loc = pixels_in_hour-5;
int mag_passes = 0;

void setup()
{
  SPI.setBitOrder(MSBFIRST);
  SPI.setDataMode(SPI_MODE0);
  SPI.setClockDivider(SPI_CLOCK_DIV4);
  SPI.begin();
  pinMode(lePin4094, OUTPUT);
  digitalWrite(lePin4094, LOW);
  SPI.transfer(spiValue);
  digitalWrite(lePin4094, HIGH);
  digitalWrite(lePin4094, LOW);
  for (int j=2; j<=13;j++)
  {
    if(j!=9 && j!=11 && j!=13)
    {
      pinMode(j, OUTPUT);
      digitalWrite(j, HIGH);
    }
  }
  pinMode(A0, OUTPUT);
  digitalWrite(A0, HIGH);
  pinMode(A1, OUTPUT);
  digitalWrite(A1, HIGH);
  pinMode(A2, OUTPUT);
  digitalWrite(A2, HIGH);
  pinMode(A3, OUTPUT);
  digitalWrite(A3, HIGH);
  
  
  pinMode(out_IR, INPUT);
  pinMode(mid_IR, INPUT);
  pinMode(in_IR, INPUT);
  pinMode(hall_pin, INPUT);
  time_zero = millis();
  last_start = micros();  
}

void loop()
{
  
  loop_start=micros();
  new_hall = digitalRead(hall_pin);
  if (new_hall == 1 && cur_hall == 0)
  {
    if (minute_selected ==1 || hour_selected==1)
    {
      rot_count+=1;
      if (rot_count>30)
      {
        minute_selected = 0;
        hour_selected = 0;
        rot_count=0;
      }
    }
    calibrated = 1;
    cur_pixel = 0;
    rev_time = (loop_start-last_start);
    last_start = loop_start;
    step_time = rev_time/pixel_half;
    to_next_tic = 10;
    to_next_large_tic = 10; // Initial offsets of hours
    start_six = -1000;
  }
  if (new_hall == 0 && cur_hall == 1 && calibrated==1)
  {
    cur_pixel = pixel_half;
    rev_time = (loop_start-last_start);
    last_start = loop_start;
    step_time = rev_time/pixel_half;
    to_next_tic = 10;
    to_next_large_tic = 10;
    start_six=start_nine + pixels_in_major_hour;
  }
  cur_hall = new_hall;  
  if (calibrated==0)
  {  
    return;  
  }
  
  run_time += micros()-loop_start;
  
  ///// ----- Start delay control code -----
  next_pxl_time = micros()+step_time-run_time-50;  //Hard recalibration here.
  while(micros()<(next_pxl_time))
  {
    if (cur_hall != digitalRead(hall_pin))
    { 
      return; 
    }
  }
  loop_start=micros();
  
    
  cur_pixel = cur_pixel+1;
  
  ///// ----- Start Time Code -----
  time = millis()-time_zero;
  if (time>=1000)
  {
    incrementTime();
    time_zero = millis();
  }
  
  
  
  if(analogRead(mid_IR)<=905)
  {
    if(cur_pixel == cur_hour_hand)
    {
      hour_selected = 1;
      minute_selected = 0;
    }
    else if(cur_pixel == cur_minute_hand)
    {
      hour_selected = 0;
      minute_selected = 1;
    }
    if(hour_selected)
    {
      cur_hour_hand = cur_pixel;
    }
    else if( minute_selected)
    {
      cur_minute_hand = cur_pixel;
    }
  }
  
  ///// ----- Start Hand Code -----
  if (cur_pixel == cur_hour_hand)
  {
    hourBlueOn();
    if (hour_selected)
    {
      hourRedOn();
    }
  }
  if (cur_pixel == cur_minute_hand)
  {
    minuteBlueOn();
    hourBlueOn();
    if (minute_selected)
    {
      hourRedOn();
      minuteRedOn();
    }
  }
  else
  {
    minuteOff();
  }
  if(cur_pixel != cur_minute_hand && cur_pixel != cur_hour_hand)
  {
    hourOff();
  }

  if (cur_pixel == cur_second_hand)
  {
    secondOn();
  }
  else
  {
    secondOff();
  }
  

  ///// ----- Start Hour Tic code -----
  digitalWrite(lePin4094, LOW); 
//  pixelOn(5, 'g');
//  pixelOn(4, 't');
//  pixelOn(3, 'b');
//  pixelOn(2, 'p');
//  pixelOn(1, 'y');
  
  if (to_next_tic == 0)
  {
    if (to_next_large_tic>0)
    {    
      //smallTic();
    }
    else
    {
      to_next_large_tic = pixels_in_major_hour;
    }

    to_next_tic = pixels_in_hour;
  }
  else
  {
   // smallTicOff();
  }
  
  to_next_large_tic -=1;
  to_next_tic -=1;
  
  ///// ----- Start Major Hour Print Code -----
  if (cur_pixel ==start_twelve)
  {
    pixelOn(1, 'y');
    pixelOn(3, 'y');
    pixelOn(2, 'y');
    pixelOn(5, 'y');
  }
  if (cur_pixel ==start_twelve+1  )
  {
    pixelOff(2, 'y');
  }
  if (cur_pixel ==start_twelve+5)
  {
    pixelOn(4, 'y');
  }
  if (cur_pixel == start_twelve+6)
  {
    digitOff('y');
  }
  if (cur_pixel == start_twelve+9)
  {
    digitOn('y');
  }
  if (cur_pixel == start_twelve+10)
  {
    digitOff('y');
  }
  
  
  if (cur_pixel ==start_nine)
  {  
      pixelOn(1, 'b');
      pixelOn(2, 'b');
      pixelOn(3, 'b');
  }
  if (cur_pixel ==start_nine+1)
  {
    pixelOff(2, 'b');
  }
  if (cur_pixel ==start_nine+4)
  {
    pixelOn(2, 'b');
  }
  if (cur_pixel == start_nine+5)
  { 
    pixelOff(1, 'b');
    pixelOff(2, 'b');
  }
  if (cur_pixel == start_nine+9)
  {
    pixelOn(1, 'b');
    pixelOn(2, 'b');
  }
  if (cur_pixel == start_nine+10)
  {    digitOff('b');   }
  
  
  
  if (cur_pixel == start_six)
  {
    digitOn('w');
  }
  if (cur_pixel == start_six+1)
  {
    pixelOff(4, 'w');
    pixelOff(2, 'w');
  }
  if (cur_pixel == start_six+5)
  {
    pixelOn(2, 'w');
  }
  if (cur_pixel == start_six+6)
  {
    digitOff('w');
  }
  
  if (cur_pixel ==start_three+1)
  {
    pixelOn(3, 'w');
    pixelOn(2, 'w');
    pixelOn(1, 'w');
  }
  if (cur_pixel ==start_three+2)
  {
    pixelOff(2, 'w');
    pixelOff(3, 'w');
  }
  if (cur_pixel ==start_three+6)
  {
    pixelOn(3, 'w');
    pixelOn(2, 'w');
  }
  if (cur_pixel == start_three+7)
  { 
    pixelOff(2, 'w');
    pixelOff(3, 'w');
  }
  if (cur_pixel == start_three+11)
  {
    pixelOn(3, 'w');
    pixelOn(2, 'w');
  }
  if (cur_pixel == start_three+12)
  {    digitOff('w');   }
  
  
  
  digitalWrite(lePin4094, LOW);
  SPI.transfer(spiValue);
  digitalWrite(lePin4094, HIGH);
  run_time =micros()-loop_start;
}

void smallTic()
{
  pixelOn(1, 'y');
  pixelOn(2, 'y');
}

void smallTicOff()
{
  pixelOff(1, 'y');
  pixelOff(2, 'y');
}

void digitOn(char c)
{
  for (int j=1; j<=5; j++)
  {
    pixelOn(j, c);
  }
}

void digitOff(char c)
{
  for (int j=1; j<=5; j++)
  {
    pixelOff(j, c);
  }
}

void hourRedOn()
{
  digitalWrite(hour_red, LOW);
}

void hourBlueOn()
{
  digitalWrite(hour_blue, LOW);
}

void hourPurpleOn()
{
  digitalWrite(hour_red, LOW);
  digitalWrite(hour_blue, LOW);
}

void hourOff()
{
  digitalWrite(hour_blue, HIGH);
  digitalWrite(hour_red, HIGH);
}


void minuteRedOn()
{
  digitalWrite(minute_red, LOW);
}

void minuteBlueOn()
{
  digitalWrite(minute_blue, LOW);
}

void minutePurpleOn()
{
  digitalWrite(minute_blue, LOW);
  digitalWrite(minute_red, LOW);
}

void minuteOff()
{
  digitalWrite(minute_blue, HIGH);
  digitalWrite(minute_red, HIGH);
}


void secondOn()
{
  digitalWrite(second_pin, LOW);

}
void secondOff()
{
  digitalWrite(second_pin, HIGH);
}


void pixelOn(int num, char color)
{
  if (color == 'r' || color == 'y' || color == 'p' || color == 'w')
  {
    switch (num)
    {
      case 1:
        spiValue=spiValue & (0xFD);
        break;
      case 2:
        spiValue=spiValue & (0xFE);
        break;
      case 3:
        digitalWrite(8, LOW);
        break;
      case 4:
        digitalWrite(5, LOW);
        break;
      case 5:
        digitalWrite(4, LOW);
        break;
      default:
        break;
    }
  }
  if (color == 'g' || color == 'y' || color == 't' || color == 'w')
  {
    switch (num)
    {
      case 1:
        spiValue=spiValue & (0xDF);
        break;
      case 2:
        spiValue=spiValue & (0xEF);
        break;
      case 3:
        spiValue=spiValue & (0xF7);
        break;
      case 4:
        spiValue=spiValue & (0xFB);
        break;
      case 5:
        spiValue=spiValue & (0xBF);
        break;
      default:
        break;
    }
  }
  if (color == 'b' || color == 'p' || color == 't' || color == 'w')
  {
    switch (num)
    {
      case 1:
        digitalWrite(A2, LOW);
        break;
      case 2:
        digitalWrite(A1, LOW);
        break;
      case 3:
        digitalWrite(A0, LOW);
        break;
      case 4:
        spiValue=spiValue & (0x7F);
        break;
      case 5:
        digitalWrite(10, LOW);
        break;
      default:
        break;
    }
  }
}

void pixelOff(int num, char color)
{
  if (color == 'r'  || color == 'p' || color == 'y' || color == 'w')
  {
    switch (num)
    {
      case 1:
        spiValue=spiValue | ~(0xFD);
        break;
      case 2:
        spiValue=spiValue | ~(0xFE);
        break;
      case 3:
        digitalWrite(8, HIGH);
        break;
      case 4:
        digitalWrite(5, HIGH);
        break;
      case 5:
        digitalWrite(4, HIGH);
        break;
      default:
        break;
    }
  }
  if (color == 'g' || color == 'y' || color == 't' || color == 'w')
  {
    switch (num)
    {
      case 1:
        spiValue=spiValue | ~(0xDF);
        break;
      case 2:
        spiValue=spiValue | ~(0xEF);
        break;
      case 3:
        spiValue=spiValue | ~(0xF7);
        break;
      case 4:
        spiValue=spiValue | ~(0xFB);
        break;
      case 5:
        spiValue=spiValue | ~(0xBF);
        break;
      default:
        break;
    }
  }
  if (color == 'b' || color == 'p' || color == 't' || color == 'w')
  {
    switch (num)
    {
      case 1:
        digitalWrite(A2, HIGH);
        break;
      case 2:
        digitalWrite(A1, HIGH);
        break;
      case 3:
        digitalWrite(A0, HIGH);
        break;
      case 4:
        spiValue=spiValue | ~(0x7F);
        break;
      case 5:
        digitalWrite(10, HIGH);
        break;
      default:
        break;
    }
  }
}

void incrementTime()
{
  cur_second_hand -=2;
  if (cur_second_hand<=0)
  {
    cur_second_hand=pixel_count;
    cur_minute_hand-=2;
    if (cur_minute_hand<=0)
    {
      cur_minute_hand=pixel_count;
      cur_hour_hand-=10;
      if (cur_hour_hand<=0)
      {
        cur_hour_hand=pixel_count;
      }
    }
  }
}

