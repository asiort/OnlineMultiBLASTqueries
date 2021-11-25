"""
This script does multiple nucleotidic|aminoacidic BLAST queries from a given multiFASTA and write the output with the results. 
The queries are parallelized using Threads. 

@Dependencies Selenium and ChromeDrive  
@Author Asier Ortega Legarreta
@Date 2021/11/25
@mail asierortega20@gmail.com
"""
#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from threading import Thread
import argparse
import os
import sys

def arguments():
    """
    Obtain the required arguments. 

    Returns
    -------
    args 
    """
    parser = argparse.ArgumentParser(description = "Automatic NCBI BLAST searches from a multiFASTA file. \
                             MultiFASTA can contain either nucleotide sequence or protein sequence. \
                            ./multiBLAST.py -p <driver-path> -d <in-path> -t <int> -o <out-path> -f nucletotide|protein \
                             Example of bash execution: \
                             ./multiBLAST.py -p driverpath/chromedriver -d myFastas/multiFasta.fa -t 4 -o myResults.txt -f nucletotide")
    parser.add_argument('-p', '--driverpath', dest='driverpath', 
                           action = 'store', required=False , 
                           help='The ChromeDriver path (Optional) Default path: chromedriver/chromedriver.')
    parser.add_argument('-d', '--dir', dest='in_file', 
                           action = 'store', required=True , 
                           help='MultiFASTA file.')
    parser.add_argument('-t', '--threads', dest='threads',
                       action = 'store', required=False,
                       help = 'Number of threads (Optional). Default value: 1.')
    parser.add_argument('-o', '--outfile', dest='out_file',
                       action = 'store', required=True,
                       help = 'Output file path')
    parser.add_argument('-f', '--format', dest='format',
                       action = 'store', required=True,
                       choices=['nucleotide', 'protein'],
                       help = 'Sequence type: "nucleotide" | "protein".')

    try:
        args = parser.parse_args()
        try:
            int(args.threads)
        except:
            print("\nNumber of threads must be an int value (-t <int>).")
            sys.exit()

        return args

    except:
        print("\nPlease, include the required arguments!")
        sys.exit()

def open_fasta(file_path):
    """
    Open the fasta file, read it and store int a dictionary the headers as keys and 
    the nucleotidic|aminoacidic sequences as values. 

    Parameters
    ----------
    file_path : str
        File path.

    Returns
    -------
    fasta_dic : dict
        Dictionary with the information of the fasta file.
    """
    fich_in = open(file_path, "r")
    fasta_dic = {}
    for line in fich_in:
        if line[0] == ">":
            name = line[1:].rstrip()
            fasta_dic[name] = [""]
        else:
            fasta_dic[name][0] += line.rstrip()

    return fasta_dic


def do_query_prot(protein, fasta_dic, driver_path):
    """
    Does the aminoacidic query sequence and store the results in the dictionary. 

    Parameters
    ----------
    protein : str
        Key of the fasta_dic dictionary.

    fasta_dic : dict
        Dictionary where the results are stored.

    driver_path : webdriver object.
        WebDriver objetc.

    Returns
    -------
    fasta_dic : dict
        Dictionary where the results are stored.
    """

    driver = webdriver.Chrome(driver_path)
    driver.get('https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastp&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome')
    query = fasta_dic[protein][0]
    driver.find_element(By.XPATH, '//*[@id="seq"]').send_keys(query)
    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/form/div[6]/div/div[1]/div[1]/input').click()
    timeout = 360 ## Max time waited until BLAST finished

    try:
        ## We add the arguments for EC.presence_of_element_located as a tupla
        element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="deflnDesc_1"]'))
        ## Wait until the following element appeare
        WebDriverWait(driver, timeout).until(element_present)
        description = driver.find_element(By.XPATH, '//*[@id="deflnDesc_1"]').text
        sc_name = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[3]/span/a').text
        max_score = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[6]').text
        tot_score = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[7]').text
        query_cover = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[8]').text
        e_value = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[9]').text
        per_ident = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[10]').text
        acc_len = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[11]').text

        ## Add results to the dic
        query_res = [description, sc_name, max_score, tot_score, query_cover, e_value, per_ident, acc_len]
        fasta_dic[protein].append(query_res)
        print("-> "+protein," finished")

    except TimeoutException:
        ## In case does not find similar sequences
        print("No significant similarity found for: "+protein)
        query_res = ["NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", ]
        fasta_dic[protein].append(query_res)

        ## In case an error ocurred
    except:
        print("An error with: "+protein+". Repeating the search...")
        fasta_dic[protein] = [fasta_dic[protein][0]]
        fasta_dic = do_query_prot(protein, fasta_dic, driver_path)

    driver.quit() ## Close the driver

    return fasta_dic


