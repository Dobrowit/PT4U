/* gcc -Os -flto -Wl,--gc-sections -Wl,--strip-all -o pyburnerc pyburner.c -lpthread ; strip pyburnerc

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <string.h>

typedef struct {
    int memory_size_mb;
    float cpu_load_percent;
    unsigned long long *ops_counter;
} thread_data_t;

void *worker(void *arg) {
    thread_data_t *data = (thread_data_t *)arg;
    int memory_size_bytes = data->memory_size_mb * 1024 * 1024;
    free(malloc(memory_size_bytes)); // Alokacja pamięci bez przechowywania wskaźnika
    unsigned long long local_ops = 0;

    while (1) {
        struct timespec start, end;
        clock_gettime(CLOCK_MONOTONIC, &start);
        do {
            local_ops++;
            clock_gettime(CLOCK_MONOTONIC, &end);
        } while ((end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9 < data->cpu_load_percent / 100.0);
        
        __sync_fetch_and_add(data->ops_counter, local_ops);
        usleep((1.0 - data->cpu_load_percent / 100.0) * 1e6);
    }
}

void print_system_info() {
    char buffer[128];
    FILE *fp = fopen("/proc/cpuinfo", "r");
    while (fgets(buffer, sizeof(buffer), fp)) {
        if (strncmp(buffer, "model name", 10) == 0) {
            printf("CPU: %s", strchr(buffer, ':') + 2);
            break;
        }
    }
    fclose(fp);

    fp = fopen("/proc/meminfo", "r");
    while (fgets(buffer, sizeof(buffer), fp)) {
        if (strncmp(buffer, "MemTotal", 8) == 0 || strncmp(buffer, "MemFree", 7) == 0) {
            printf("%s", buffer);
        }
    }
    fclose(fp);
}

void *monitor_performance(void *arg) {
    unsigned long long *ops_counter = (unsigned long long *)arg;
    unsigned long long previous_value = 0;

    while (1) {
        sleep(10);
        unsigned long long current_value = *ops_counter;
        printf("[%s]  %.2f k op/sek\n", __TIME__, (current_value - previous_value) / 10.0 / 1000.0);
        previous_value = current_value;
    }
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        printf("Użycie: %s <liczba_wątków> <RAM_na_wątek_MB> <obciążenie_CPU_%%>\n", argv[0]);
        print_system_info();
        return 1;
    }

    int num_threads = atoi(argv[1]);
    int memory_per_thread = atoi(argv[2]);
    float cpu_load = atof(argv[3]);

    print_system_info();

    unsigned long long ops_counter = 0;
    pthread_t threads[num_threads];
    thread_data_t thread_data[num_threads];

    for (int i = 0; i < num_threads; i++) {
        thread_data[i] = (thread_data_t){memory_per_thread, cpu_load, &ops_counter};
        pthread_create(&threads[i], NULL, worker, &thread_data[i]);
    }

    pthread_t monitor_thread;
    pthread_create(&monitor_thread, NULL, monitor_performance, &ops_counter);

    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }
    pthread_cancel(monitor_thread);

    return 0;
}
