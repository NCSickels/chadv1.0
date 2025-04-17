// Phind - C++ Banner Grabber Attack Tool
#include <iostream>
#include <string>
#include <vector>
#include <cstring>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <errno.h>
#include <stdexcept>

class BannerGrabber
{
private:
    int sockfd;

public:
    BannerGrabber() : sockfd(-1) {}

    ~BannerGrabber()
    {
        if (sockfd != -1)
        {
            close(sockfd);
        }
    }

    void initializeSocket()
    {
        sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sockfd == -1)
        {
            throw std::runtime_error("Failed to create socket: " + std::string(std::strerror(errno)));
        }

        // Set timeout for connection attempts
        struct timeval tv;
        tv.tv_sec = 5; // 5 seconds timeout
        tv.tv_usec = 0;
        setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (const char *)&tv, sizeof tv);
        setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, (const char *)&tv, sizeof tv);
    }

    bool connectToTarget(const std::string &ipAddress, uint16_t port)
    {
        struct sockaddr_in server_addr;
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(port);

        if (inet_pton(AF_INET, ipAddress.c_str(), &server_addr.sin_addr) <= 0)
        {
            throw std::invalid_argument("Invalid IP address format");
        }

        if (::connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1)
        {
            return false;
        }
        return true;
    }

    std::string grabBanner(size_t bufferSize = 2048)
    {
        std::vector<char> buffer(bufferSize);
        ssize_t bytesReceived = recv(sockfd, buffer.data(), bufferSize - 1, 0);

        if (bytesReceived <= 0)
        {
            return "";
        }

        buffer[bytesReceived] = '\0';
        return std::string(buffer.data());
    }
};

int main()
{
    try
    {
        BannerGrabber bg;

        // Initialize the socket
        bg.initializeSocket();

        // Example usage - grabbing SSH banner
        std::string targetIP = "192.168.0.50";
        uint16_t port = 22;

        if (bg.connectToTarget(targetIP, port))
        {
            std::cout << "Connected to " << targetIP << ":" << port << std::endl;

            // Grab the banner
            std::string banner = bg.grabBanner(4096);
            if (!banner.empty())
            {
                std::cout << "Received banner:\n"
                          << banner << std::endl;
            }
            else
            {
                std::cout << "No banner received" << std::endl;
            }
        }
        else
        {
            std::cout << "Failed to connect to " << targetIP << ":" << port << std::endl;
        }
    }
    catch (const std::exception &e)
    {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
