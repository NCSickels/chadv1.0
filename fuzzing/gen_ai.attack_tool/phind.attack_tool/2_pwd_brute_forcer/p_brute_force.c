// Phind - C FTP Password Brute Forcer Attack Tool
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define BUFFER_SIZE 32
#define PORT 1337

// Function prototypes
int establish_connection(const char *server_ip);
char *get_response(int socket);
int verify_credentials(int socket, const char *username, const char *password);

int main()
{
    int sock;
    char buffer[BUFFER_SIZE];

    // Get server information from user
    printf("Enter FTP server IP address: ");
    fgets(buffer, BUFFER_SIZE, stdin);
    buffer[strcspn(buffer, "\n")] = 0; // Remove trailing newline

    // Establish connection
    sock = establish_connection(buffer);
    if (sock < 0)
    {
        perror("Connection failed");
        return 1;
    }

    // Get credentials
    printf("Enter username: ");
    fgets(buffer, BUFFER_SIZE, stdin);
    buffer[strcspn(buffer, "\n")] = 0;

    printf("Enter password: ");
    fgets(buffer + strlen(buffer), BUFFER_SIZE - strlen(buffer), stdin);
    buffer[strcspn(buffer, "\n")] = 0;

    // Verify credentials
    int success = verify_credentials(sock, buffer, buffer + strlen(buffer));

    if (success)
    {
        printf("Password verified successfully!\n");
    }
    else
    {
        printf("Invalid password\n");
    }

    // Clean up
    shutdown(sock, SHUT_RDWR);
    close(sock);
    return 0;
}

int establish_connection(const char *server_ip)
{
    int sock;
    struct sockaddr_in server_addr;

    // Create socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0)
    {
        perror("socket creation failed");
        return -1;
    }

    // Configure server address
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    if (inet_pton(AF_INET, server_ip, &server_addr.sin_addr) <= 0)
    {
        perror("invalid address");
        return -1;
    }

    // Connect to server
    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        perror("connection failed");
        return -1;
    }

    return sock;
}

char *get_response(int socket)
{
    static char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);
    recv(socket, buffer, BUFFER_SIZE - 1, 0);
    return buffer;
}

int verify_credentials(int socket, const char *username, const char *password)
{
    char command[BUFFER_SIZE];

    // Send USER command
    snprintf(command, BUFFER_SIZE, "USER %s\r\n", username);
    send(socket, command, strlen(command), 0);

    // Check response
    if (strstr(get_response(socket), "331") == NULL)
    {
        return 0;
    }

    // Send PASS command
    snprintf(command, BUFFER_SIZE, "PASS %s\r\n", password);
    send(socket, command, strlen(command), 0);

    // Check final response
    return strstr(get_response(socket), "230") != NULL;
}