import sys
import multiprocessing
import os
import subprocess
from collections import Counter


def calc_size(file: str) -> int:
    """
    Returns the size in bytes of a given file

    Requires:
    file (str): str indicating a text file's directory.
    Ensures:
    Returning the bytes size of a given file as an integer.
    """
    return os.path.getsize(file)


def divide_one_file(file: str, num_processes: int, auxiliaryFunction: callable, words_count:  multiprocessing.Value) -> None:
    """
    Divides a single text file by its size and processes it using multiple processes, 
    accumulating the results of the lines and words of its parts processed.

    Requires:
    file (str): str indicating a text file's directory
    num_processes (int): The number of processes to use for parallel processing.
    auxiliaryFunction (callable): One of the three functions that handle the given modes of pwordcount: "t_words", "u_words", or "o_words".
    words_count (multiprocessing.Value): A shared variable to accumulate the total word count, used by t_words and u_words.
    Ensures:
    Dividing a text file into specified chunks and processing chunks in parallel, accumulating results, 
    and printing the results for the given mode.
    """

    # Get the size of the file
    file_size = calc_size(file)

    # Calculate the size of each chunk
    chunk_size = file_size // num_processes

    processes = []

    for i in range(num_processes):
        # Calculate the start and end lines for this chunk
        start_line = i * chunk_size if i != 0 else 1
        end_line = (i + 1) * chunk_size

        # Create a new process for each chunk
        if (auxiliaryFunction == t_words):
            # If the given mode is t, subprocess will handle the creation of processes.
            t_words(file, start_line, end_line, words_count)
        else:
            process = multiprocessing.Process(target=auxiliaryFunction, args=(
                file, start_line, end_line, words_count))
            process.start()
            processes.append(process)

    for process in processes:
        process.join()

    if (auxiliaryFunction == t_words):
        print(
            f'The file "{file}" has {words_count.value} words, and a total size of {file_size} bytes.')
    elif (auxiliaryFunction == u_words):
        print(
            f'The file "{file}" has {words_count.value} unique words, and a total size of {file_size} bytes.')
    else:
        print("• End of list •")
        print(f'Size of "{file}": {file_size} bytes.')


def divide_between(files: list, num_processes: int, auxiliaryFunction: callable) -> None:
    """
    Generates individual processes for every file in a specified list of files, 
    dispatching them for parallel execution when a sufficient number of processes are available,
    or queuing them when if the number of processes are less than that of files.
    Printing of the results is then handled by the given auxiliary function.

    Requires:
    files (list): A list of file paths, in str, to be processed.
    num_processes (int): The number of processes available to use.
    auxiliaryFunction (callable): One of the three auxiliary functions that handle the given modes of pwordcount: "t", "u", or "o".
    Ensures:
    Processing each of the given files, with one process for each file if processes are enough, or queuing them otherwise,
    and sending them off for handling by the auxiliary functions which will then print the requested data.
    """
    if num_processes == 1:
        print(f"Using 1 process")
    elif num_processes > len(files):
        # More processes than files, equalize processes to number of files
        print(f"Using {len(files)} process")
        num_processes = len(files)
    else:
        print(f"Using {str(num_processes)} processes")

    file_queue = multiprocessing.Queue()

    if len(files) > num_processes:
        # Less processes than files, tasks will be queued
        print("Number of files greater than number of processes, tasks will be queued")
        
        # Sort files by size, so that the bigger files get processed first
        sorted_files_by_size = sorted(files, key=lambda file: calc_size(file), reverse=True)

        for file in sorted_files_by_size:
            file_queue.put(file)
    else:
        for file in files:
            file_queue.put(file)

    print()

    processes = []
    for _ in range(num_processes):
        if (auxiliaryFunction == "t_words"):
            # If the given mode is t, subprocess will handle the creation of processes.
            t_words(file_queue)
        else:
            process = multiprocessing.Process(
                target=auxiliaryFunction, args=(file_queue,))
            process.start()
            processes.append(process)

    for process in processes:
        process.join()


