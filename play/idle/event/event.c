#include <cstdio>
#include <ctime>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#include <linux/input.h>

#define EVENT_DEVICES 32
static int fd[EVENT_DEVICES];
static time_t last_event = time(NULL);

void open_event_devs() {
    char event_dev[32];

    for (int i = 0; i < EVENT_DEVICES; i++) {
        sprintf(event_dev, "/dev/input/event%i", i);
        fd[i] = open(event_dev, O_RDONLY|O_NONBLOCK);
    }
}

bool event_devs_idle(time_t t) {
    struct input_event ev;
    bool retval = true;

    if (last_event > t) return false;

    for (int i = 0; i < EVENT_DEVICES; i++) {
        if (fd[i] == -1)
            continue;
        if (read(fd[i], &ev, sizeof(struct input_event)) < 0)
            continue;
        if (ev.time.tv_sec > t) {
            last_event = ev.time.tv_sec;
            retval = false;
        }
    }
    return retval;
}

int main(int argc, char** argv) {
    open_event_devs();

    while (1) {
        time_t idle_time = time(NULL) - 3;
        if (event_devs_idle(idle_time))
            printf("OOO System is idle...\n");
        else
            printf("XXX User is active...\n");
        usleep(500000);
    }
    return 0;
}
