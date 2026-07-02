document.addEventListener("DOMContentLoaded", () => {
	const toggle = document.querySelector("[data-nav-toggle]");
	const nav = document.querySelector("[data-nav]");

	if (toggle && nav) {
		toggle.addEventListener("click", () => {
			const isOpen = toggle.getAttribute("aria-expanded") === "true";
			toggle.setAttribute("aria-expanded", String(!isOpen));
			nav.classList.toggle("is-open", !isOpen);
			document.body.classList.toggle("nav-open", !isOpen);
		});
	}

	const currentPath = window.location.pathname.replace(/\/$/, "") || "/";
	document.querySelectorAll(".royal-nav a").forEach((link) => {
		const linkPath = new URL(link.href, window.location.origin).pathname.replace(/\/$/, "") || "/";
		if (linkPath === currentPath) link.classList.add("is-active");
	});

	document.querySelectorAll("[data-accordion-button]").forEach((button) => {
		button.addEventListener("click", () => {
			const expanded = button.getAttribute("aria-expanded") === "true";
			button.setAttribute("aria-expanded", String(!expanded));
			button.nextElementSibling.hidden = expanded;
		});
	});

	document.querySelectorAll("[data-filter]").forEach((button) => {
		button.addEventListener("click", () => {
			const group = button.closest("[data-filter-group]");
			const target = group?.dataset.target;
			if (!target) return;
			group.querySelectorAll("[data-filter]").forEach((item) => item.classList.remove("is-active"));
			button.classList.add("is-active");
			document.querySelectorAll(target).forEach((card) => {
				const categories = (card.dataset.category || "").split(" ");
				card.hidden = button.dataset.filter !== "all" && !categories.includes(button.dataset.filter);
			});
		});
	});

	document.querySelectorAll("[data-catalog]").forEach((catalog) => {
		const search = catalog.querySelector("[data-catalog-search]");
		const buttons = catalog.querySelectorAll("[data-catalog-filter]");
		const items = catalog.querySelectorAll("[data-catalog-item]");
		const results = catalog.querySelector("[data-catalog-results]");
		const empty = catalog.querySelector("[data-catalog-empty]");
		let activeCategory = "all";

		const normalize = (value) =>
			value
				.toLocaleLowerCase("ar")
				.normalize("NFKD")
				.replace(/[\u064B-\u065F\u0670]/g, "")
				.replace(/[أإآ]/g, "ا")
				.replace(/ة/g, "ه")
				.trim();

		const updateCatalog = () => {
			const query = normalize(search?.value || "");
			let visibleCount = 0;
			items.forEach((item) => {
				const categories = (item.dataset.category || "").split(" ");
				const searchableText = normalize(`${item.dataset.search || ""} ${item.textContent}`);
				const categoryMatches = activeCategory === "all" || categories.includes(activeCategory);
				const searchMatches = !query || searchableText.includes(query);
				item.hidden = !(categoryMatches && searchMatches);
				if (!item.hidden) visibleCount += 1;
			});
			if (results) results.textContent = `${visibleCount} منتجًا وحلًا مطابقًا`;
			if (empty) empty.hidden = visibleCount !== 0;
		};

		buttons.forEach((button) => {
			button.addEventListener("click", () => {
				activeCategory = button.dataset.catalogFilter || "all";
				buttons.forEach((item) => item.classList.toggle("is-active", item === button));
				updateCatalog();
			});
		});
		search?.addEventListener("input", updateCatalog);
		updateCatalog();
	});

	document.querySelectorAll("[data-quote-form]").forEach((form) => {
		form.addEventListener("submit", async (event) => {
			event.preventDefault();
			const submit = form.querySelector("button[type='submit']");
			const status = form.querySelector("[data-form-status]");
			submit.disabled = true;
			status.textContent = "جارٍ إرسال طلبك...";
			try {
				const response = await fetch("/api/method/royal_web.api.submit_quote", {
					method: "POST",
					headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.csrf_token || "" },
					body: JSON.stringify(Object.fromEntries(new FormData(form))),
				});
				if (!response.ok) throw new Error("Request failed");
				form.reset();
				status.textContent = "تم استلام طلبك بنجاح. سيتواصل معك فريقنا قريبًا.";
				status.className = "form-status is-success";
			} catch (error) {
				status.textContent = "تعذر الإرسال الآن. يرجى التواصل معنا عبر واتساب أو الهاتف.";
				status.className = "form-status is-error";
			} finally {
				submit.disabled = false;
			}
		});
	});
});
