# OnlineMultiBLASTqueries
Does multiple nucleotidic | aminoacidic BLAST queries from a given multiFASTA and write the output with the results. 
- The queries are parallelized using Threads. 
- Works using Selenium and ChromeDriver. 

## Requeriments:
 - Python Installed (Recommended version 3.8 or above)
 - Pip Package Manager
 - Selenium library (use `pip install selenium`)
 - Driver for launching the automation (chromedriver)
   - Be sure to match the version of Chrome you have
   - [Download URL](https://sites.google.com/chromium.org/driver/downloads?authuser=0)
 
## Query file:
- The query file should be a (multi)FASTA with one or more either nucleotidic or aminoacidic sequence. 
- Each sequence must have unique name (header)

## Script options:
- `-p --driverpath DRIVERPATH`
  - The ChromeDriver path (Optional). Default path: usr/bin/chromedrive
- `-d --dir IN_FILE`
  - MultiFASTA file.
- `-t --threads THREADS`
  - Number of threads (Optional). Default value: 1.
- `-O --outfile OUT_FILE`
  - Output file.
- `-f --format {nucleotide, protein}`
  - Sequence type: "nucleotide" | "protein"..
