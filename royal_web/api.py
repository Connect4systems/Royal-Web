import re

import frappe
from frappe import _
from frappe.utils import cstr


@frappe.whitelist(allow_guest=True)
def submit_quote(**data):
	"""Create a CRM lead from the public Royal quote form."""
	if cstr(data.get("website")):
		return {"ok": True}

	name = cstr(data.get("first_name") or data.get("name")).strip()
	phone = cstr(data.get("mobile_no") or data.get("phone")).strip()
	email = cstr(data.get("email")).strip()
	service = cstr(data.get("service")).strip()
	message = cstr(data.get("message")).strip()

	if len(name) < 2 or not re.fullmatch(r"[+0-9\s()-]{7,20}", phone):
		frappe.throw(_("يرجى إدخال الاسم ورقم هاتف صحيحين."))
	if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
		frappe.throw(_("يرجى إدخال بريد إلكتروني صحيح."))

	field_labels = {
		"custom_site_location": "موقع العمل",
		"custom_station_capacity": "قدرة المحطة بالكيلو وات",
		"custom_specific_components": "المكونات المفضلة",
		"custom_submersible_pump_power": "قدرة الغاطس",
		"custom_water_level": "منسوب سطح المياه",
		"custom_irrigation_method": "نوع الري",
		"custom_electricity_source": "مصدر الكهرباء",
		"custom_salt_levels": "نسبة الأملاح",
		"custom_submersible_origin": "منشأ الغاطس",
		"custom_submersible_brand": "ماركة الغاطس",
	}
	lead_data = {
		"doctype": "Lead",
		"lead_name": name[:140],
		"mobile_no": phone,
		"email_id": email or None,
	}
	if frappe.db.exists("Lead Source", "Website"):
		lead_data["source"] = "Website"

	lead_meta = frappe.get_meta("Lead")
	details = [
		f"الخدمة المطلوبة: {service}" if service else "",
		f"التفاصيل: {message}" if message else "",
	]
	for fieldname, label in field_labels.items():
		value = cstr(data.get(fieldname)).strip()
		if not value:
			continue
		details.append(f"{label}: {value}")
		if lead_meta.has_field(fieldname):
			lead_data[fieldname] = value
	if lead_meta.has_field("notes"):
		lead_data["notes"] = "\n".join(part for part in details if part)[:2000]

	lead = frappe.get_doc(lead_data)
	lead.flags.ignore_permissions = True
	lead.insert()
	return {"ok": True, "lead": lead.name}
