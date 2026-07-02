"""Materialize the Royal website as editable Frappe v15 Website records.

The files under ``www`` are source templates only. On the first migration this
module creates normal Web Page, Website Theme, File and Website Settings records.
Those database records take routing precedence and can be edited entirely from
Desk. A global install flag prevents later migrations from overwriting UI edits.
"""

from __future__ import annotations

import re
from pathlib import Path

THEME_NAME = "Royal Modern RTL"
INSTALL_KEY = "royal_standard_website_installed"
PACKAGE_ROOT = Path(__file__).resolve().parent
WWW_ROOT = PACKAGE_ROOT / "www"
CSS_PATH = PACKAGE_ROOT / "public" / "css" / "royal.css"
JS_PATH = PACKAGE_ROOT / "public" / "js" / "royal.js"
IMAGE_ROOT = PACKAGE_ROOT / "public" / "images"

PAGE_FILES = (
	"index.html",
	"about.html",
	"services.html",
	"solar-energy.html",
	"pumps-wells.html",
	"well-services.html",
	"water-solutions.html",
	"control-panels.html",
	"maintenance.html",
	"products.html",
	"sectors.html",
	"projects.html",
	"brands.html",
	"resources.html",
	"careers.html",
	"contact.html",
	"quote-request.html",
	"privacy.html",
	"terms.html",
)

MEDIA_FILES = {
	"hero-solar.jpg": "royal-hero-solar.jpg",
	"engineer.jpg": "royal-engineer.jpg",
	"water.jpg": "royal-water.jpg",
	"industry.jpg": "royal-industry.jpg",
	"agriculture.jpg": "royal-agriculture.jpg",
	"partners/vansan.jpg": "royal-partner-vansan.jpg",
	"partners/ferat.jpg": "royal-partner-ferat.jpg",
	"partners/sp.jpg": "royal-partner-sp.jpg",
	"partners/shakti.jpg": "royal-partner-shakti.jpg",
	"partners/niagara.jpg": "royal-partner-niagara.jpg",
	"partners/prakash.jpg": "royal-partner-prakash.jpg",
	"partners/jinko.jpg": "royal-partner-jinko.jpg",
	"partners/ja-solar.jpg": "royal-partner-ja-solar.jpg",
	"partners/suntech.jpg": "royal-partner-suntech.jpg",
	"partners/aiko.jpg": "royal-partner-aiko.jpg",
	"partners/frecon.jpg": "royal-partner-frecon.jpg",
	"partners/veichi.jpg": "royal-partner-veichi.jpg",
	"partners/delixi.jpg": "royal-partner-delixi.jpg",
	"partners/invt.jpg": "royal-partner-invt.jpg",
	"partners/saj.jpg": "royal-partner-saj.jpg",
	"partners/quantum.jpg": "royal-partner-quantum.jpg",
	"partners/astral.jpg": "royal-partner-astral.jpg",
	"partners/sudarshan.jpg": "royal-partner-sudarshan.jpg",
	"partners/ashirvad.jpg": "royal-partner-ashirvad.jpg",
	"partners/idol.jpg": "royal-partner-idol.jpg",
	"partners/ontel.jpg": "royal-partner-ontel.jpg",
	"partners/turan.jpg": "royal-partner-turan.jpg",
}

CONTACT_REPLACEMENT = """
<div class="quote-form">
	<span class="eyebrow">نموذج ERPNext الرسمي</span>
	<h2>أرسل بيانات مشروعك بالتفصيل</h2>
	<p>يفتح النموذج القياسي المسجل داخل ERPNext ويحفظ الطلب مباشرة كسجل Lead لفريق المبيعات.</p>
	<ul class="check-list">
		<li>بيانات الموقع وقدرة المحطة</li>
		<li>قدرة الغاطس ومنسوب المياه</li>
		<li>نوع الري ومصدر الكهرباء</li>
		<li>العلامة والمكونات المفضلة</li>
	</ul>
	<a class="royal-btn royal-btn-primary" href="/inquiry/new">افتح نموذج الاستفسار ←</a>
</div>
"""


def _extract_value(source: str, variable: str, fallback: str = "") -> str:
	match = re.search(rf'{{%\s*set\s+{variable}\s*=\s*"([^"]*)"\s*%}}', source)
	return match.group(1).strip() if match else fallback


