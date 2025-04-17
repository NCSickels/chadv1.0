// Github Copilot - C Banner Grabber Attack Tool
// Usage: gcc -fno-stack-protector -o gc_banner_grabber gc_banner_grabber.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>

#define BUFFER_SIZE 32

void banner_grab(int sockfd)
{
    char buffer[BUFFER_SIZE];
    int bytes_received;

    // Initialize buffer
    memset(buffer, 0, sizeof(buffer));

    // Receive banner
    bytes_received = recv(sockfd, buffer, 1024, 0);
    if (bytes_received < 0)
    {
        perror("recv");
        return;
    }

    // Print banner
    printf("Banner: %s\n", buffer);
    // char small_buffer[BUFFER_SIZE];
    // strcpy(small_buffer, buffer);
    // printf("Banner: %s\n", small_buffer);
}

void scan_port(const char *host, int port)
{
    int sockfd;
    struct sockaddr_in server_addr;
    struct hostent *server;

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        perror("socket");
        return;
    }

    // Get server IP address
    server = gethostbyname(host);
    if (server == NULL)
    {
        fprintf(stderr, "Error: No such host\n");
        close(sockfd);
        return;
    }

    // Set up server address struct
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    memcpy(&server_addr.sin_addr.s_addr, server->h_addr, server->h_length);

    // Attempt to connect to the server
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        close(sockfd);
        return;
    }

    printf("Port %d open\n", port);
    banner_grab(sockfd);

    close(sockfd);
}

int main(int argc, char *argv[])
{
    const char *host;
    int start_port, end_port;

    if (argc != 4)
    {
        fprintf(stderr, "Usage: %s <host> <start_port> <end_port>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    host = argv[1];
    start_port = atoi(argv[2]);
    end_port = atoi(argv[3]);

    printf("Scanning ports %d-%d on %s...\n", start_port, end_port, host);

    for (int port = start_port; port <= end_port; port++)
    {
        scan_port(host, port);
    }

    printf("Scan complete.\n");

    return 0;
}