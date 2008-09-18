#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <unistd.h>

FILE* f;
long irq_count[256];

bool interrupts_idle(time_t t) {
    static time_t last_irq = time(NULL);
    char line[256];
    int i = 0;
    long ccount = 0;

    rewind(f);
    while (fgets(line, sizeof(line), f)) {
        // Check for mouse, keyboard and PS/2 devices.
        if (strcasestr(line, "mouse") != NULL ||
            strcasestr(line, "keyboard") != NULL ||
            strcasestr(line, "i8042") != NULL) {
            // If any IRQ count changed, update last_irq.
            if (sscanf(line, "%d: %ld", &i, &ccount) == 2 &&
                irq_count[i] != ccount) {
                last_irq = time(NULL);
                irq_count[i] = ccount;
            }
        }
    }
    return last_irq < t ? true : false;
}

int main(int argc, char** argv) {
    f = fopen("/proc/interrupts", "r");
    if (! f)
        exit(1);

    while (1) {
        time_t idle_time = time(NULL) - 3;
        if (interrupts_idle(idle_time))
            printf("OOO System is idle...\n");
        else
            printf("XXX User is active...\n");
        usleep(500000);
    }
    exit(0);
}
