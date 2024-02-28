// Copyright (c) 2024, Khushi and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Balance Report"] = {
	"filters": [
        {
            fieldname: "posting_date",
            label: __("Date"),
            fieldtype: "Date",
            options: "Stock Ledger Entry",
        }
	]
};