def do_query_nuc(protein, fasta_dic, driver_path):
    """
    Does the nucleotidic query sequence and store the results in the dictionary. 

    Parameters
    ----------
    protein : str
        Key of the fasta_dic dictionary.

    fasta_dic : dict
        Dictionary where the results are stored.

    driver_path : webdriver object.
        WebDriver objetc.

    Returns
    -------
    fasta_dic : dict
        Dictionary where the results are stored.
    """

    driver = webdriver.Chrome(driver_path)
    driver.get('https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastn&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome')
    query = fasta_dic[protein][0]
    driver.find_element(By.XPATH, '//*[@id="seq"]').send_keys(query)
    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/form/div[6]/div/div[1]/div[1]/input').click()
    timeout = 120 ## Max time waited until BLAST finished

    try:
        ## We add the arguments for EC.presence_of_element_located as a tupla
        element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="deflnDesc_1"]'))
        not_found_element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="noResMsg"]'))
        ## Wait until the following element appeare
        WebDriverWait(driver, timeout).until(element_present or not_found_element_present)
        description = driver.find_element(By.XPATH, '//*[@id="deflnDesc_1"]').text
        sc_name = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[3]/span/a').text
        max_score = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[6]').text
        tot_score = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[7]').text
        query_cover = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[8]').text
        e_value = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[9]').text
        per_ident = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[10]').text
        acc_len = driver.find_element(By.XPATH, '/html/body/main/section[2]/ul/li[1]/div/div[3]/form/div[3]/div/table/tbody/tr[1]/td[11]').text

        ## Add results to the dic
        query_res = [description, sc_name, max_score, tot_score, query_cover, e_value, per_ident, acc_len]
        fasta_dic[protein].append(query_res)
        print("-> "+protein," finished")

    except TimeoutException:
        ## In case does not find similar sequences
        print("No significant similarity found for: "+protein)
        query_res = ["NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", ]
        fasta_dic[protein].append(query_res)

    except:
        ## In case an error ocurred
        print("An error with: "+protein+". Repeating the search...")
        fasta_dic[protein] = [fasta_dic[protein][0]]
        fasta_dic = do_query_prot(protein, fasta_dic, driver_path)

    driver.quit() ## Close the driver

    return fasta_dic


def manage(list_protein, start, end, fasta_dic, driver_path, format):
    """
    Distribute all the amount of queries using threads. 

    Parameters
    ----------
    list_protein : list
        List with the headers of the multiFASTA.

    start : int
   
    end : int

    fasta_dic : dict
        Dictionary where the results are stored.

    driver_path : webdriver object.
        WebDriver objetc.
    
    format: str
        Either 'nucleotide' or 'protein' depending on the sequences of the multiFASTA. 

    Returns
    -------
    fasta_dic : dict
        Dictionary where the results are stored.
    """

    for tarea in range(start, end):
        protein = list_protein[tarea]
        if format == "protein":
            fasta_dic = do_query_prot(protein, fasta_dic, driver_path) ## Aminoacidic sequence query
        else:
            fasta_dic = do_query_nuc(protein, fasta_dic, driver_path) ## Nucleotidic sequence query

    return fasta_dic


def write_output(file_out, fasta_dic):
    """
    Write an output with the results obtained and storaged in fasta_dic.

    Parameters
    ----------
    file_out : str
        Path to write the output file. 

    fasta_dic : dict
        Dictionary where the results are stored.
    """

    fich_out = open(file_out, "w")

    fich_out.write("Header\tDescription\tScientific name\tMax score\tTotal score\tQuery cover\tE value \tPercentage identity \tAccession length\n")
    print("\nWriting results...")
    for i in fasta_dic.keys():
        fich_out.write(i+"\t")
        for j in fasta_dic[i][1]:
            fich_out.write(j+"\t")
        fich_out.write("\n")

    fich_out.close()


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
        path = os.getcwd()
        driver_path = path+'/SeleniumDriver/chromedriver'

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
