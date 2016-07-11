#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A large script to do a simple job, enter invoices into Manager."""
import pyManager as pm
import pprint

__author__ = 'Andrew James Collett'
log_file = open('log.txt', 'w')

acounts = {'SalesInvoiceReceipt': 'd1489e95-bb28-4f5d-b42e-67d3291b3893'}


def is_num(ref):
    """Check if the ref is a number."""
    try:
        int(ref)
        return True
    except:
        return False


def get_manager_info(host, user, business):
    """Get managers info, including static info and lists of info."""
    static_info = dict()

    manager_object = pm.manager_object(host, user, business)

    sales_items = manager_object.get_inventory()
    sales_items_new = dict()
    for item_ref in sales_items:
        item = dict()
        item = sales_items[item_ref]
        item['Code'] = item_ref
        # sales_items_new[sales_items[item_ref]['Code']] = {
        #     'Id': item_ref,
        #     'Description': sales_items[item_ref]['Description'],
        # }

    sales_items = sales_items_new
    log_file.write('We got sales Items\n')

    track_codes = manager_object.get_tracking_codes()
    for code_ref in track_codes:
        if 'takealot sales' in track_codes[code_ref]['Name']:
            static_info['tracking_code'] = code_ref

    log_file.write('We got tracking code: ' + static_info['tracking_code'] +
                   '\n')

    bank_acc = manager_object.get_cash_accounts()
    for account_ref in bank_acc:
        if ('takealot seller account' in bank_acc[account_ref]['Name']):
            static_info['bank_account'] = account_ref

    log_file.write('We got bank account: ' + static_info['bank_account'] +
                   '\n')

    accounts = manager_object.get_profit_loss_accounts()
    for prof_los_account_ref in accounts:
        if ('takealot Success fee' in accounts[prof_los_account_ref]['Name']):
            static_info['success_fee'] = prof_los_account_ref
        if ('takealot Handling fee' in accounts[prof_los_account_ref]['Name']):
            static_info['handling_fee'] = prof_los_account_ref

    log_file.write('We got success and handling fee: ' +
                   static_info['success_fee'] +
                   ' ' + static_info['handling_fee'] + '\n')

    customers = manager_object.get_customers()
    sales_invoices = manager_object.get_sales_invoices()

    return(manager_object, customers, sales_invoices, sales_items, static_info)


def create_invoices_dict(invoices, OrderID, Date, Title, Qty, Price, Email,
                         m_refs):
    """Create the Invoices dict and add details to it."""
    if is_num(OrderID):
        if OrderID in m_refs:
            log_file.write(Email + ' is in Manager already\n')
        else:
            try:
                invoices[OrderID]['items'].append([Title, Qty, Price])

            except (IndexError, KeyError):
                invoices[OrderID] = {'ref': OrderID, 'date': Date,
                                     'price': Price, 'email': Email,
                                     'name': '', 'quantity': Qty,
                                     'transactions': {},
                                     'items': [[Title, Qty, Price]]}


def add_to_dict(invoices, T_Dt, T_Tp, T_ID, T_Des, Cus,
                Ref_Tp, Ref, Ex_VAT, VAT, In_VAT, Bal, m_refs):
    """Add the details to the Invoices dict."""
    try:
        ref = Ref.split()[2].replace(')', '').strip()
        if is_num(ref):
            if ref in m_refs:
                log_file.write(ref + ' is in Manager already \n')
            else:
                try:
                    invoices[str(ref)]['name'] = Cus
                    num_transactions = len(invoices[ref]['transactions']) + 1
                    invoices[ref]['transactions'][num_transactions] = {
                        'date': T_Dt, 'type': T_Tp, 'description': T_Des,
                        'amount': In_VAT}
                except (KeyError) as e:
                    log_file.write("This key is not in the dictionary" +
                                   str(e) + "\n")

    except IndexError as e:
        return


def get_data(invoice_file, statement_file, m_refs):
    """Get the data out of files, and add to dict, if not already there."""
    invoices = {}
    [create_invoices_dict(invoices, OrderID, Date, Title, Qty, Price, Email,
                          m_refs)
     for OrderID, Date, Title, Qty, Price, Email in
        [line.strip().split(',') for line in invoice_file]]

    [add_to_dict(invoices, T_Dt, T_Tp,
                 T_ID, T_Des, Cus, Ref_Tp, Ref, Ex_VAT, VAT, In_VAT, Bal,
                 m_refs) for
     T_Dt, T_Tp, T_ID, T_Des, Cus, Ref_Tp, Ref, Ex_VAT, VAT, In_VAT, Bal in
     [line.strip().split(',') for line in statement_file]]

    pprint.pprint(invoices)

    return invoices


def post_customer_return(manager_object, invoice, m_emails):
    cus_email = invoice['email']
    if (cus_email != '') and (cus_email not in m_emails):
        ret = manager_object.post_customer(name=invoice['name'],
                                           email=invoice['email'])
        _, obj = ret.headers['Location'].rsplit('/', 1)
        obj, _ = obj.split('.')
        return(cus_email, obj)
    else:
        log_file.write('There was no reason to add email for:' +
                       invoice + '\n')
        return(None, None)


def post_invoice_return(manager_object, customers, invoice, ref):
    if invoice['email'] == '' or invoice['transactions'] == {}:
        print(invoice['email'], invoice['transactions'])
        return(None, None)
    items = invoice['items']
    lines = []
    for item in items:
        in_item = sales_items[item[0]]
        in_item['Qty'] = item[1]
        in_item['Amount'] = item[2]
        lines.append(in_item)
    try:
        ret = manager_object.post_sales_invoice(issue_date=invoice['date'],
                                                ref=ref,
                                                to=customers[invoice['email']],
                                                lines=lines)
        _, obj = ret.headers['Location'].rsplit('/', 1)
        obj, _ = obj.split('.')
        return(ref, obj)

    except (KeyError) as e:
        log_file.write("An error occured or," +
                       "This key is not in the dictionary: " +
                       str(e) + '\n')
        return(None, None)


def post_receipt_return(manager_object, ref, invoice):

    print(invoice)


def try_appends(objs, obj_lst, key):
    for ref in objs:
        try:
            obj_lst.append(objs[ref][key])
        except (KeyError) as e:
            log_file.write("An error occured or," +
                           "This key is not in the dictionary: " + ref +
                           str(e) + '\n')


def __main__():
    # xvTcVN8QNxusX3S6xSLd
    user = 'api'
    host = 'https://manager.procsum.co.za'
    # invoice_file = open('invoice.csv', 'r')
    # statement_file = open('statement.csv', 'r')
    m_o, customers, invoices, items, static_info = get_manager_info(
       host, user, 'ProcSum')

    m_emails = list()
    m_refs = list()

    try_appends(customers, m_emails, 'Email')
    try_appends(invoices, m_refs, 'Reference')

    # new_invoices = get_data(invoice_file, statement_file, m_refs)

    print('Got all the info.\n')

    customers = {value['Email']: key
                 for key, value in customers.items()
                 if 'Email' in value}

    # pprint.pprint(invoices[0])
    # pprint.pprint(customers)
    # pprint.pprint(static_info)
    pprint.pprint(items)


    # for ref in new_invoices:
    #     email, obj = post_customer_return(m_o, new_invoices[ref], m_emails)
    #     customers[email] = obj
    #     invoice, obj = post_invoice_return(m_o, customers,
    #                                        new_invoices[ref], ref)

    print('Posted all the things.\n')


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
"""
