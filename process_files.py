#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A large script to do a simple job, enter invoices into Manager."""
import pyManager as pm

__author__ = 'Andrew James Collett'
log_file = open('log.txt', 'w')


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
    customers = manager_object.get_customers()
    sales_invoices = manager_object.get_sales_invoices()
    sales_items = manager_object.get_sales_inventory_items()

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

    return(manager_object, customers, sales_invoices, sales_items, static_info)


def create_invoices_dict(invoices, OrderID, Date, Title, Qty, Price, Email,
                         m_emails):
    """Create the Invoices dict and add details to it."""
    if is_num(OrderID):
        if Email in m_emails:
            log_file.write(Email + ' is in Manager already\n')
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


def get_data(invoice_file, statement_file, m_emails, m_refs):
    """Get the data out of files, and add to dict, if not already there."""
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
    invoice_file = open('invoice.csv', 'r')
    statement_file = open('statement.csv', 'r')
    m_o, customers, invoices, items, static_info = get_manager_info(
        host, user, 'ProcSum')

    m_emails = list()
    m_refs = list()

    for customer in customers:
        try:
            m_emails.append(customers[customer]['Email'])
        except (KeyError) as e:
            log_file.write("An error occured or," +
                           "This key is not in the dictionary: " + customer +
                           str(e) + '\n')

    for invoice in invoices:
        m_refs.append(invoices[invoice]['Reference'])

    invoices = get_data(invoice_file, statement_file, m_emails, m_refs)

    # TODO check all the things
    # (self, issue_date, ref, to, lines)

    print('Got all the info.\n')

    for ref in invoices:
        m_o.post_customer(name=invoices[ref]['name'],
                          email=invoices[ref]['email'])

    print('Printed all the things.\n')
    final_customers = m_o.get_customers()

    # for ref in invoices:
    #     man.post_sales_invoice(issue_date=order['date'], ref=ref, to=)

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
