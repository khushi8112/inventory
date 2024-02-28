# Copyright (c) 2024, Khushi and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	return columns, data
# Copyright (c) 2024, Khushi and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	for item in data:
		if int(item.quantity_change) < 0:
			item.out_quantity = item.quantity_change
			item.in_quantity = 0
		else:
			item.out_quantity = 0
			item.in_quantity = item.quantity_change
	return columns, data

def get_columns():
	columns = [
		{
            'fieldname' : 'item_name',
            'label' : _('Item Name'),
            'fieldtype' : 'Link',
            'options' : 'Stock Ledger Entry',
			'width': 120
        },
		{
            'fieldname' : 'warehouse_name',
            'label' : _('Warehouse'),
            'fieldtype' : 'Link',
            'options' : 'Stock Ledger Entry',
			'width': 120
        },
		{
            'fieldname' : 'posting_date',
            'label' : _('Posting Date'),
            'fieldtype' : 'Date',
            'options' : 'Stock Ledger Entry',
			'width': 120
        },
		{
            'fieldname' : 'in_quantity',
            'label' : _('In quantity'),
            'fieldtype' : 'Data',
            'options' : 'Stock Ledger Entry',
			'width': 120
        },
		{
            'fieldname' : 'out_quantity',
            'label' : _('Out quantity'),
            'fieldtype' : 'Data',
            'options' : 'Stock Ledger Entry',
			'width': 120
        },
        {
            'fieldname' : 'inout_rate',
            'label' : _('Item Rate'),
            'fieldtype' : 'Data',
            'options' : 'Stock Ledger Entry',
			'width': 120
        },
		{
            'fieldname' : 'valuation_rate',
            'label' : _('Valuation'),
            'fieldtype' : 'Data',
            'options' : 'Stock Ledger Entry',
			'width': 120
		},
		{
            'fieldname' : 'voucher_type',
            'label' : _('Voucher Type'),
            'fieldtype' : 'Link',
            'options' : 'Stock Ledger Entry',
			'width': 120
        },
		{
            'fieldname' : 'voucher_name',
            'label' : _('Voucher Name'),
            'fieldtype' : 'Dynamic Link',
            'options' : 'Stock Ledger Entry',
			'width': 200
        }
	]
	return columns

def get_data(filters):
	query_filters = {}

	if filters.item_name:
		query_filters["item_name"] = filters["item_name"]
	if filters.warehouse_name:
		query_filters["warehouse_name"] = filters["warehouse_name"]
	if filters.posting_date:
		query_filters["posting_date"] = filters["posting_date"]
	
	data = frappe.db.get_all("Stock Ledger Entry", query_filters, ['item_name', 'warehouse_name', 'posting_date', 'inout_rate', 'quantity_change', 'valuation_rate', 'voucher_type', 'voucher_name'])
	
	# if data.quantity_change < 0:
	# 	data.append({
	# 		"out_quantity": data.quantity_change,
	# 		"in_quantity": 0
	# 	})
	# else:
	# 	data.append({
	# 		"out_quantity": 0,
	# 		"in_quantity": data.quantity_change
	# 	})
	return data
	

