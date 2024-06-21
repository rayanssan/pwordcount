# pwordcount

- Synopsis:<br>
	`bash ./pwordcount [-h|help] [-m t|u|o] [-p n] files...`

- Description:<br>
<strong>pwordcount</strong> is a command-line program that performs word counting tasks on text files using multiprocessing. 
It supports three modes of operation: counting total words, counting unique words, and counting occurrences of each unique word. The program can divide 
the counting operations across multiple processes to handle a single file or multiple files efficiently.
 
- Arguments:
  - `m`: option that defines the counting mode (only one mode per execution)
    - `t`: counts the total words (default option)
    - `u`: counts the total number of unique/different words
    - `o`: counts the number of occurrences of each word in the input files<br>
  - `p`: option that defines the parallelization level
    - `n`: defines the number of allowed child processes (by default n=1)  
	- `h | help`: shows help information

- Example usage:
  - `./pwordcount -m t file1.txt`
  - `./pwordcount -p 2 -m u file2.txt`
  - `./pwordcount -m o -p 4 file2.txt file3.txt`
  - `./pwordcount -p 5 file2.txt`
  - `./pwordcount -m u file3.txt`
  - `./pwordcount file1.txt`
  - `./pwordcount file2.txt file3.txt file4.txt`
  - `./pwordcount -m t -p 1 file1.txt file2.txt file3.txt`
  - `./pwordcount -m o -p 4 file1.txt file2.txt. file3.txt file4.txt`
  - `./pwordcount help`

<strong>Developed by:</strong>
Rayan S. Santana
