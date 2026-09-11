#include <stdbool.h>

extern void wdt_reset(void);
extern bool control_loop_healthy(void);

/* fires every 100 ms regardless of whether the control loop is alive */
void timer_isr(void) {
    wdt_reset();
}

/* NEGATIVE: the correct pattern, conditional on liveness */
void supervisor_task(void) {
    if (control_loop_healthy()) {
        wdt_reset();
    }
}
