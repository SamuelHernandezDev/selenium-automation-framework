# Selenium Automation Framework

A scalable UI automation framework built with **Python**, **Selenium WebDriver**, and the **Page Object Model (POM)** design pattern.

The project focuses on creating a clean, reusable, and maintainable automation architecture that can easily scale as new test suites and features are introduced.

---

## Features

- Page Object Model (POM) architecture
- Reusable page components
- Centralized configuration
- WebDriver Manager integration
- Modular project structure
- Chrome WebDriver support
- Clean separation between Pages and Tests
- Ready for future pytest integration

---

## Project Structure

```text
selenium-automation-framework/
│
├── config/
│   └── settings.py
│
├── pages/
│   ├── base_page.py
│   ├── home_page.py
│   ├── redirect_page.py
│   └── status_codes_page.py
│
├── tests/
│   ├── navigation/
│   ├── status-codes/
│   └── base_test.py
│
├── utils/
│   └── driver.py
│
├── screenshots/
├── docs/
│
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Technologies

- Python
- Selenium WebDriver
- ChromeDriver Manager
- Page Object Model (POM)

---

## Current Test Suites

### Navigation

- Verify page title
- Verify redirect navigation

### HTTP Status Codes

- Retrieve available HTTP status codes
- Verify HTTP 500 status page

---

## Getting Started

### Clone the repository

```bash
git clone

cd selenium-automation-framework
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run a test

Example:

```bash
python tests/navigation/page_title_test.py
```

---

## Roadmap

### Version 1.0

- Page Object Model architecture
- Navigation tests
- HTTP Status Code tests
- Centralized configuration

### Planned Features

- pytest integration
- HTML reports
- Allure reports
- GitHub Actions CI
- Screenshots on failure
- Fixtures
- Cross-browser execution
- Parallel execution
