# ThreadSanitizer

## Masscan Configuration

From the Masscan Makefile, add the following flags to the `CFLAGS` variable (line 101):

```bash
-fsanitize=thread,undefined,bounds-strict -fno-omit-frame-pointer
```

Once the flags are added, recompile Masscan by running the 'make' command. When Masscan runs with the ThreadSanitizer, the output is sent to stderr. This will require you to redirect the output to a file to view the results.

## Running Masscan with ThreadSanitizer

To run Masscan with the ThreadSanitizer, use the following command:

```bash
sudo bin/masscan -p21-8180 <TARGET_IP> --banners --packet-trace &> output.txt
```

## Running AFLnet on Masscan with ThreadSanitizer  