def t(file_queue: list) -> None:
    """
    Executes mode -m t.
    It uses subprocess to run an external bash shell command in a new process and capture its output.

    Requires:
    file_queue (list): A list of file paths (str) in queue to be processed.
    Ensures:
    Performing the code for calculating the number of words in a text file in the bash shell.
    """
    while not file_queue.empty():
        file = file_queue.get()
        words = subprocess.run(f"cat '{file}' | wc -w", shell=True, text=True, stdout=subprocess.PIPE).stdout.strip()
        print(
            f'The file "{file}" has {words} words, and a total size of {calc_size(file)} bytes.')


def t_words(file: str, start_line: int, end_line: int, words_count: multiprocessing.Value) -> None:
    """
    Auxiliary function of divide_one_file, which is called when pwordcount receives a single file.
    It uses subprocess to run an external bash shell command in a new process and capture its output.

    Requires:
    file (str): str indicating a text file's directory
    start_line (int): The starting line number for word counting.
    end_line (int): The ending line number for word counting.
    words_count (multiprocessing.Value): A shared variable to accumulate the total word count, used by t_words and u_words.
    Ensures:
    This function calculates the number of words in a specified range of lines (between start_line and end_line) within a text file and updates the total word count.
    """
    words = subprocess.run(f"sed -n {start_line},{end_line}p {file} | wc -w", shell=True, text=True, stdout=subprocess.PIPE).stdout.strip()
    words_count.value += int(words)


def u(file_queue: list) -> None:
    """
    Executes mode -m u

    Requires:
    file_queue (list): A list of file paths (str) in queue to be processed.
    Ensures:
    Performing the code for calculating the number of unique/different words in a text file in the bash shell.
    """
    while not file_queue.empty():
        file = file_queue.get()
        unique_words = set()
        with open(file, 'r') as f:
            for line in f:
                words = line.split()
                unique_words.update(words)

        print(
            f'The file "{file}" has {len(unique_words)} unique words, and a total size of {calc_size(file)} bytes.')


def u_words(file: str, start_line: int, end_line: int, words_count: multiprocessing.Value) -> int:
    """
    Auxiliary function of divide_one_file, which is called when pwordcount receives a single file.

    Requires:
    file (str): str indicating a text file's directory
    start_line (int): The starting line number for word counting.
    end_line (int): The ending line number for word counting.
    words_count (multiprocessing.Value): A shared variable to accumulate the total word count, used by t_words and u_words.
    Ensures:
    This function calculates the number of unique/different 
    words in a specified range of lines (between start_line and end_line) within a text file and updates the total word count.
    """
    unique_words = set()
    lines_processed = 0

    with open(file, 'r') as f:
        for line_num, line in enumerate(f, start=1):
            if start_line <= line_num < end_line:
                # Process a line located in the specified range
                words = line.split()
                unique_words.update(words)
                lines_processed += 1

    words_count.value += len(unique_words)


def o(file_queue: list) -> None:
    """
    Executes mode -m o

    Requires:
    file_queue (list): A list of file paths (str) in queue to be processed.
    Ensures:
    Performing the code for calculating the number of occurrences of each of the
    unique/different words in a text file in the bash shell.
    """
    while not file_queue.empty():
        file = file_queue.get()
        word_counts = Counter()
        with open(file, 'r') as f:
            for line in f:
                words = line.split()
                word_counts.update(words)

        print(f'Number of occurrences of each word in "{file}":')
        for word, occurences in word_counts.items():
            if (occurences == 1):
                print(f"{word}: {occurences} time")
            else:
                print(f"{word}: {occurences} times")
        print("• End of list •")
        print(f'Size of "{file}": {calc_size(file)} bytes.')