def _extract_content(source: str) -> str:
	match = re.search(
		r"{%\s*block\s+royal_content\s*%}(.*){%\s*endblock\s*%}",
		source,
		flags=re.DOTALL,
	)
	if not match:
		raise ValueError("Royal content block was not found")
	return match.group(1).strip()


def _make_database_independent(content: str, route: str) -> str:
	"""Remove dependencies on app-only API endpoints from standard pages."""
	if route == "contact":
		content = re.sub(
			r'<form\s+class="quote-form"\s+data-quote-form>.*?</form>',
			CONTACT_REPLACEMENT.strip(),
			content,
			flags=re.DOTALL,
		)
	if route == "quote-request":
		return '<!-- redirect:/inquiry/new -->'
	return content


def build_page_definitions(media_urls: dict[str, str] | None = None) -> list[dict]:
	"""Return pure page dictionaries; this part is testable without Frappe."""
	media_urls = media_urls or {
		source: f"/files/{target}" for source, target in MEDIA_FILES.items()
	}
	pages = []
	for filename in PAGE_FILES:
		source = (WWW_ROOT / filename).read_text(encoding="utf-8")
		stem = Path(filename).stem
		route = "royal-home" if stem == "index" else stem
		content = _make_database_independent(_extract_content(source), route)
		for image_name, file_url in media_urls.items():
			content = content.replace(
				f"/assets/royal_web/images/{image_name}",
				file_url,
			)
		content = "<!-- no-breadcrumbs --><!-- no-header -->\n" + content
		pages.append(
			{
				"title": _extract_value(source, "page_title", stem.replace("-", " ").title()),
				"route": route,
				"meta_description": _extract_value(source, "page_description"),
				"main_section_html": content,
			}
		)
	return pages


def _upload_media(frappe) -> dict[str, str]:
	urls = {}
	for source_name, target_name in MEDIA_FILES.items():
		existing_url = frappe.db.get_value(
			"File",
			{"file_name": target_name, "is_private": 0},
			"file_url",
		)
		if existing_url:
			urls[source_name] = existing_url
			continue
		file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": target_name,
				"is_private": 0,
				"content": (IMAGE_ROOT / source_name).read_bytes(),
			}
		)
		file_doc.insert(ignore_permissions=True)
		urls[source_name] = file_doc.file_url
	return urls


def _theme_assets(media_urls: dict[str, str]) -> tuple[str, str]:
	css = CSS_PATH.read_text(encoding="utf-8")
	for image_name, file_url in media_urls.items():
		css = css.replace(f"/assets/royal_web/images/{image_name}", file_url)
	return css, JS_PATH.read_text(encoding="utf-8")


def _upsert_theme(frappe, media_urls: dict[str, str], force: bool) -> str:
	css, javascript = _theme_assets(media_urls)
	if frappe.db.exists("Website Theme", THEME_NAME):
		if not force:
			return "kept"
		theme = frappe.get_doc("Website Theme", THEME_NAME)
	else:
		theme = frappe.new_doc("Website Theme")
		theme.theme = THEME_NAME
		theme.module = "Website"
		theme.custom = 1
	theme.google_font = "Cairo"
	theme.font_properties = "wght@400;500;600;700;800"
	theme.custom_scss = css
	theme.js = javascript
	theme.save(ignore_permissions=True)
	return "updated"


def _upsert_pages(frappe, pages: list[dict], force: bool) -> dict[str, int]:
	result = {"created": 0, "updated": 0, "kept": 0}
	for page_data in pages:
		existing_name = frappe.db.get_value("Web Page", {"route": page_data["route"]}, "name")
		if existing_name and not force:
			result["kept"] += 1
			continue
		page = frappe.get_doc("Web Page", existing_name) if existing_name else frappe.new_doc("Web Page")
		page.update(
			{
				**page_data,
				"content_type": "HTML",
				"published": 1,
				"full_width": 1,
				"show_title": 0,
				"insert_style": 0,
				"text_align": "Right",
				"enable_comments": 0,
			}
		)
		page.save(ignore_permissions=True)
		result["updated" if existing_name else "created"] += 1
	return result


