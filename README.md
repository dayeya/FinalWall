# Blanket
This project aims to develop a robust and secure Web Application Firewall for websites.<br>
Blanket detects, monitors, and protects websites from the following web attacks.

* Blind/No-Blind SQL Injection.
* Stored/Reflected XSS.
* CSRF
* File Inclusion.

# Configuration
Blanket protects one website at a time. An admin may deploy another Blanket to protect another website.
This project uses a given website vulnerable to SQL Injection documented at [docs](https://github.com/dayeya/SQLi/blob/main/README.md).

# Attack detection and prevention
Blanket uses a simple protocol called blanket and built-in policies to block malicious traffic.

## Protocol
The blanket protocol covers HTTP sessions and cuts them off when needed. Each blanket handles data analysis.

# Database
In progress.

# Contributions
This project was written only by Dayeya, as opposed to the contributors list.
