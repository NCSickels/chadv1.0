# Testbed Configuration

## Description

For Chadv1.0 project, we will be using two virtual machines running on VirtualBox. The first virtual machine will be running Kali Linux and the second virtual machine will be running Metasploitable2. The Kali Linux virtual machine will be used to run the attack tools against services running on the Metasploitable2 virtual machine.

## Configuration

**Hypervisor**: VirtualBox 7.1.0

**VM 1 (Host)**:

- Kali Linux 2024.3 ( 16384 MB RAM, 2 CPU, 80 GB Storage )
- Network Adapter 1: NAT
- Network Adapter 2: Internal Network (_intnet_)
  - IP Address: 192.168.1.99 /24

**VM 2 (Target)**:

- Metasploitable 2.0 ( 2048 MB RAM, 1 CPU, 8GB Storage )
- Network Adapter 1: Internal Network (_intnet_)
  - IP Address: 192.168.1.100 /24

### Network Configuration

- Network Address: 192.168.1.0 /24
- Default Gateway: 192.168.1.1

## Miscellaneous

- Kali Linux Kernel Version: Linux kali 6.10.11-amd64 #1 SMP PREEMPT_DYNAMIC Kali 6.10.11-1kali1 (2024-09-26) x86_64 GNU/Linux
- GCC Version: gcc (Debian 14.2.0-3) 14.2.0
