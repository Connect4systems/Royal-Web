### Royal Web

Professional Arabic RTL website for Royal's water and energy solutions, built as
standard Frappe/ERPNext v15 `www` pages.

### Included pages

- Home, About, Services, Products, Sectors, Projects, Brands, Resources, Careers
- Solar Energy, Pumps & Wells, Well Drilling & Rehabilitation, Water Treatment,
  Control Panels, Maintenance
- Searchable and filterable product catalogue covering pumps, motors, solar,
  cables, controls, pipes and well accessories
- Contact, Quote Request, Privacy, Terms
- Shared RTL navbar/footer, responsive mobile actions, project filtering and FAQ
- Public quote/contact forms that create a Lead in ERPNext CRM

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

Then build assets and clear the website cache:

```bash
bench build --app royal_web
bench --site your-site.local clear-cache
bench --site your-site.local migrate
```

The hook `home_page = "index"` makes the new homepage the website root. Every
route is an independent file in `royal_web/www`, while the shared header/footer
live in `royal_web/templates/includes` and the design system is in
`royal_web/public/css/royal.css`.

Quote and contact submissions call
`royal_web.api.submit_quote` and create a standard ERPNext `Lead` with source
`Website`.

All primary quote and consultation buttons link to the existing ERPNext inquiry
form at `/inquiry/new` (`https://royal.connect4systems.com/inquiry/new`). The
custom `/quote-request` page remains available as a fallback.

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
