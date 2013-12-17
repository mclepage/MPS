/*
  @author Matthew Lepage, mcl82
*/

const int redPin = 9;
const int bluePin = 5;
const int greenPin = 6;
const int dialPin = 6;
const int flexPin = 4;
const int lightPin = 3;
const int buttonPin = 12;
const int speakerPin = 11;

int playerScore;
int playerStrikes;
int rounds;
int tempo;
int elapsed;

void setup(){
  Serial.begin(9600);
  pinMode(redPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(flexPin, INPUT);
  pinMode(dialPin, INPUT);
  pinMode(buttonPin, INPUT);
  startGame();
}

// Starts a new game, resetting all values to their defaults.
void startGame()
{
  tempo = 1000;
  rounds = 0;
  playerScore = 0;
  playerStrikes = 0;
  startTone();
  digitalWrite(greenPin, HIGH);
  waitForButton();
  tick();
  delay(tempo);
  tick();
  delay(tempo);
  tick();
  delay(tempo);
  tick();
  delay(tempo);
}

void loop(){
  boolean success = 0;
  // Randomly decides which action to ask for.
  switch(random(1, 5))
  {
    case 1:
      success = flickIt();
      break;
    case 2:
      success = bopIt();
      break;
    case 3:
      success = twistIt();
      break;
    case 4:
      success = lightIt();
      break;
  }
  if (success)
  {
    playerScore +=1;
  }
  else
  {
    playerStrikes+=1;
  }
  
  // The number of failures made is reflected in the LED state.
  switch(playerStrikes)
  {
    case 0:
      digitalWrite(greenPin, HIGH);
      break;
    case 1:
      digitalWrite(bluePin, HIGH);
      break;
    case 2:
      digitalWrite(greenPin, LOW);
      break;
    case 3:
      digitalWrite(redPin, HIGH);
      break;
    case 4:
      digitalWrite(bluePin, LOW);
      break;
  }
  if (playerStrikes>4) // in an If statement 
  {
    failTone();
    playScore();
    digitalWrite(redPin, LOW);
    startGame();
  }
  else
  {
    rounds+=1;
    if (rounds%5==0)
    {
      tempo-=100;
      if (tempo>400)
      {
        nextRoundTone();
        tick();
        delay(tempo);
        tick();
        delay(tempo);
        tick();
        delay(tempo);
        tick();
        delay(tempo);
      }
      else
      {
        victoryTone();
        digitalWrite(redPin, LOW);
        digitalWrite(greenPin, LOW);
        digitalWrite(bluePin, LOW);
        startGame();
      }
    }
  }
}

// Simply loops until the button is pressed.
void waitForButton()
{
  while(digitalRead(buttonPin)==0)
  {
    delay(100);
  }
}

// The following 4 functions play the tone for their respective action,
// and then give the user a set amount of time to complete it. The thresholds
// for success vary across the sensors.
boolean bopIt(){
  int curReading = digitalRead(buttonPin);
  tick();
  bopTone();
  tick();
  elapsed = 0;
  boolean success = false;
  while (elapsed< (tempo))
  {
    if (curReading != digitalRead(buttonPin))
    {
      success= true;
    }
    delay(10);
    elapsed += 10;
  }
  return success;
}

boolean twistIt(){
  int curReading = analogRead(dialPin);
  tick();
  twistTone();
  tick();
  elapsed = 0;
  boolean success = false;
  while (elapsed< (tempo))
  {
    if (abs(curReading - analogRead(dialPin))>10)
    {
      success= true;
    }
    delay(10);
    elapsed += 10;
  }
  return success;
}

boolean flickIt(){
  int curReading = analogRead(flexPin);
  tick();
  flickTone();
  tick();
  elapsed = 0;
  boolean success = false;
  while (elapsed< (tempo))
  {
    if (abs(curReading - analogRead(flexPin))>5)
    {
      success= true;
    }
    delay(10);
    elapsed += 10;
  }
  return success;
}

boolean lightIt(){
  int curReading = analogRead(lightPin);
  tick();
  lightTone();
  tick();
  elapsed = 0;
  boolean success = false;
  while (elapsed< (tempo))
  {
    if (abs(curReading - analogRead(lightPin))>50)
    {
      success= true;
    }
    delay(10);
    elapsed += 10;
  }
  return success;
}

// A helpful method that makes all following fucntions shorter.
void playPitch(int pitch, int delTime)
{
  tone(speakerPin, pitch);
  delay(delTime);
}

// One clock tick for the system.
void tick()
{
  playPitch(262, tempo/20);
  noTone(speakerPin);
}

// Plays a number of tones equal to the player's score.
void playScore()
{
  while (playerScore>0)
  {
    playPitch(784, 300);
    noTone(speakerPin);
    delay(300);
    playerScore-=1;
  }
  delay(500);
}

// -- All functions below this point are just melodies for various queues or events.

void bopTone()
{
  delay(tempo/4);
  playPitch(695, tempo/3);
  playPitch(532, tempo/6);
  noTone(speakerPin);
  delay(tempo/4);
}

void lightTone()
{
  delay(tempo/4);
  playPitch(440, tempo/6);
  playPitch(659, tempo/6);
  playPitch(523, tempo/6);
  noTone(speakerPin);
  delay(tempo/4);
}

void flickTone()
{
  delay(tempo/4);
  playPitch(100, tempo/12);
  playPitch(150, tempo/12);
  playPitch(100, tempo/12);
  playPitch(150, tempo/12);
  playPitch(100, tempo/12);
  playPitch(150, tempo/12);
  noTone(speakerPin);
  delay(tempo/4);
}

void twistTone()
{
  delay(tempo/4);  
  playPitch(523, tempo/12);
  playPitch(554, tempo/12);
  playPitch(587, tempo/12);
  playPitch(622, tempo/12);
  playPitch(659, tempo/12);
  playPitch(698, tempo/12);
  noTone(speakerPin);
  delay(tempo/4);
}

void failTone()
{
  playPitch(156, 200);
  playPitch( 147, 200);
  playPitch(139, 200);
  playPitch(131, 200);
  playPitch( 123, 100);
  playPitch(117, 100);
  playPitch(123, 100);
  playPitch(117, 100);
  playPitch(123, 100);
  playPitch(117, 100);
  playPitch(123, 100);
  playPitch(117, 100);
  playPitch(123, 1000);
  noTone(speakerPin);
}

void nextRoundTone()
{
  playPitch(262, 200);
  playPitch(294, 200);
  playPitch(330, 200);
  playPitch(349, 200);
  playPitch(392, 400);
  noTone(speakerPin);
  delay(500);
}

void victoryTone()
{
  playPitch(131, 200);
  playPitch(164, 200);
  playPitch(196, 200);
  playPitch(262, 200);
  playPitch(330, 200);
  playPitch(392, 200);
  playPitch(523, 200);
  playPitch(659, 200);
  playPitch(784, 200);
  playPitch(1047, 2000);
  noTone(speakerPin);
  delay(1000);
}

void startTone()
{
  playPitch(523, 300);
  playPitch(659, 300);
  playPitch(784, 300);
  noTone(speakerPin);
  delay(500);
}