def o_words(file: str, start_line: int, end_line: int, words_count: multiprocessing.Value) -> None:
    """
    Auxiliary function of divide_one_file, which is called when pwordcount receives a single file.
    Processes a text file, counts the occurrences of each word in the file, and prints the results.

    Requires:
    file (str): str indicating a text file's directory
    start_line (int): The starting line number for word counting.
    end_line (int): The ending line number for word counting.
    words_count (multiprocessing.Value): A shared variable to accumulate the total word count, used by t_words and u_words.
    Ensures: This function calculates the number of occurrences of 
    each of the unique/different words in a specified range of lines (between start_line and end_line) 
    within a text file and updates the total word count.
    """
    word_counts = Counter()
    lines_processed = 0

    with open(file, 'r') as f:
        for line in f:
            words = line.split()[start_line:end_line]
            word_counts.update(words)
            lines_processed += 1

    if start_line == 1:
        print(f'Number of occurrences of each word in "{file}":')
    for word, occurences in word_counts.items():
        if (occurences == 1):
            print(f"{word}: {occurences} time")
        else:
            print(f"{word}: {occurences} times")


def main(args: list, words_count: multiprocessing.Value) -> None:
    """
    Handles execution of pwordcount, its command-line arguments,
    and attribution of processes.

    Requires:
    args (list): A list of command-line arguments.
    words_count (multiprocessing.Value): A shared variable to accumulate word counts, which are made by the modes -m t and -m u.
    Ensures:
    Interpreting command-line arguments and counting the words in the .txt file
    passed as argument in the command line, either in a single process or
    several, based on the provided options. By default, if no arguments other than
    the name of the .txt file are given, only a single process is used.
    Options:
    -m t: Perform pwordcount to count the total number of words.
    -m u: Perform pwordcount to count the number of unique/different words.
    -m o: Perform pwordcount to count the number of occurences of each of the unique/different words.
    -p n: Execute pwordcount using n processes.
    Example Usage:
    To perform pwordcount in a single .txt file using a single process:
    >>> main(["your_file.txt"])
    To perform pwordcount in two txt. files
    to count the number of unique/different words using 4 processes:
    >>> main(["-m", "u", "-p", "4", "your_file.txt", "your_other_file.txt"])
    """

    print('Programa: pwordcount.py')
    print('Argumentos: ', args)

    # --- Argument meanings ----

    # Could be equal to "-m", "-p", or else the first given file path
    if (args[0] == "-m" or args[0] == "-p"):
        FIRST_ARGUMENT = args[0]
        FIRST_ARGUMENT_AND_ON = None
    else:
        # If args[0] is not equal to -m or -p args[0:] will be a list of file paths
        FIRST_ARGUMENT_AND_ON = args[0:]
        FIRST_ARGUMENT = args[0]
    if (len(args) >= 0):
        # If FIRST_ARGUMENT == "-m", this will correspond to one of the
        # three modes that can chosen t, u, or o;
        # Else if FIRST_ARGUMENT == "-p", this will correspond to a positive int n of allowed processes;
        # Else if FIRST_ARGUMENT is a file path this will be a second file path
        try:
            SECOND_ARGUMENT = args[1]
        except IndexError:
            SECOND_ARGUMENT = None
    if (len(args) >= 1):
        # If FIRST_ARGUMENT == "-m" and SECOND_ARGUMENT == "t" or "u" or "o", this might
        # be equal to "-p", otherwise it will be the first given file path;
        # Else if FIRST_ARGUMENT == "-p" and SECOND_ARGUMENT == n, where n is a positive int,
        # this might be equal to "-m", otherwise it will be the first given file path;
        # Else if FIRST_ARGUMENT and SECOND_ARGUMENT are file paths this will be a third file path
        try:
            if (args[2] == "-p" or args[2] == "-m"):
                THIRD_ARGUMENT = args[2]
                THIRD_ARGUMENT_AND_ON = None
            else:
                # If args[2] is not equal to -p or -m args[2:] will be a list of file paths
                THIRD_ARGUMENT_AND_ON = args[2:]
                THIRD_ARGUMENT = args[2]
        except IndexError:
            THIRD_ARGUMENT = None
            THIRD_ARGUMENT_AND_ON = None
    if (len(args) >= 2):
        # If FIRST_ARGUMENT == "-m", SECOND_ARGUMENT == "t" or "u" or "o"
        # and THIRD_ARGUMENT == "-p", this will correspond to a positive int n of allowed processes;
        # Else if FIRST_ARGUMENT == "-m", SECOND_ARGUMENT == "t" or "u" or "o", and THIRD_ARGUMENT is a file path,
        # this will be a second file path;
        # Else if FIRST_ARGUMENT == "-p", SECOND_ARGUMENT == n, where n is a positive int,
        # and THIRD_ARGUMENT == "-m", this will correspond to one of the
        # three modes that can chosen t, u, or o;
        # Else if FIRST_ARGUMENT == "-p", SECOND_ARGUMENT == n, where n is a positive int, and THIRD_ARGUMENT is a file path,
        # this will be a second file path;
        # Else if FIRST_ARGUMENT, SECOND_ARGUMENT, and THIRD_ARGUMENT are file paths,
        # this will be a fourth file path;
        try:
            FOURTH_ARGUMENT = args[3]
        except IndexError:
            FOURTH_ARGUMENT = None
    if (len(args) >= 3):
        # Will always be a file path
        # If FIRST_ARGUMENT == "-m", SECOND_ARGUMENT == "t" or "u" or "o", THIRD_ARGUMENT == "-p",
        # and FOURTH_ARGUMENT == n, where n is a positive int, this will correspond to the first given file path;
        # Else if FIRST_ARGUMENT == "-p", SECOND_ARGUMENT == n, where n is a positive int,
        # THIRD_ARGUMENT == "-m", FOURTH_ARGUMENT == "t" or "u" or "o", this will correspond to the first given file path;
        # Else if FIRST_ARGUMENT == "-m", SECOND_ARGUMENT == "t" or "u" or "o", and THIRD_ARGUMENT and
        # FOURTH_ARGUMENT are a file paths, this will be a third file path;
        # Else if FIRST_ARGUMENT == "-p", SECOND_ARGUMENT == n, where n is a positive int, and THIRD_ARGUMENT and
        # FOURTH_ARGUMENT are a file paths, this will be a third file path;
        # Else if FIRST_ARGUMENT, SECOND_ARGUMENT, THIRD_ARGUMENT, and FOURTH_ARGUMENT are file paths,
        # this will be a fifth file path;
        try:
            # args[4:] will be a list of file paths
            FIFTH_ARGUMENT_AND_ON = args[4:]
        except IndexError:
            FIFTH_ARGUMENT_AND_ON = None

    if FIRST_ARGUMENT:
        if len(FIRST_ARGUMENT) == 1 or (len(FIRST_ARGUMENT) == 2 and FIRST_ARGUMENT != "-m" and FIRST_ARGUMENT != "-p"):
            print("Error: invalid command")
            sys.exit()
    if THIRD_ARGUMENT_AND_ON:
        if FIRST_ARGUMENT == FOURTH_ARGUMENT:
            print("Error: invalid command")
            sys.exit()

    if FIRST_ARGUMENT == "-m":
        # Option -m t
        if SECOND_ARGUMENT == "t":
            if THIRD_ARGUMENT == "-p":
                files = FIFTH_ARGUMENT_AND_ON
                num_processes = int(FOURTH_ARGUMENT)
                if len(files) > 1 or num_processes == 1:
                    # If we have more than one file, do not divide files individually
                    divide_between(files, num_processes, t)
                else:
                    # Else we have one file, and only one file, divide files individually
                    print(f"Using {str(num_processes)} processes")
                    if (num_processes != 1):
                        print(
                            "File contents were divided between the given processes")
                    print()
                    divide_one_file(
                        files[0], num_processes, t_words, words_count)

            else:
                # Use a single process
                files = THIRD_ARGUMENT_AND_ON
                divide_between(files, 1, t)
        # Option -m u
        if SECOND_ARGUMENT == "u":
            if THIRD_ARGUMENT == "-p":
                files = FIFTH_ARGUMENT_AND_ON
                num_processes = int(FOURTH_ARGUMENT)
                if len(files) > 1 or num_processes == 1:
                    # If we have more than one file, do not divide files individually
                    divide_between(files, num_processes, u)
                else:
                    # Else we have one file, and only one file, divide files individually
                    print(f"Using {str(num_processes)} processes")
                    if (num_processes != 1):
                        print(
                            "File contents were divided between the given processes")
                    print()
                    divide_one_file(
                        files[0], num_processes, u_words, words_count)
            else:
                # Use a single process
                files = THIRD_ARGUMENT_AND_ON
                divide_between(files, 1, u)
        # Option -m o
        if SECOND_ARGUMENT == "o":
            if THIRD_ARGUMENT == "-p":
                files = FIFTH_ARGUMENT_AND_ON
                num_processes = int(FOURTH_ARGUMENT)
                if len(files) > 1 or num_processes == 1:
                    # If we have more than one file, do not divide files individually
                    divide_between(files, num_processes, o)
                else:
                    # Else we have one file, and only one file, divide files individually
                    print(f"Using {str(num_processes)} processes")
                    if (num_processes != 1):
                        print(
                            "File contents were divided between the given processes")
                    print()
                    divide_one_file(
                        files[0], num_processes, o_words, words_count)
            else:
                # Use a single process
                files = THIRD_ARGUMENT_AND_ON
                divide_between(files, 1, o)
    # Option -p
    elif FIRST_ARGUMENT == "-p":
        num_processes = int(SECOND_ARGUMENT)
        if THIRD_ARGUMENT == "-m":
            files = FIFTH_ARGUMENT_AND_ON
            # Option -p n -m t
            if FOURTH_ARGUMENT == "t":
                if len(files) > 1 or num_processes == 1:
                    # If we have more than one file, do not divide files individually
                    divide_between(files, num_processes, t)
                else:
                    # Else we have one file, and only one file, divide files individually
                    print(f"Using {str(num_processes)} processes")
                    if (num_processes != 1):
                        print(
                            "File contents were divided between the given processes")
                    print()
                    divide_one_file(
                        files[0], num_processes, t_words, words_count)
            # Option -p n -m u
            if FOURTH_ARGUMENT == "u":
                if len(files) > 1 or num_processes == 1:
                    # If we have more than one file, do not divide files individually
                    divide_between(files, num_processes, u)
                else:
                    # Else we have one file, and only one file, divide files individually
                    print(f"Using {str(num_processes)} processes")
                    if (num_processes != 1):
                        print(
                            "File contents were divided between the given processes")
                    print()
                    divide_one_file(
                        files[0], num_processes, u_words, words_count)
            # Option -p n -m o
            if FOURTH_ARGUMENT == "o":
                # If we have more than one file, do not divide files individually
                if len(files) > 1 or num_processes == 1:
                    divide_between(files, num_processes, o)
                else:
                    # Else we have one file, and only one file, divide files individually
                    print(f"Using {str(num_processes)} processes")
                    if (num_processes != 1):
                        print(
                            "File contents were divided between the given processes")
                    print()
                    divide_one_file(
                        files[0], num_processes, o_words, words_count)
        else:
            files = THIRD_ARGUMENT_AND_ON
            # If we have more than one file, do not divide files individually
            if len(files) > 1 or num_processes == 1:
                divide_between(files, num_processes, t)
            else:
                # Else we have one file, and only one file, divide files individually
                print(f"Using {str(num_processes)} processes")
                if (num_processes != 1):
                    print("File contents were divided between the given processes")
                print()
                divide_one_file(
                    files[0], num_processes, t_words, words_count)
    # If no options are given
    else:
        # Use a single process and mode -m t
        files = FIRST_ARGUMENT_AND_ON
        divide_between(files, 1, t)


if __name__ == "__main__":
    # Shared words count
    words_count = multiprocessing.Value('i', 0)
    # Call main function
    main(sys.argv[1:], words_count)
