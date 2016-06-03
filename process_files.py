#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A large script to do a simple job, enter invoices into Manager."""
import pyManager as pm
import pprint

__author__ = 'Andrew James Collett'
log_file = open('log.txt', 'w')

sales_items = {'Flirc Raspberry Pi Case': {
               'Description': 'The most beautifully crafted Raspberry Pi' +
               ' Case. An aluminium body with a built in heat sink, our' +
               ' case is the perfect home for your Raspberry Pi B+ and' +
               ' will become another one of your favourite media centre' +
               ' companions.',
               'Account': 'ea44f579-9548-4954-baf0-48538aceff1e',
               'TrackingCode': 'd590095a-fe46-4a3e-8989-3c9564d69d4e',
               'InventoryItem': '85cd0eb9-d4c3-491d-9639-e20eab51e5e1',
               'Item': 'a0184658-6ad3-4a87-bfdd-002e74c6384e'
               }, 'Flirc USB': {
               'Description': 'Flirc USB IR reciever PC remote',
               'Account': 'ea44f579-9548-4954-baf0-48538aceff1e',
               'TrackingCode': 'd590095a-fe46-4a3e-8989-3c9564d69d4e',
               'InventoryItem': '77b6e2d4-4f19-4e06-9c31-f6c39cb6592a',
               'Item': '19816a8e-0344-4e7f-88b2-42704d3cc99d'
               }, 'Raspberry Pi 3 Model B (parallel import)': {
               'Description': 'Features & Benefits of the Pi 3 Broadcom' +
               ' BCM2837 chipset running at 1.2 GHz 64-bit quad-core ARM' +
               ' Cortex-A53 802.11 b/g/n Wireless LAN Bluetooth 4.1' +
               ' (Classic & Low Energy) Dual core Videocore IV' +
               ' Multimedia co-processor 1 GB LPDDR2 memory Supports all' +
               ' the latest ARM GNU/Linux distributions and Windows 10 ' +
               'IoT microUSB connector for 2.5 A power supply 1 x 10/100' +
               ' Ethernet port 1 x HDMI video/audio connector 1 x RCA' +
               ' video/audio connector 1 x CSI camera connector 4 x USB' +
               ' 2.0 ports 40 GPIO pins Chip antenna DSI display' +
               ' connector microSD card slot Dimensions: 85 x 56 x 17 mm',
               'Account': '8ac854ab-eee5-43de-8790-54f42bc74bd0',
               'TrackingCode': 'd590095a-fe46-4a3e-8989-3c9564d69d4e',
               'InventoryItem': 'df8539b8-104b-413c-bbf7-651dc857bf50',
               'Item': 'b6b223a3-cc0e-43d3-8817-3631f5f0e391'
               }, 'Raspberry Pi 2 Model B': {
               'Description': 'Raspberry Pi 2 Model B',
               'Account': 'ea44f579-9548-4954-baf0-48538aceff1e',
               'TrackingCode': 'd590095a-fe46-4a3e-8989-3c9564d69d4e',
               'InventoryItem': 'a90f1015-c749-464b-85b6-5bbfa17e3ce8',
               'Item': '42f5176a-d441-494e-9de5-0372b9304d1b'
               }
               }


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
    # sales_items = manager_object.get_sales_inventory_items()
    sales_items = dict()

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


def try_appends(objs, obj_lst, key):
    for ref in objs:
        try:
            obj_lst.append(objs[ref][key])
        except (KeyError) as e:
            log_file.write("An error occured or," +
                           "This key is not in the dictionary: " + ref +
                           str(e) + '\n')


def __main__():
    user = 'api'
    host = 'https://manager.procsum.co.za'
    invoice_file = open('invoice.csv', 'r')
    statement_file = open('statement.csv', 'r')
    m_o, customers, invoices, items, static_info = get_manager_info(
       host, user, 'ProcSum')

    m_emails = list()
    m_refs = list()

    try_appends(customers, m_emails, 'Email')
    try_appends(invoices, m_refs, 'Reference')

    invoices = get_data(invoice_file, statement_file, m_refs)

    print('Got all the info.\n')

    customers = {value['Email']: key
                 for key, value in customers.items()
                 if 'Email' in value}

    for ref in invoices:
        email, obj = post_customer_return(m_o, invoices[ref], m_emails)
        customers[email] = obj
        invoice, obj = post_invoice_return(m_o, customers, invoices[ref], ref)

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
