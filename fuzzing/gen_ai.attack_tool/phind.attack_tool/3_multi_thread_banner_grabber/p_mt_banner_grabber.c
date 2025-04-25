// Phind - C Multi-threaded Banner Grabber Attack Tool
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

#define MAX_THREADS 1
#define BUFFER_SIZE 32
#define PORT 1337

// Shared result structure
typedef struct
{
    char ip[BUFFER_SIZE];
    int status;
    char banner[BUFFER_SIZE];
} scan_result_t;

// Mutex for thread-safe operations
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void *scan_target(void *arg)
{
    scan_result_t *result = (scan_result_t *)arg;
    int sockfd;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];

    // Initialize socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        pthread_mutex_lock(&mutex);
        strcpy(result->banner, "Failed to create socket");
        result->status = -1;
        pthread_mutex_unlock(&mutex);
        return NULL;
    }

    // Setup server address
    server_addr.sin_family = AF_INET;
    inet_pton(AF_INET, result->ip, &server_addr.sin_addr);
    server_addr.sin_port = htons(PORT);

    // Connect to target
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        pthread_mutex_lock(&mutex);
        strcpy(result->banner, "Connection failed");
        result->status = -1;
        pthread_mutex_unlock(&mutex);
        close(sockfd);
        return NULL;
    }

    // Receive banner
    int bytes_received = recv(sockfd, buffer, BUFFER_SIZE - 1, 0);
    if (bytes_received <= 0)
    {
        pthread_mutex_lock(&mutex);
        strcpy(result->banner, "No banner received");
        result->status = -1;
        pthread_mutex_unlock(&mutex);
    }
    else
    {
        buffer[bytes_received] = '\0';
        pthread_mutex_lock(&mutex);
        strncpy(result->banner, buffer, BUFFER_SIZE - 1);
        result->banner[BUFFER_SIZE - 1] = '\0';
        result->status = 0;
        pthread_mutex_unlock(&mutex);
    }

    close(sockfd);
    return NULL;
}

int main(int argc, char *argv[])
{
    if (argc < 3)
    {
        printf("Usage: %s <target_ip_1> <target_ip_2>\n", argv[0]);
        return 1;
    }

    // Create scan result structures
    scan_result_t targets[MAX_THREADS];
    pthread_t threads[MAX_THREADS];

    // Initialize target IPs
    strncpy(targets[0].ip, argv[1], BUFFER_SIZE - 1);
    targets[0].ip[BUFFER_SIZE - 1] = '\0';
    if (argc > 3)
    {
        strncpy(targets[1].ip, argv[2], BUFFER_SIZE - 1);
        targets[1].ip[BUFFER_SIZE - 1] = '\0';
    }

    // Create threads
    for (int i = 0; i < MAX_THREADS && i < argc - 1; i++)
    {
        pthread_create(&threads[i], NULL, scan_target, &targets[i]);
    }

    // Wait for threads to complete
    for (int i = 0; i < MAX_THREADS && i < argc - 1; i++)
    {
        pthread_join(threads[i], NULL);
    }

    // Display results
    printf("\nScan Results:\n");
    for (int i = 0; i < MAX_THREADS && i < argc - 1; i++)
    {
        printf("Target %d (%s):\n", i + 1, targets[i].ip);
        printf("Status: %d\n", targets[i].status);
        printf("Banner: %s\n\n", targets[i].banner);
    }

    return 0;
}