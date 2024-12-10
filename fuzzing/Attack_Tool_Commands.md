# Attack Tool Commands

## Description

This document contains the commands used to run the attack tools against services running on the Metasploitable2 virtual machine.

## Medusa

For each of the services tested, the hostname used is `msfadmin` and the password list used is `password_list.txt`. The password list was generated using using the first 28 passwords from the `rockyou.txt` password list with two additional passwords `msfadmin` and `postgres` added to the end of the list to generate found cases.

The command used to generate the `password_list.txt` file is:

```bash
tail -n +6 rockyou.txt | head -n 28 > password_list.txt && echo "msfadmin" >> password_list.txt && echo "postgres" >> password_list.txt
```

```bash
# SSH Brute Force
medusa -h 192.168.1.100 -u msfadmin -P password_list.txt -M ssh -n 22

# FTP Brute Force
medusa -h 192.168.1.100 -u msfadmin -P password_list.txt -M ftp -n 21

# PostgreSQL Brute Force
medusa -h 192.168.1.100 -u postgres -P password_list.txt -M postgres -n 5432
```

## Masscan

```bash
# List available network interfaces
masscan --iflist

# Scan all ports on the target machine using the specified network interface
sudo masscan -p21-8180 192.168.1.100 --banners --packet-trace --source-mac <IFACE_MAC_ADDR> 
```

## Radamsa

### Fuzzing Requests to Network Services

```bash
mkdir ~/www && cd ~/www
# Create a simple html file
nano index.html
echo "<h1>Hello, World!</h1>" > index.html
# Start a php server
php -S localhost:8080
```

After running the PHP server, you should get output similar to:

```bash
PHP 7.2.24-0ubuntu0.18.04.1 Development Server started at Wed Jan  1 16:06:41 2020
Listening on http://localhost:8080
Document root is /home/user/www
Press Ctrl-C to quit.
```

From here, switch back to your original terminal session and test that the web server is working using `curl`:

```bash
curl localhost:8080
# or you can also type
curl http://localhost:8080
```

This should return the HTML content you created in the `index.html` file.

```html
<h1>Hello, World!</h1>
```

The web server only needs to be accessible locally, so you should not need to open any ports on the firewall.

Now that the web server is set up, you can use Radamsa to fuzz the web server.

First, you'll need to create a sample HTTP request to use as the input data for Radamsa. You can use the following command to create a sample HTTP request:

```bash
nano http-request.txt
```

Then copy the HTTP request into the file:

```http
GET / HTTP/1.1
Host: localhost:8080
User-Agent: test
Accept: */*
```

Next, you can use Radamsa to submit this HTTP request to the local web server. In order to do this, you'll need to use Radamsa as a TCP client, which can be done by specifuing an IP address and port to connect to:

```bash
radamsa -o 127.0.0.1:8080 http-request.txt
```

> **Note:** Be aware that using Radamsa as a TCP client will potentially cause malformed/malicious data to be transmitted over the network. This may break things, so be careful to only access networks that we are authorized to test on, or stick to local host.

Finally, if you view the output of the PHP server logs, you'll see that it has received the requests, but most likely not process them as they were invalid/malformed.

## Fuzzing Network Client Applications

Radamsa can also be used to fuzz network client applications. This is achieved by intercepting responses from a network service and fuzzing them before they are received by the client.

The purpose behind this is to test how reslient the client application is to malformed data.

As an example, we will fuzz the `whois` command. First, you'll need to acquire a sample `whois` response to use as the input data. This can be done by making a whois requests and saving the output to a file. You can use any domain you like, but `example.com` is used below:

```bash
whois example.com > whois-response.txt
```

Next, you'll set up Radamsa as a server that serves fuzzed versions of this `whois` response. You'll need to be able to continue using your terminal once Radamsa is running in server mode, so it is recommended to open a new terminal session for this.

```bash
radamsa -o :4343 whois-response.txt -n inf
```

Radamsa will now be running in TCP server mode, and will serve a fuzzed version of `whois-response.txt` each time a connection is made to the server, no matter what request data is received.

You can now proceed to testing the `whois` client application. You'll need to make a normal `whois` request for any domain, but wuth `whois` pointed to the local Radamsa server:

```bash
whois -h localhost:4343 example.com
```

The response will be the sample data, but fuzzed by Radamsa. You can continue to make requests to the local server as long as Radamsa is running, and it will serve a different fuzzed version of the `whois-response.txt` each time.
