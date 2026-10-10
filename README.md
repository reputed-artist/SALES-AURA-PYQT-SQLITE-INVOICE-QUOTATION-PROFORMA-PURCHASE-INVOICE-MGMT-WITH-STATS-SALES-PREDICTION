# 🚀 Sales Aura

### PyQt6 + SQLite Business Management, Digital Marketing Insights & Sales Prediction System

**Sales Aura** is a modern desktop business management, invoicing, and **digital marketing intelligence** application built with **Python, PyQt6, and SQLite**.

> **Zero-setup storage** — the app keeps all of its data in a local SQLite file located at `%LOCALAPPDATA%\Sales Aura\sales aura.db`. There is no database server to install, no credentials to configure, and no XAMPP/MySQL dependency. On the very first launch, the file is created automatically and seeded from the bundled `db.sql` dump.

It brings **sales, purchasing, quotations, invoicing, customer management, accounts, reports, digital marketing insights, Facebook comment scraping, and sales prediction** together in a single desktop application.

The project is designed for small and medium-sized businesses that need a practical desktop solution for managing day-to-day sales, billing, and marketing operations — while also turning historical sales data into actionable insights.

---

## ✨ Key Features

### 🧾 Invoice Management

* Tax Invoice generation and management
* Proforma Invoice
* Quotation
* Quick Quotation
* Purchase Invoice
* Invoice editing and deletion
* Invoice viewing and print preview
* PDF-ready invoice printing
* Financial-year based invoice numbering
* GST / tax calculation support
* Automatic subtotal, tax, and grand-total calculations

---

### 👥 Customer & Supplier Management

Manage customers and suppliers from a centralized interface.

* Add / edit / delete customers
* Add / edit / delete suppliers
* Customer and Supplier information pages
* Customer/Supplier classification
* Searchable customer selection
* Customer and supplier transaction history

---

### 📦 Product Management

Maintain your product catalog from within the application.

* Product creation, editing, deletion
* Product information pages
* Product pricing
* HSN code support
* Product-related transaction information

---

### 💰 Accounts & Ledger

Sales Aura includes an integrated account and ledger system for tracking business transactions.

* Customer accounts and supplier accounts
* Opening balance, credit, debit, closing balance
* Ledger view
* Financial-year based accounting
* Transaction history and account summaries

---

### 📊 Sales & Business Reports

Analyze your business data through dedicated reporting pages.

Supported reporting areas include:

* **Sales reports** — item-wise, HSN-wise, summary
* **Purchase reports** — item-wise, HSN-wise, summary
* **Quotation reports** — including quick quotations
* **HSN reports** — across Sales, Purchase, and Quotation records
* Transaction reports and account reports
* Customer-related and product-related reports
* Financial-year based reporting
* Export-ready report data

---

### 📈 Digital Marketing Dashboard

Sales Aura includes a **digital marketing insights dashboard** built to help businesses understand their marketing performance at a glance.

The dashboard is designed to bring together metrics from invoices, marketing sources, and customer activity to support data-driven marketing decisions.

Depending on the configured data, the dashboard provides insight into:

* **Marketing performance overview**
* **Campaign and channel insights**
* **Customer acquisition trends**
* **Engagement metrics** derived from social / marketing sources
* **Sales turnover and purchase activity**
* **Tax/GST information**
* **Business transaction summaries**
* **Customer and product activity**
* **Sales trends**
* **Prediction insights**

> The digital marketing dashboard is designed to be the analytics layer that ties marketing activity back to actual business results — invoices, customers, and revenue.

---

### 🤖 Sales Prediction & Next-Purchase Forecasting

One of the flagship features of Sales Aura is its **Sales Prediction** module.

The system analyses historical sales information to transform business transaction data into forward-looking insights — including **predicting when each client is likely to purchase next**.

The module is designed to support:

* **Next-purchase date prediction per client** — estimates when a specific customer is likely to place their next order, based on their past purchase intervals and behaviour
* **Historical sales analysis**
* **Sales trends and seasonality**
* **Sales forecasting**
* **Prediction dashboards**
* **Data-driven business planning**
* **Customer retention and re-engagement signals**

> Sales prediction results should be treated as analytical estimates and not guaranteed future outcomes.

---

### 📣 Facebook Comment Scraper & Marketing Tools

Sales Aura bundles **marketing tools** that help digital marketing teams gather and act on public engagement data.

#### Facebook Comment Scraper

* Scrape comments from **public Facebook posts / pages**
* Collect comment text, author, timestamp, and engagement data
* Export scraped comment data for further analysis
* Supports marketing research, sentiment overview, and lead discovery workflows
* Integrates with the digital marketing dashboard for reporting

