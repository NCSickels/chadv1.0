// BannerGrabberPhind.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <time.h>

#define BUFFER_SIZE 4096
#define TIMEOUT_SECONDS 5

// Structure to hold connection parameters
typedef struct
{
    char *hostname;
    uint16_t port;
} ConnectionParams;

// Initialize socket with timeout settings
int initialize_socket()
{
    int sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sockfd == -1)
    {
        fprintf(stderr, "Error creating socket: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    // Set timeouts
    struct timeval tv;
    tv.tv_sec = TIMEOUT_SECONDS;
    tv.tv_usec = 0;

    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) == -1 ||
        setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv)) == -1)
    {
        perror("Failed to set socket timeout");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    return sockfd;
}

// Connect to target server
int connect_to_target(int sockfd, const ConnectionParams *params)
{
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(params->port);

    // Convert hostname to IP address
    if (inet_pton(AF_INET, params->hostname, &server_addr.sin_addr) <= 0)
    {
        fprintf(stderr, "Invalid hostname/IP format\n");
        return 0;
    }

    // Attempt connection with timeout
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1)
    {
        if (errno != ETIMEDOUT && errno != ECONNREFUSED)
        {
            perror("Connection failed");
        }
        return 0;
    }

    return 1;
}

// Grab banner from server
char *grab_banner(int sockfd, size_t buffer_size)
{
    char *buffer = malloc(buffer_size);
    if (!buffer)
    {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }

    ssize_t bytes_received = recv(sockfd, buffer, buffer_size - 1, 0);
    if (bytes_received <= 0)
    {
        free(buffer);
        return NULL;
    }

    buffer[bytes_received] = '\0';
    return buffer;
}

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        fprintf(stderr, "Usage: %s <hostname/IP> <port>\n", argv[0]);
        return EXIT_FAILURE;
    }

    ConnectionParams params = {
        .hostname = argv[1],
        .port = atoi(argv[2])};

    // Validate port number
    if (params.port < 1 || params.port > 65535)
    {
        fprintf(stderr, "Invalid port number\n");
        return EXIT_FAILURE;
    }

    int sockfd = initialize_socket();

    printf("Attempting connection to %s:%d...\n", params.hostname, params.port);

    if (connect_to_target(sockfd, &params))
    {
        printf("Connected successfully!\n");

        char *banner = grab_banner(sockfd, BUFFER_SIZE);
        if (banner)
        {
            printf("Received banner:\n%s\n", banner);
            free(banner);
        }
        else
        {
            printf("No banner received\n");
        }
    }

    close(sockfd);
    return EXIT_SUCCESS;
}
