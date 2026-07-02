### Royal Web

Professional Arabic RTL website for Royal's water and energy solutions, built as
standard, database-backed Frappe/ERPNext v15 **Web Page** records.

### Included pages

- Home, About, Services, Products, Sectors, Projects, Brands, Resources, Careers
- Solar Energy, Pumps & Wells, Well Drilling & Rehabilitation, Water Treatment,
  Control Panels, Maintenance
- Searchable and filterable product catalogue covering pumps, motors, solar,
  cables, controls, pipes and well accessories
- Contact, Quote Request, Privacy, Terms
- Shared RTL navbar/footer, responsive mobile actions, project filtering and FAQ
- Existing `/inquiry/new` Web Form integration for ERPNext CRM Leads
- Website Theme, standard Navbar, standard Footer and public File records

### Before deployment

1. Upload the full company logo to `/files/logo-royal.png`.
2. Upload the icon-only logo to `/files/logo1.png`.
3. Replace the placeholder phone, email, address, social links, statistics,
   brands and project content.
4. Replace the stock images in `royal_web/public/images` with real Royal project
   photography when available.
5. Review the privacy and terms pages with legal counsel.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app royal_web
```

Run migrate. The `after_migrate` hook creates the standard website records once:

```bash
bench --site your-site.local migrate
bench --site your-site.local clear-cache
```

After this command, edit all content from:

- **Website > Web Site > Web Page** — every page and its SEO fields
- **Website > Setup > Website Theme > Royal Modern RTL** — all CSS and JavaScript
- **Website > Setup > Website Settings** — home page, navbar, footer and logo
- **File** — all website images

The app files are only source/installation material. Published routes are served
from standard Web Page database records, which take precedence over `www` files.
Later migrations do not overwrite changes made in Desk.

To intentionally rebuild every Web Page and the theme from source:

```bash
bench --site your-site.local execute \
  royal_web.standard_pages.install_standard_website --kwargs "{'force': true}"
```

Do not use `force` after editors have changed content in Desk unless those edits
may be replaced. All quote and consultation buttons link to the existing
ERPNext Web Form at `/inquiry/new`.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/royal_web
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
