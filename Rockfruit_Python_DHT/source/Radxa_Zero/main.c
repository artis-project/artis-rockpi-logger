#include"rzero_dht_mraa_read.h"
#include<stdio.h>

int main()
{
	float hum;
	float temp;
	
rzero_dht_mraa_read(22, 40, &hum, &temp);

printf("%f\n", hum);
printf("%f\n", temp);

}

#include <time.h>

void sleep_milliseconds(unsigned int ms) {
    struct timespec ts;
    ts.tv_sec = ms / 1000;
    ts.tv_nsec = (ms % 1000) * 1000000;
    nanosleep(&ts, NULL);
}

#include <sys/time.h>
#include <sys/resource.h>

void set_default_priority() {
    setpriority(PRIO_PROCESS, 0, 0);
}


#include <sys/time.h>
#include <sys/resource.h>

void set_max_priority() {
    setpriority(PRIO_PROCESS, 0, -20);
}


#include <time.h>

void busy_wait_milliseconds(unsigned int ms) {
    struct timespec ts;
    ts.tv_sec = ms / 1000;
    ts.tv_nsec = (ms % 1000) * 1000000;
    nanosleep(&ts, NULL);
}
