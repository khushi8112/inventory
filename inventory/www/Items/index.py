import frappe

def get_context(context):
	context.new_doc = frappe.get_all("Item")
	return context
	