#### Marketing Tools

A growing set of utilities for digital marketing teams:

* Campaign tracking helpers
* Engagement data collection
* Audience / comment insight workflows
* Data preparation for reporting and dashboards

> **Note:** The scraper is intended for use only on publicly accessible content and must be used in compliance with Facebook's Terms of Service and applicable data-protection laws. Always obtain consent where required.

---

### 🔎 Smart DataTables-Style Interfaces

List pages provide a DataTables-inspired experience.

Features include:

* Search, Pagination
* First / Previous / Next / Last navigation
* Page numbers, Rows per page
* 10 / 25 / 50 / 100 / All entries
* Entry counters
* Filtered totals and visible-page totals
* Fast client-side page rendering

---

### 🖨️ Printing & PDF

Sales Aura provides printing functionality for business documents.

Supported document workflows include:

* Tax Invoice
* Proforma Invoice
* Quotation
* Quick Quotation
* Purchase Invoice

Documents can be opened through print preview and prepared for PDF/physical printing.

---

## 🏗️ Application Modules

| Module                  | Description                                              |
| ----------------------- | -------------------------------------------------------- |
| 🏠 Dashboard            | Business overview and analytics                          |
| 📈 Digital Marketing    | Marketing insights dashboard                             |
| 🤖 Sales Prediction     | Next-purchase forecasting and sales analysis             |
| 📣 Facebook Scraper     | Public comment scraping for marketing research           |
| 👥 Clients              | Customer management                                      |
| 🏭 Suppliers            | Supplier management                                      |
| 📦 Products             | Product catalog                                          |
| 🧾 Tax Invoice          | Sales invoice management                                 |
| 📄 Proforma             | Proforma invoice management                              |
| 💬 Quotation            | Quotation management                                     |
| ⚡ Quick Quotation       | Fast quotation workflow                                  |
| 🛒 Purchase             | Purchase invoice management                              |
| 💳 Transactions         | Payment/transaction management                           |
| 📚 Accounts             | Account and ledger management                            |
| 📊 Reports              | Sales, purchase, quotation & HSN reports                 |
| ⚙️ Settings             | Application / company settings                           |

---

## 🛠️ Technology Stack

### Desktop Application

* **Python 3**
* **PyQt6**
* **sqlite3** (built into Python — no driver to install)

### Database

* **SQLite 3** — local file storage, no server required

### Marketing / Scraping

* HTTP client for public data collection
* HTML parsing utilities
* Comment export (CSV / Excel-ready)

### Application Architecture

* PyQt6 desktop UI
* Modular page architecture
* SQLite database layer with a MySQL-dialect compatibility shim
* Reusable utility functions
* Invoice / document rendering
* Financial-year based business logic
* Prediction and analytics engine

---

## 📁 Project Structure

```text
pyqt_app/
│
├── database/
│   ├── db_manager.py          # all queries / data access
│   ├── sqlite_compat.py       # MySQL-dialect -> SQLite translation
│   ├── schema_sqlite.py       # table definitions for the local database
│   └── init_sqlite.py         # creates + seeds data/sales_aura.db from db.sql
│
├── data/                      # created automatically on first run
│   ├── sales_aura.db          # the local SQLite database
│   └── backups/               # one-click backups
│
├── dist/
│   └── img/
│
├── tools/
│   ├── make_brand_logo.py
│   └── fb_comment_scraper.py  # Facebook public comment scraper
│
├── ui/
│   ├── pages/
│   │   ├── accounts_page.py
│   │   ├── dashboard_page.py
│   │   ├── digital_marketing_page.py
│   │   ├── fb_scraper_page.py
│   │   ├── invoice_pages.py
│   │   ├── master_pages.py
│   │   ├── quickquote_page.py
│   │   ├── reports_page.py
│   │   ├── sales_prediction_page.py
│   │   ├── settings_page.py
│   │   └── transaction_page.py
│   │
│   ├── login_window.py
│   ├── main_window.py
│   ├── splash_screen.py
│   ├── app_icon.py
│   └── icons.py
│
├── utils/
│   ├── helpers.py
│   └── invoice_print.py
│
├── config.py
├── db.sql
├── main.py
├── requirements.txt
├── smoke_test.py
└── README.md
```

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone <your-repo-url>
```

Move into the project directory:

```bash
cd sales-aura
```

---

## 2. Create a Virtual Environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The repository already contains a `requirements.txt` file for the Python dependencies.

---

# 🗄️ Database Setup

**No manual database setup is required.** Sales Aura uses a local SQLite file.

On the first launch the app automatically:

1. Creates the database file `sales aura.db` in `%LOCALAPPDATA%\Sales Aura\`
2. Creates all 22 tables (`admin`, `client`, `products`, `invtest` / `invtest2`, `protest` / `protest2`, `quote` / `quote2`, `purchaseinv` / `purchaseinv2`, `quickquote`, `account`, `acc_type`, `bankdetails`, `paidhistory`, `clienttype`, `delivery_addresses`, `techsps`, `fd`, `fest`)
3. Imports the seed data from the bundled `db.sql` dump
4. Creates the secondary indexes the dashboard relies on

To start from scratch, simply delete the database file from `%LOCALAPPDATA%\Sales Aura\` and launch the app again.

---

# ⚙️ Database Configuration

The database location is configured in:

```text
config.py
```

Example:

```python
# SQLite database — stored in %LOCALAPPDATA%\Sales Aura\ (writable)
# When frozen (exe): uses get_db_path() -> %LOCALAPPDATA%\Sales Aura\sales aura.db
# When running from source: uses BASE_DIR/data/sales aura.db
DB_FILE = get_db_path()

