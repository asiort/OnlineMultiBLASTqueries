"""
This script does multiple nucleotidic|aminoacidic BLAST queries from a given multiFASTA and write the output with the results. 
The queries are parallelized using Threads. 

@Dependencies Selenium and ChromeDrive  
@Author Asier Ortega Legarreta
@Date 2021/11/25
@mail asierortega20@gmail.com
"""

from threading import Thread
from myFunctions.functions import arguments, open_fasta, manage, write_output

def main():
    """
    Main program
    """
    """
    Obtain the arguments and define parameters
    """
    args = arguments()

    path_fasta = args.in_file
    file_out = args.out_file
    format = args.format

    ## Selenium Driver path
    if args.driverpath:
        driver_path = args.driverpath
    else:
        driver_path = "/usr/bin/chromedriver"


    """
    We obtain the dic
    """
    fasta_dic = open_fasta(path_fasta) ## Obtain dic with proteins
    list_protein = []

    ## Create a list with the keys of the dic = fasta headers
    for i in fasta_dic.keys():
        list_protein.append(i)

    """
    With threads
    """
    if args.threads:
        n_threads = int(args.threads)
    else:
        n_threads = 1

    if n_threads > len(list_protein): ## In case there are more threads than queries
        n_threads = len(list_protein)

    t = [] ## List for the threads

    ## Distribute the processes
    integer = len(list_protein) // n_threads
    remainder = len(list_protein) % n_threads

    start = 0
    end = integer

    for task in range(n_threads):
        if not task == n_threads-1: ## Not last thread
            t.append(Thread(target=manage, args=(list_protein, start, end, fasta_dic, driver_path, format)))
            t[task].start()
            aux = end
            start = end
            end = aux + integer

        else:
            end += remainder
            t.append(Thread(target=manage, args=(list_protein, start, end, fasta_dic, driver_path, format)))
            t[task].start()

    for task in range(n_threads):
        t[task].join()

    """
    Write output
    """
    write_output(file_out, fasta_dic)

    print("\n---FINISHED----")

if __name__ == "__main__":
    main()
