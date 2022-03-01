# OnlineMultiBLASTqueries
Does multiple nucleotidic | aminoacidic sequence BLAST queries in the NCBI BLAST web from a given multiFASTA and writes the output with the results. 
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
```bash
python3 run_OnlineMultiBLASTqueries.py -p <driver-path> -d <in-path> -t <int> -o <out-path> -f <nucleotide|protein> -hi <yes|no>
```

- `-p --driverpath DRIVERPATH`
  - The ChromeDriver path (Optional). Default path: usr/bin/chromedrive
- `-d --dir IN_FILE`
  - MultiFASTA file.
- `-t --threads THREADS`
  - Number of threads (Optional). Default value: 1.
- `-O --outfile OUT_FILE`
  - Output file.
- `-f --format {nucleotide, protein}`
  - Sequence type: "nucleotide" | "protein".
- `-hi --hide {yes, no}`
  - Hide the browser. Default yes.
 
Example of bash execution:
```bash
python3 run_OnlineMultiBLASTqueries.py -d test/test_nucleotide.fa -o output_example.txt -f nucleotide -hi yes -t 4
```
### Move the chromedriver to the default path 
```bash
sudo mv path/to/chromedriver usr/bin
```
