/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <arpa/inet.h>
#include <errno.h>
#include <netdb.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>

bool isIPv4Addr(const char *domain);

bool isIPv6Addr(const char *domain);

int get_address(const char *domain, char *ip_address, size_t ip_address_size);