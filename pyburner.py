#!/usr/bin/python3

import sys
import time
import multiprocessing
import os
from datetime import datetime

def worker(memory_size_mb, cpu_load_percent, ops_counter):
    # Alokacja pamięci
    memory_size_bytes = memory_size_mb * 1024 * 1024
    dummy_data = [0] * (memory_size_bytes // 4)  # Alokacja listy o odpowiedniej wielkości

    # Obciążenie CPU
    load_time = cpu_load_percent / 100.0
    sleep_time = 1.0 - load_time

    while True:
        # Obciążenie
        start = time.time()
        operations = 0
        while (time.time() - start) < load_time:
            operations += 1
        # Aktualizacja licznika operacji
        with ops_counter.get_lock():
            ops_counter.value += operations
        # Czas "bezczynności"
        time.sleep(sleep_time)

def get_memory_info():
    # Pobranie informacji o pamięci z /proc/meminfo
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()

    mem_total = int(lines[0].split()[1]) / 1024  # KB na MB
    mem_free = int(lines[1].split()[1]) / 1024
    mem_used = mem_total - mem_free
    return mem_total, mem_used, mem_free

def get_cpu_info():
    # Pobranie informacji o CPU z /proc/cpuinfo
    with open('/proc/cpuinfo', 'r') as f:
        lines = f.readlines()

    cpu_model = None
    cpu_cores = 0
    for line in lines:
        if line.startswith("model name"):
            if cpu_model is None:
                cpu_model = line.split(":")[1].strip()
            cpu_cores += 1
    return cpu_model, cpu_cores

def get_cpu_times():
    with open('/proc/stat', 'r') as f:
        line = f.readline()
        parts = line.split()[1:]  # Pomijamy pierwszy element "cpu"
        return list(map(int, parts))

def calculate_cpu_usage(prev, curr):
    # Oblicz różnice czasów pomiędzy dwoma pomiarami
    prev_idle = prev[3] + prev[4]
    curr_idle = curr[3] + curr[4]

    prev_total = sum(prev)
    curr_total = sum(curr)

    # Oblicz zmiany w czasach ogólnych i bezczynności
    total_diff = curr_total - prev_total
    idle_diff = curr_idle - prev_idle

    # Oblicz obciążenie CPU jako procent
    cpu_usage = (total_diff - idle_diff) / total_diff * 100
    return cpu_usage

def print_system_info():
    # Wyświetlenie informacji o systemie
    total_memory, used_memory, free_memory = get_memory_info()
    cpu_model, cpu_cores = get_cpu_info()

    print(f"      CPU: {cpu_model}")
    print(f"CPU cores: {cpu_cores}")
    print(f"Total RAM: {total_memory:.2f} MB")
    print(f" Used RAM: {used_memory:.2f} MB")
    print(f" Free RAM: {free_memory:.2f} MB")

def monitor_performance(ops_counter):
    # Monitorowanie wydajności co jakiś czas
    global prev_times
    previous_value = 0
    while True:
        time.sleep(10) # częstość monitorowania
        current_value = ops_counter.value
        operations_per_sec = (current_value - previous_value) / 60.0 / 1000.0
        previous_value = current_value
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cpu_usage = calculate_cpu_usage(prev_times, get_cpu_times())
        prev_times = get_cpu_times()
        print(f"[{timestamp}]  {operations_per_sec:.2f}k op/sek  CPU load: {cpu_usage:.2f}%")

def main():
    if len(sys.argv) != 4:
        print("Użycie: python3 stress_test.py <liczba_wątków> <RAM_na_wątek_MB> <obciążenie_CPU_%>")
        print_system_info()
        sys.exit(1)

    num_threads = int(sys.argv[1])
    memory_per_thread = int(sys.argv[2])
    cpu_load = float(sys.argv[3])

    print_system_info()

    # Utwórz zmienną wspólną do zliczania operacji
    ops_counter = multiprocessing.Value('i', 0)

    # Tworzenie i uruchamianie procesów roboczych
    processes = []
    for _ in range(num_threads):
        process = multiprocessing.Process(target=worker, args=(memory_per_thread, cpu_load, ops_counter))
        process.start()
        processes.append(process)

    # Uruchom monitor wydajności w osobnym procesie
    monitor_process = multiprocessing.Process(target=monitor_performance, args=(ops_counter,))
    monitor_process.start()

    # Czekaj na zakończenie wszystkich procesów
    try:
        for process in processes:
            process.join()
        monitor_process.join()
    except KeyboardInterrupt:
        print("Przerywanie testu...")
        for process in processes:
            process.terminate()
        monitor_process.terminate()

if __name__ == "__main__":
    prev_times = get_cpu_times()
    main()
