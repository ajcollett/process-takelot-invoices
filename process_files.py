import pyManager as pm

__author__ = 'Andrew James Collett'


def is_num(ref):
    try:
        int(ref)
        return True
    except:
        return False


def get_manager_info(host, user, business):

    manager_object = pm.manager_object(host, user, business)
    customers = manager_object.get_customers()
    sales_invoices = manager_object.get_sales_invoices()
    tracking_codes = manager_object.get_tracking_codes()
    bank_accounts = manager_object.get_cash_accounts()
    inventory_items = manager_object.get_inventory()
    accounts = manager_object.get_profit_loss_accounts()

    # emails = list()
    # refs = list()
    #
    # for customer in customers:
    #     emails.append(customer['Email'])
    #
    # for invoice in invoices:
    #     refs.append(invoice['Reference'])
    #
    # return emails, refs


def create_invoices_dict(invoices, OrderID, Date, Title, Qty, Price, Email,
                         m_emails):

    if is_num(OrderID):
        if Email in m_emails:
            print Email + ' is in Manager already'
        else:
            try:
                invoices[OrderID]['items'].append([Title, Qty])

            except (IndexError, KeyError):
                invoices[OrderID] = {'ref': OrderID, 'date': Date,
                                     'price': Price, 'email': Email,
                                     'name': '', 'quantity': Qty,
                                     'transactions': {},
                                     'items': [[Title, Qty]]}


def add_to_dict(invoices, T_Dt, T_Tp, T_ID, T_Des, Cus,
                Ref_Tp, Ref, Ex_VAT, VAT, In_VAT, Bal, m_refs):

    try:
        ref = Ref.split()[2].replace(')', '').strip()
        if is_num(ref):
            if ref in m_refs:
                print ref + ' is in Manager already'
            else:
                try:
                    invoices[str(ref)]['name'] = Cus
                    num_transactions = len(invoices[ref]['transactions']) + 1
                    invoices[ref]['transactions'][num_transactions] = {
                        'date': T_Dt, 'type': T_Tp, 'description': T_Des,
                        'amount': In_VAT}
                except (KeyError) as e:
                    print "This key is not in the dictionary", e

    except IndexError as e:
        return


def get_data(invoice_file, statement_file, m_emails, m_refs):
    invoices = {}
    [create_invoices_dict(invoices, OrderID, Date, Title, Qty, Price, Email,
                          m_emails)
     for OrderID, Date, Title, Qty, Price, Email in
        [line.strip().split(',') for line in invoice_file]]

    [add_to_dict(invoices, T_Dt, T_Tp,
                 T_ID, T_Des, Cus, Ref_Tp, Ref, Ex_VAT, VAT, In_VAT, Bal,
                 m_refs) for
     T_Dt, T_Tp, T_ID, T_Des, Cus, Ref_Tp, Ref, Ex_VAT, VAT, In_VAT, Bal in
     [line.strip().split(',') for line in statement_file]]

    return invoices


def __main__():
    user = 'api'
    host = 'https://manager.procsum.co.za'
    # invoice_file = open('invoice.csv', 'r')
    # statement_file = open('statement.csv', 'r')
    # inv_proc = open('process.csv', 'w')
    # customers = open('customers.csv', 'w')

    # m_emails, m_refs = get_manager_info(host, user, 'ProcSum')
    get_manager_info(host, user, 'ProcSum')

    # invoices = get_data(invoice_file, statement_file, m_emails, m_refs)

    # keys = invoices.keys()
    # keys.sort()
    # keys.reverse()

    # customers.write('Name	Email' + '\n')

    # for key in keys:
    #     write_files(invoices[key], inv_proc, customers)


if __name__ == "__main__":
    __main__()

"""
def write_files(order, inv_proc, customers):

    transs = order['transactions']

    inv_proc.write(str(
        order['ref'] + ',' + order['date'] + ',' +
        order['name'] + ',' + order['email'] + '\n'))

    customers.write(str(order['name'] + '	' + order['email'] + '\n'))

    for item in order['items']:
        inv_proc.write(',' + order['date'] +
                       ',,' + item[0] + ',' + item[1] + '\n')

    for key in transs:
        trans = transs[key]
        if 'Storage Fee' not in trans['description']:
            inv_proc.write(str(
                trans['date'] + ',' + order['date'] + ',' +
                trans['type'] + ',' + trans['description'] + ',' +
                trans['amount'] + '\n'))

    inv_proc.write('\n')

def get_manager_info(host, user, business):
    nav_path_customers = [business, 'Customer']
    nav_path_invoices = [business, 'SalesInvoice']

    gom = manager.manager_objects(host, user)
    customers = gom.get_json_object(nav_path_customers)
    invoices = gom.get_json_object(nav_path_invoices)

    emails = list()
    refs = list()

    for customer in customers:
        emails.append(customer['Email'])

    for invoice in invoices:
        refs.append(invoice['Reference'])

    return emails, refs


"""
