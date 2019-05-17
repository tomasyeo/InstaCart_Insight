# InstaCart_Insight
###### Coder: Tomas Yeo
###### Email: tomas.yeo@outlook.com
###### github: https://github.com/tomasyeo/InstaCart_Insight
###### Purpose: Coding challenge for Insight data engineering fellowship program
###### Submission date: 3 Apr 2019


Insight coding challenge March 2019
-----------------------------------

Introduction
------------
This program takes two input files, order_products.csv & products.csv, from the input directory
and generate an output file, report.csv, in the output directory.


Requirements
------------
Just good old python 3 primitives and base libraries.
No external dependencies required.


Usage
-----
Provide source path to product.csv, order_products.csv and filename for output.
Example: python purchase_analytics.py </path/products.csv> </path/order_products.csv> </path/output.csv>
>   python purchase_analytics.py ./input/products.csv ./input/order_products.csv ./output/output.csv

[Optional] Use --tolerance to specify the # of parsing errors (threshold) to bypass before terminating
    program prematurely. It would be ideal to set the threshold to approximately 5 to 10% of the # of lines
    in a csv file to bypass parsing errors

    Default limit: 100
Example: python purchase_analytics.py -t 100 </path/products.csv> </path/order_products.csv> </path/output.csv>
>   python purchase_analytics.py -t 100 ./input/products.csv ./input/order_products.csv ./output/output.csv


Outputs
-------
The program generates a report file into ./output/ folder.

This file contains the following statistics for each department with the following fields:
    number_of_orders: # of times a product was requested from this department
    number_of_first_orders: # of times a request is a first time order for a product
    percentage: the percentage of first time orders vs the total # of requests from a department

Run logs are also generated for every run with the naming convention, 'YYYYMMDD_HHmm.log'. Each log
contains benign run information (if parsing runs smoothly without unfortunate events), warnings for
csv parsing related issues and other unforeseeable critical unhandled exceptions that may be encountered
during runtime.

It is strongly recommended to glance at the run logs to ensure no lines are omitted.


Testsuite
---------
These are the tests to run:
1. test_1_generic: Generic test. Outcome: program functions as normal.
    Expected test result is PASS.
2. test_2_malformed_lines_within_limits: Testing if a malformed line with value in a key column as string
    is omitted as bad type. Outcome: program will bypass the parsing error and resumes to next line.
    Expected test result is PASS.
3. test_3_csv_sniffer_error: Any malformed line within the first 1024 bytes will cause csvreader to terminate.
    Outcome: program will terminate
    Expected test result is FAIL.
4. test_4_malformed_lines_over_limits: Tolerance is set to omit 3 parsing errors. Test to ensure program will
    terminate prematurely when more than 3 malformed lines are parsed. Outcome: program will terminate.
    Expected test result is FAIL.
5. test_5_prodID_deptID_mismatch: Product ID cannot find a corresponding Department ID from product.csv.
    Testing to find out these mismatches handled as malformed lines will trigger a premature termination.
    Outcome: program will terminate. Expected test result is FAIL.


Design
------
The specification requests for a csv parser specifically designed to read product.csv and order_products.csv
files. A simple parser should not take up a lot of memory or cpu cycles. Instead of reading the whole file
into a list, each line is parsed and processed within one file read iteration. Line processing functions are
customized to process each line in product.csv and order_products.csv respectively, in their respective file
read iteration as a Partial method that acts as a delegate.

One useful feature added is the logging. It keeps track of malformed lines that fail to parse, or cannot be
processed due to bad type. It also records unexpected runtime exceptions that may occur during parsing. Tolerance,
is an error threshold which sets the number of malformed lines to omit before terminating prematurely. The reason
is that, the whole exercise to process a file to obtain some form of useful information is totally irrelevant if
majority of lines in the file si malformed. In this case, one should investigate the file, scrub the data if
necessary, before running it again. The default value is set to 100000000. User will require to lower the value
as appropriate, typically 5% - 10% of the total expected lines in the file.

One feature not implemented is to check for duplicated entries in order_products.csv. Although one can always
assume the data is dumped from a database that conform to good database design practices, it is always safe to
ensure every entry n each order are unique.

