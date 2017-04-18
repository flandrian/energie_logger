#include <EnableInterrupt.h>

static const int COUNTER_0_PIN = 2;
static const int NUM_COUNTERS = 10;
static uint16_t counters[NUM_COUNTERS] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
static uint16_t last_counter_values[NUM_COUNTERS] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(COUNTER_0_PIN, INPUT_PULLUP);
  enableInterrupt(COUNTER_0_PIN, handle_counter0_increment, FALLING);
}

void handle_counter0_increment()
{
  counters[0]++;
}

void loop() {
  int last_char = Serial.read();
  if (last_char == '?') report_and_reset();
  delay(1000);
}

void report_and_reset()
{
  for (int i = 0; i < NUM_COUNTERS; i++)
  {
    unsigned int sample = counters[i];
    // this relies on the subtraction to wrap around
    unsigned int ticks = sample - last_counter_values[i];
    last_counter_values[i] = sample;
    Serial.print(i, DEC);
    Serial.print(":");
    Serial.print(ticks, DEC);
    Serial.println();
  }
}
