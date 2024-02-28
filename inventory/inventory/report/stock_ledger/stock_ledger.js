// Copyright (c) 2024, Khushi and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Ledger"] = {
	"filters": [
		{
            fieldname: 'item_name',
            label: __('Item Name'),
            fieldtype: 'Link',
            options: 'Item'
        },
        {
            fieldname: 'warehouse_name',
            label: __('Warehouse Name'),
            fieldtype: 'Link',
            options: 'Warehouse'
        },
        {
            fieldname: 'posting_date',
            label: __('Posting Date'),
            fieldtype: 'Date',
            options: 'Stock Ledger Entry'
        }
	]
};
