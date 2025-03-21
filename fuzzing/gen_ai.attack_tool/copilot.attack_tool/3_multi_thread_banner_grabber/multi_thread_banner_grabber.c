// Usage: ./multi_thread_banner_grabber <targets_file>
// Targets file format: <ip> <port>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#define BUFFER_SIZE 1024
#define MAX_THREADS 10

typedef struct
{
    char ip[INET_ADDRSTRLEN];
    int port;
} target_t;

void *grab_banner(void *arg)
{
    target_t *target = (target_t *)arg;
    int sockfd;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    char response[BUFFER_SIZE];

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        perror("Socket creation failed");
        pthread_exit(NULL);
    }

    // Set server address
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(target->port);
    inet_pton(AF_INET, target->ip, &server_addr.sin_addr);

    // Connect to server
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        perror("Connection failed");
        close(sockfd);
        pthread_exit(NULL);
    }

    // Send a simple request
    snprintf(buffer, BUFFER_SIZE, "HEAD / HTTP/1.0\r\n\r\n");
    write(sockfd, buffer, strlen(buffer));

    // Read server response
    read(sockfd, response, BUFFER_SIZE);
    printf("Banner from %s:%d\n%s\n", target->ip, target->port, response);

    // Close socket
    close(sockfd);
    pthread_exit(NULL);
}

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s <targets_file>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    FILE *file = fopen(argv[1], "r");
    if (file == NULL)
    {
        perror("Failed to open file");
        exit(EXIT_FAILURE);
    }

    target_t targets[MAX_THREADS];
    pthread_t threads[MAX_THREADS];
    int thread_count = 0;

    while (fscanf(file, "%s %d", targets[thread_count].ip, &targets[thread_count].port) == 2)
    {
        if (pthread_create(&threads[thread_count], NULL, grab_banner, &targets[thread_count]) != 0)
        {
            perror("Failed to create thread");
            exit(EXIT_FAILURE);
        }
        thread_count++;

        if (thread_count >= MAX_THREADS)
        {
            for (int i = 0; i < thread_count; i++)
            {
                pthread_join(threads[i], NULL);
            }
            thread_count = 0;
        }
    }

    for (int i = 0; i < thread_count; i++)
    {
        pthread_join(threads[i], NULL);
    }

    fclose(file);
    return 0;
}