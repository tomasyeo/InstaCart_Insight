import csv
from functools import partial
import argparse

products = "d:/Users/tomas/Downloads/instacart_online_grocery_shopping_2017_05_01/products.csv"
orders = "d:/Users/tomas/Downloads/instacart_online_grocery_shopping_2017_05_01/order_products__train.csv"


def open_inputfile(filename, func):
    """

    :param filename: The path of the csv file to open.
    :param func: Use partial on a function to process the parsed csv row.
    :return: Nones
    """
    with open(filename, encoding="utf8") as fh:
        sample = fh.read(1024)
        header = csv.Sniffer().has_header(sample)
        fh.seek(0)

        # Assume csv uses 'excel' dialect.
        reader = csv.reader(fh, dialect='excel', quoting=csv.QUOTE_ALL)

        # Skip first row if header exists.
        if header:
            next(reader)

        try:
            for row in reader:
                try:
                    func(row)
                except Exception as ex:
                    print(ex)
                    continue
        except Exception as ex:
            print(ex)
        finally:
            # Make sure the filehandler is closed at the end of a bad event.
            fh.close()


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
    except Exception as ex:
        # Let the caller handle the exception.
        raise ex


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
        # print(dept_id)
        # if isinstance(callback, dict):
        #    dict_products_dept.geta
        callback[dept_id]['prod_count'] += 1
        if reordered is 1:
            callback[dept_id]['reordered_count'] += 1

    except Exception as e:
        raise e


def summarize_orders_by_dept(input_products=None, input_orders=None, output_filename=None):
    """
    Summarize product orders by department.
    :param input_products: path to 'products' csv file to read.
    :param input_orders: path to 'orders' csv file to read.
    :param output_filename: path and/or filename of the output written out in csv.s
    :return: None
    """
    # Callback.
    dict_products_dept = {}
    # Get products' dept ID.
    open_inputfile(input_products, ft.partial(get_product_dept_id, callback=dict_products_dept))

    # Get a list of unique dept_id.
    dept_id = set([val for val in test.values()])
    # Init a callback for orders summary.
    dict_output = dict(map(lambda x: (x, {'prod_count': 0, 'reordered_count': 0}), dept_id))

    # Get orders summary grouped by dept ID.
    open_inputfile(input_orders, partial(get_orders_by_dept, ref_dict=dict_products_dept, callback=dict_output))

    for i in dept_id:
        # Pop entry if dept has 0 prod_count.
        if dict_output[i]['reordered_count'] == 0:
            dict_output.pop(i)
        else:
            # Calculate ratio.
            dict_output[i]['ratio'] = dict_output[i]['reordered_count'] / dict_output[i]['prod_count']

    # Export report to csv.
    if output_filename is not None:
        with open(output_filename, 'w', encoding='utf-8') as fh:
            try:
                writer = csv.writer(fh)
                # Write headers first.
                headers = ['department_id', 'number_of_orders', 'number_of_first_orders', 'percentage']
                writer.writerow(headers)

                # Write each entry sorted by dept_id in ascending order.
                for i in sorted(dict_output):
                    writer.writerow((i, dict_output[i]['prod_count'], dict_output[i]['reordered_count'],
                                     '{:.3f}'.format(dict_output[i]['ratio'])))
            except csv.Error as e:
                print('file {}, line {}: {}'.format(filename, reader.line_num, e))

    return dict_output

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     help="Link files by hard or symbolic link.",
                                     description=desc, epilog=epilog)

    desc = """\
        Link files by hard or symbolic link.
        """

    epilog = """\
        Basic Usage
        -----------
        Provide source path to product.csv and order_products.csv.
        Example: pipeline_link.py <sourcefile> <target path>

        [Optional] Use symbolic link instead of hard link.
        Example: pipeline_link.py -s <sourcepath> <target path>
        >   pipeline_link.py -s /path/file.txt /target_path

        """

    parser.add_argument("product_file", help="Path to product.csv file.")
    parser.add_argument("orders_file", help="Path to order_products.csv file.")
    parser.add_argument("-o", "--output", help="Output filename. Default: report.csv", default="report.csv")

    # Parse arguments.
    args = parser.parse_args()

    if args.product_file is not None and args.orders_file is not None:
        summarize_orders_by_dept(args.product_file, args.orders_file, args.output)
    else:
        parser.print_usage()

    pass


if __name__ == '__main__':
    main()