def _set_navigation(settings) -> None:
	settings.set("top_bar_items", [])
	nav_items = [
		("الرئيسية", "/", ""),
		("من نحن", "/about", ""),
		("الخدمات", "", ""),
		("الطاقة الشمسية", "/solar-energy", "الخدمات"),
		("المضخات والآبار", "/pumps-wells", "الخدمات"),
		("حفر وتأهيل الآبار", "/well-services", "الخدمات"),
		("معالجة المياه", "/water-solutions", "الخدمات"),
		("لوحات التحكم", "/control-panels", "الخدمات"),
		("الصيانة والتشغيل", "/maintenance", "الخدمات"),
		("المنتجات", "/products", ""),
		("القطاعات", "/sectors", ""),
		("المشاريع", "/projects", ""),
		("العلامات التجارية", "/brands", ""),
		("الموارد", "/resources", ""),
		("اتصل بنا", "/contact", ""),
	]
	for label, url, parent_label in nav_items:
		settings.append(
			"top_bar_items",
			{"label": label, "url": url, "parent_label": parent_label, "right": 1},
		)

	settings.set("footer_items", [])
	footer_items = [
		("رويال", "", ""),
		("من نحن", "/about", "رويال"),
		("المشاريع", "/projects", "رويال"),
		("الوظائف", "/careers", "رويال"),
		("الحلول", "", ""),
		("الطاقة الشمسية", "/solar-energy", "الحلول"),
		("المضخات والآبار", "/pumps-wells", "الحلول"),
		("التحكم والحماية", "/control-panels", "الحلول"),
		("المساعدة", "", ""),
		("اتصل بنا", "/contact", "المساعدة"),
		("طلب عرض سعر", "/inquiry/new", "المساعدة"),
		("سياسة الخصوصية", "/privacy", "المساعدة"),
	]
	for label, url, parent_label in footer_items:
		settings.append(
			"footer_items",
			{"label": label, "url": url, "parent_label": parent_label, "right": 1},
		)


def _configure_website_settings(frappe) -> None:
	settings = frappe.get_single("Website Settings")
	settings.home_page = "royal-home"
	settings.title_prefix = "رويال"
	settings.website_theme = THEME_NAME
	settings.banner_image = "/files/logo1.png"
	settings.brand_html = (
		'<img src="/files/logo1.png" alt="رويال" '
		'style="height:48px;width:auto;object-fit:contain">'
	)
	settings.footer_logo = "/files/logo-royal.png"
	settings.call_to_action = "اطلب عرض سعر"
	settings.call_to_action_url = "/inquiry/new"
	settings.copyright = "رويال — جميع الحقوق محفوظة"
	settings.address = "0101 696 5712 — 0100 436 0202 — 0101 815 2493"
	settings.hide_login = 1
	settings.hide_footer_signup = 1
	settings.navbar_search = 0
	font_link = (
		'<link rel="preconnect" href="https://fonts.googleapis.com">'
		'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
		'<link href="https://fonts.googleapis.com/css2?family=Cairo:'
		'wght@400;500;600;700;800&display=swap" rel="stylesheet">'
	)
	head_html = settings.head_html or ""
	if "fonts.googleapis.com/css2?family=Cairo" not in head_html:
		settings.head_html = f"{head_html}\n{font_link}".strip()
	_set_navigation(settings)
	settings.save(ignore_permissions=True)


def install_standard_website(force: bool | str = False) -> dict:
	"""Create editable standard website records once.

	Run manually with:
	``bench --site SITE execute royal_web.standard_pages.install_standard_website``

	Pass ``force=true`` only when intentionally replacing edits made in Desk.
	"""
	import frappe
	from frappe.defaults import get_global_default, set_global_default

	force = str(force).lower() in {"1", "true", "yes"}
	if get_global_default(INSTALL_KEY) and not force:
		return {"status": "kept", "reason": "Standard website is already installed"}

	media_urls = _upload_media(frappe)
	theme_status = _upsert_theme(frappe, media_urls, force)
	page_result = _upsert_pages(frappe, build_page_definitions(media_urls), force)
	_configure_website_settings(frappe)
	set_global_default(INSTALL_KEY, "1")
	frappe.clear_cache()
	frappe.db.commit()
	return {
		"status": "installed",
		"theme": theme_status,
		"pages": page_result,
		"media": len(media_urls),
	}
