// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
#include <stdbool.h>
#include <stdlib.h>
#include <unistd.h>
#include "rzero_dht_mraa_read.h"

// This is the only processor specific magic value, the maximum amount of time to
// spin in a loop before bailing out and considering the read a timeout.  This should
// be a high value, but if you're running on a much faster platform than a Raspberry
// Pi or Beaglebone Black then it might need to be increased.
#define DHT_MAXCOUNT 640000

// Number of bit pulses to expect from the DHT.  Note that this is 41 because
// the first pulse is a constant 50 microsecond pulse, with 40 pulses to represent
// the data afterwards.
#define DHT_PULSES 41



int rzero_dht_mraa_read(int type, int pin, float* humidity, float* temperature) {
  // Validate humidity and temperature arguments and set them to zero.
  if (humidity == NULL || temperature == NULL) {
    return DHT_ERROR_ARGUMENT;
  }
  // This is all built for the libmraa library, which is a lot slower than RPi GPIO control. Might still be buggy
  mraa_result_t status = MRAA_SUCCESS;
  mraa_gpio_context gpio;
  mraa_init();
  *temperature = 0.0f;
  *humidity = 0.0f;

  // Initialize GPIO library.
  gpio = mraa_gpio_init(pin);
  if (gpio == NULL) {
    fprintf(stderr, "Failed to initialize GPIO %d\n", pin);
    mraa_deinit();
    return EXIT_FAILURE;
  }
  // Store the count that each DHT bit pulse is low and high.
  // Make sure array is initialized to start at zero.
  int pulseCounts[DHT_PULSES*2] = {0};

  // Set pin to output.
  status = mraa_gpio_dir(gpio, MRAA_GPIO_OUT);
    if (status != MRAA_SUCCESS) {
        goto err_exit;
  }
  // Bump up process priority and change scheduler to try to try to make process more 'real time'.
  set_max_priority();

  // Set pin high for ~500 milliseconds.

  status = mraa_gpio_write(gpio, 1);
  if (status != MRAA_SUCCESS) {
    goto err_exit;
  }
  sleep_milliseconds(500);

  // The next calls are timing critical and care should be taken
  // to ensure no unnecssary work is done below.
  // Set pin low for ~20 milliseconds.
  status = mraa_gpio_write(gpio, 0);
  if (status != MRAA_SUCCESS) {
    goto err_exit;
  }

  busy_wait_milliseconds(20);

  // Set pin at input.
  status = mraa_gpio_dir(gpio, MRAA_GPIO_IN);
    if (status != MRAA_SUCCESS) {
      goto err_exit;
  }
  /* //Some debugging code
  uint32_t countdb = 0;
  while (!mraa_gpio_read(gpio)) {
    printf("Pin: %x\n", mraa_gpio_read(gpio));
    ++countdb;
  }

  printf("Pin: %x\n", mraa_gpio_read(gpio));
  printf("Took : %x\n",countdb);
  */
  // Need a very short delay before reading pins or else value is sometimes still low.
  for (volatile int i = 0; i < 50; ++i) {
  }
  // Wait for DHT to pull pin low.
  uint32_t count = 0;
  while (mraa_gpio_read(gpio)) {
    if (++count >= DHT_MAXCOUNT) {
      // Timeout waiting for response.
      set_default_priority();
      //printf("Timeout D");
      mraa_deinit();
      return DHT_ERROR_TIMEOUT;
    }
  }
  //printf("Took : %x",count);
  // Record pulse widths for the expected result bits.
  for (int i=0; i < DHT_PULSES*2; i+=2) {
    // Count how long pin is low and store in pulseCounts[i]
    while (!mraa_gpio_read(gpio)) {
      if (++pulseCounts[i] >= DHT_MAXCOUNT) {
        // Timeout waiting for response.
        set_default_priority();
        mraa_deinit();
        return DHT_ERROR_TIMEOUT;
      }
    }
    // Count how long pin is high and store in pulseCounts[i+1]
    while (mraa_gpio_read(gpio)) {
      if (++pulseCounts[i+1] >= DHT_MAXCOUNT) {
        // Timeout waiting for response.
        set_default_priority();
        mraa_deinit();
        return DHT_ERROR_TIMEOUT;
      }
    }
  }

  // Done with timing critical code, now interpret the results.
  //printf("Check!");
  // Drop back to normal priority.
  set_default_priority();

  // Compute the average low pulse width to use as a 50 microsecond reference threshold.
  // Ignore the first two readings because they are a constant 80 microsecond pulse.
  uint32_t threshold = 0;
  for (int i=2; i < DHT_PULSES*2; i+=2) {
    threshold += pulseCounts[i];
  }
  threshold /= DHT_PULSES-1;

  // Interpret each high pulse as a 0 or 1 by comparing it to the 50us reference.
  // If the count is less than 50us it must be a ~28us 0 pulse, and if it's higher
  // then it must be a ~70us 1 pulse.
  uint8_t data[5] = {0};
  for (int i=3; i < DHT_PULSES*2; i+=2) {
    int index = (i-3)/16;
    data[index] <<= 1;
    if (pulseCounts[i] >= threshold) {
      // One bit for long pulse.
      data[index] |= 1;
    }
    // Else zero bit for short pulse.
  }

  // Useful debug info:
  //printf("Data: 0x%x 0x%x 0x%x 0x%x 0x%x\n", data[0], data[1], data[2], data[3], data[4]);

  // Verify checksum of received data.
  if (data[4] == ((data[0] + data[1] + data[2] + data[3]) & 0xFF)) {
    if (type == DHT11) {
      // Get humidity and temp for DHT11 sensor.
      *humidity = (float)data[0];
      *temperature = (float)data[2];
    }
    else if (type == DHT22) {
      // Calculate humidity and temp for DHT22 sensor.
      *humidity = (data[0] * 256 + data[1]) / 10.0f;
      *temperature = ((data[2] & 0x7F) * 256 + data[3]) / 10.0f;
      if (data[2] & 0x80) {
        *temperature *= -1.0f;
      }
    }
    return DHT_SUCCESS;
  }
  else {
    return DHT_ERROR_CHECKSUM;
  }

err_exit:
    mraa_result_print(status);

    /* deinitialize mraa for the platform (not needed most of the times) */
    mraa_deinit();

    return EXIT_FAILURE;
}
