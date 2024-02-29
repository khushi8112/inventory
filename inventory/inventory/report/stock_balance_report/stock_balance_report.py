# Copyright (c) 2024, Khushi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{
            'fieldname': 'item_name',
            'label': _('Item Name'),
            'fieldtype': 'Link',
            'options': 'Stock Ledger Entry',
			'width': 200,
        },
		{
            'fieldname': 'warehouse_name',
            'label': _('Warehouse'),
            'fieldtype': 'Link',
            'options': 'Stock Ledger Entry',
			'width': 200,
        },
		{
            'fieldname': 'available_qty',
            'label': _('Available Quantity'),
            'fieldtype': 'Data',
            'options': 'Stock Ledger Entry',
			'width': 200
        },
		{
            'fieldname': 'inout_rate',
            'label': _('In-Out Rate'),
            'fieldtype': 'Data',
            'options': 'Stock Ledger Entry',
			'width': 200
        },
		{
            'fieldname': 'valuation_rate',
            'label': _('Valuation'),
            'fieldtype': 'Data',
            'options': 'Stock Ledger Entry',
			'width': 200
        }
	]
	return columns

def get_data(filters):
	query_filters = {}
	if filters.posting_date:
		query_filters["posting_date"] = filters["posting_date"]
	else:
		query_filters["posting_date"] = today()
	
	data = frappe.db.get_all("Stock Ledger Entry", {
        "posting_date": ['<=', query_filters["posting_date"]]
        }, [
        "SUM(quantity_change) as available_qty",
        'item_name', 
        'warehouse_name', 
        'posting_date', 
        'inout_rate', 
        'quantity_change',  
        'valuation_rate'
        ],
    group_by = "item_name, warehouse_name"
	)
	return data