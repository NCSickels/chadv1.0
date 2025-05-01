# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -O2 
LDFLAGS = -lpthread -lm

# Source files
SOURCES = gc_banner_grabber.c gc_brute_force.c gc_mt_banner_grabber.c \
					p_banner_grabber.c p_brute_force.c p_mt_banner_grabber.c

# Binaries (one for each source file)
BINARIES = $(SOURCES:.c=)

# Default target: build all binaries
all: $(BINARIES)

# Rule to build each binary
%: %.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

tsan: CFLAGS += -fsanitize=thread,undefined,bounds-strict -fno-omit-frame-pointer
tsan: $(BINARIES)

# Clean target: remove all binaries
clean:
	rm -f $(BINARIES)
