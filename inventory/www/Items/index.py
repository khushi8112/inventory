import frappe

def get_context(context):
	context.items = frappe.get_all("Item", fields=["name1", "opening_warehouse", "image", "opening_rate"])
	return context
	