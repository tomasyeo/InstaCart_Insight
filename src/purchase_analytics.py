import csv
from functools import partial
import argparse
import logging
from datetime import datetime as dt


def open_inputfile(filename, func, tolerance):
    """
    A generic csv file reading function. Use partial function to handle each parsed csv row from
    a csv (comma separated) format file.
    :param filename: The path of the csv file to open.
    :param func: Use partial on a function to process the parsed csv row.
    :param tolerance: # of parsing errors to bypass before terminating prematurely.
    :return: None
    """
    try:
        with open(filename, encoding="utf8") as fh:
            sample = fh.read(1024)
            header = csv.Sniffer().has_header(sample)
            fh.seek(0)

            # Assume csv uses 'excel' dialect.
            print("Opening %s" % filename)
            logging.info("Opening %s" % filename)
            reader = csv.reader(fh, dialect='excel')

            # Skip first row if header exists.
            if header:
                next(reader)

            count = 0
            error_threshold = tolerance
            for row in reader:
                try:
                    func(row)
                except csv.Error as e:
                    # This exception handles csv parsing related issues, bypass the offending row,
                    # logs the exception for diagnostics, and resume parsing the next line.
                    errormsg = 'Error in {}, line {}: {}'.format(filename, reader.line_num, e)
                    print(errormsg)
                    logging.warning(errormsg)

                    # Threshold reduces by 1 for every parsing error. If errors exceed a defined count, this section
                    # will trigger a premature termination.
                    error_threshold -= 1
                    if error_threshold < 0:
                        errormsg = 'Parsing errors exceeding tolerance (%i) limit! ' \
                                   'Please check %s and try again. Terminating.' % (tolerance, filename)
                        print(errormsg)
                        logging.critical(errormsg)
                        exit(1)
                    else:
                        continue
                count += 1
            print("Processed %i rows." % count)
            logging.info("Processed %i rows." % count)
    except FileNotFoundError as e:
        # Deals with file not found.
        print('Error: File %s not found!' % filename)
        logging.critical('File %s not found!' % filename)
        exit(1)
    except Exception as e:
        # Handle other unknown exceptions.
        print('Error: File %s. %s' % (filename, e))
        logging.critical('Error: File %s. %s' % (filename, e))
        exit(1)


def get_product_dept_id(row, callback=None):
    """
    Read product.csv to get a dict of (product_id, department_id).
    :param row: A parsed row.
    :param callback: Provide a callback dict to store values.
    :return: None
    """
    try:
        prod_id, dept_id = int(row[0]), int(row[3])
        callback[prod_id] = dept_id
    except ValueError as e:
        # Let the caller handle the ValueError exception.
        raise csv.Error("Not an integer!")
    except Exception as e:
        # Handle other unknown exceptions.
        raise csv.Error(e)


def get_orders_by_dept(row, ref_dict=None, callback=None):
    """
    Read orders.csv to aggregate product orders by department.
    :param row: A parsed row.
    :param ref_dict: A dict of (product_id, department_id).
    :param callback: Provide a callback dict to store values.
    :return: None
    """
    try:
        prod_id, reordered = int(row[1]), int(row[3])
        dept_id = ref_dict[prod_id]
        callback[dept_id]['prod_count'] += 1

        # First time order is flagged as 0.
        if reordered is 0:
            callback[dept_id]['first_time_count'] += 1

    except ValueError:
        # Let the caller handle the ValueError exception.
        raise csv.Error("Not an integer!")
    except KeyError:
        # Handles KeyError exception from dict. Count towards tolerance limit.
        raise csv.Error("No Dept_ID corresponds to Prod_ID %i." % prod_id)
    except Exception as e:
        # Handle other unknown exceptions.
        print(e)
        raise csv.Error(e)

def summarize_orders_by_dept(tolerance, input_products=None, input_orders=None, output_filename=None):
    """
    Summarize product orders by department.
    :param tolerance: # of parsing errors to bypass before terminating prematurely.
    :param input_products: path to 'products' csv file to read.
    :param input_orders: path to 'orders' csv file to read.
    :param output_filename: path and/or filename of the output written out in csv.s
    :return: None
    """
    # Callback.
    dict_products_dept = {}
    # Get products' dept ID.
    open_inputfile(input_products, partial(get_product_dept_id, callback=dict_products_dept), tolerance)

    # Get a list of unique dept_id.
    dept_id = set([val for val in dict_products_dept.values()])
    # Init a callback for orders summary.
    dict_output = dict(map(lambda x: (x, {'prod_count': 0, 'first_time_count': 0}), dept_id))

    # Get orders summary grouped by dept ID.
    open_inputfile(input_orders, partial(get_orders_by_dept, ref_dict=dict_products_dept,
                                         callback=dict_output), tolerance)

    for i in dept_id:
        # Pop entry if dept has 0 prod_count.
        if dict_output[i]['prod_count'] == 0:
            dict_output.pop(i)
        else:
            # Calculate ratio.
            dict_output[i]['ratio'] = dict_output[i]['first_time_count'] / dict_output[i]['prod_count']

    # Export report to csv.
    if output_filename is not None:
        with open(output_filename, 'w', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            # Write headers first.
            headers = ['department_id', 'number_of_orders', 'number_of_first_orders', 'percentage']
            writer.writerow(headers)

            # Write each entry sorted by dept_id in ascending order.
            for i in sorted(dict_output):
                writer.writerow((i, dict_output[i]['prod_count'], dict_output[i]['first_time_count'],
                                 '{:.2f}'.format(dict_output[i]['ratio'])))

        print("Results output to %s." % output_filename)
        logging.info("Results output to %s." % output_filename)

    return dict_output

def main():
    # Log setup.
    logname = dt.now().strftime('%Y%m%d_%H%M') + '.log'
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        filename=logname, level=logging.DEBUG)
    logging.info("START!")

    desc = """\
        Insight InstaCart Coding Challenge!
        -----------------------------------
        This program takes two input files, order_products.csv & products.csv, in the input directory and generate 
        an output file, report.csv, in the output directory.
        
        The report file generates the following statistics for each department:
            number_of_orders: # of times a product was requested from this department
            number_of_first_orders: # of times a request is a first time order for a product
            percentage: the percentage of first time orders vs the total # of requests from a department
        """

    epilog = """\
        Usage
        -----------
        Provide source path to product.csv, order_products.csv and filename for output.
        Example: python purchase_analytics.py </path/products.csv> </path/order_products.csv> </path/output.csv>
        >   python purchase_analytics.py ./input/products.csv ./input/order_products.csv ./output/output.csv

        [Optional] Use --tolerance to specify the # of parsing errors to bypass before terminating program prematurely.
            Default limit: 100
        Example: python purchase_analytics.py -t 100 </path/products.csv> </path/order_products.csv> </path/output.csv>
        >   python purchase_analytics.py -t 100 ./input/products.csv ./input/order_products.csv ./output/output.csv

        """

    # Initialize argparser.
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=desc, epilog=epilog)
    parser.add_argument("product_file", help="Path to product.csv file.")
    parser.add_argument("orders_file", help="Path to order_products.csv file.")
    parser.add_argument("output", help="Output filename.")
    parser.add_argument("-t", "--tolerance", help="Error tolerance. default=100000000", default=100000000, type=int)

    # Parse arguments.
    args = parser.parse_args()

    # Exit program if required files are not provided.
    if args.product_file is not None and args.orders_file is not None and args.output is not None:
        # Run function.
        summarize_orders_by_dept(args.tolerance, args.product_file, args.orders_file, args.output)
    else:
        parser.print_usage()

    logging.info("END!")


if __name__ == '__main__':
    main()
