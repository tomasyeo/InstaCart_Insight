import csv
from functools import partial

products = "d:/Users/tomas/Downloads/instacart_online_grocery_shopping_2017_05_01/products.csv"
orders = "d:/Users/tomas/Downloads/instacart_online_grocery_shopping_2017_05_01/order_products__train.csv"


def open_inputfile(filename, func):
    with open(filename, encoding="utf8") as fh:
        sample = fh.read(1024)
        # dialect = csv.Sniffer().sniff(sample)
        header = csv.Sniffer().has_header(sample)
        fh.seek(0)

        # Assume csv uses 'excel' dialect.
        reader = csv.reader(fh, dialect='excel', quoting=csv.QUOTE_ALL)

        # Skip first row if header exists, .
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
    try:
        prod_id, dept_id = int(row[0]), int(row[3])
        callback[prod_id] = dept_id
    except Exception as ex:
        # Let the caller handle the exception.
        raise ex


def get_orders_by_dept(row, ref_dict=None, callback=None):
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