# Backup directory derived from DB_FILE location
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(DB_FILE)), "backups")
```

Point `DB_FILE` anywhere you like (e.g. an external drive) — the folder is created automatically if it does not exist.

### Backup & Restore

* **Settings → Backup** writes a consistent snapshot to `%LOCALAPPDATA%\Sales Aura\backups\sales aura_<timestamp>.db` using SQLite's online backup API — safe to run while the app is open.
* **Settings → Restore** validates the chosen file, swaps it in, and re-opens the connection. Restart the app afterwards to be safe.

---

### A Note on the SQL Layer

The project was originally written against MySQL, and the queries in `database/db_manager.py` are still written in MySQL dialect. Instead of rewriting them by hand, `database/sqlite_compat.py` translates each statement just before execution:

* `%s` / `%(name)s` placeholders → `?` / `:name`
* `GROUP_CONCAT(x SEPARATOR ', ')` → `group_concat(x, ', ')`
* `YEAR`, `MONTH`, `DATE_FORMAT`, `CONCAT`, `IF`, `IFNULL`, `CHAR_LENGTH`, `SUBSTRING_INDEX`, `CONCAT_WS`, `CURDATE`, `NOW` are registered as SQLite functions
* `DATE` / `DATETIME` columns are declared as such, so values come back as real `datetime.date` / `datetime.datetime` objects exactly like they did from MySQL (the UI relies on this)

This keeps every screen — and every query — behaving exactly as before, while the storage is now a single local file.

---

# ▶️ Run Sales Aura

Start the application using:

```bash
python main.py
```

The application will launch the Sales Aura desktop interface.

---

# 🔐 Login

Use the default administrator credentials:

```plaintext
Email:    admin@gmail.com
Password: admin@123
```

> **Security:** Do not publish real production credentials in this repository. Change the default password from **Settings → Profile** before using the application in a production environment.

---

# 📣 Facebook Comment Scraper — Usage Notes

The scraper is provided as a marketing research tool. It is designed to work only on publicly accessible content.

**Recommended usage:**

1. Open the **Facebook Scraper** module.
2. Paste the URL of a **public** post or page.
3. Choose the number of comments to fetch.
4. Click **Start**.
5. Export results to CSV / Excel for analysis.

**Compliance:**

* Only scrape content that is publicly available.
* Respect Facebook's Terms of Service and any applicable privacy / data-protection laws.
* Do not use collected data for spam, harassment, or targeted advertising without consent.
* If in doubt, consult your legal team before scraping.

---

# 🧠 Sales Intelligence

Sales Aura is not limited to traditional billing.

The long-term goal of the project is to combine:

```text
Business Transactions
        ↓
Historical Sales Data
        ↓
Analytics
        ↓
Sales Trends
        ↓
Prediction (Next Purchase Date per Client)
        ↓
Business Insights
        ↓
Marketing Action
```

This makes the system useful not only for recording transactions but also for understanding business performance and shaping marketing decisions.

---

# 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

---

# 📜 License

This project is licensed under the **MIT License** unless otherwise specified in the repository.

---

# 👨‍💻 Developer

Developed by **Tejas Chavda**

**Tejaschavda2020@gmail.com**

---

# ⭐ Support the Project

If you find **Sales Aura** useful:

⭐ Star the repository on GitHub

🐛 Report bugs

💡 Suggest improvements

🔧 Contribute code

📢 Share the project with other developers and businesses

---

### Sales Aura

> **Invoices · Insights · Intelligence · Predictions**
