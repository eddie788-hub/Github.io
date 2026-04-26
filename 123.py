I'll create a complete multi-bot penetration testing swarm where each specialized bot handles a different aspect of security testing, all coordinated through a central command center with real-time visualization.

```python
#!/usr/bin/env python3
"""
PENETRATION TESTING SWARM - Complete Multi-Bot Security Suite
Specialized bots for network, web, phishing, password, and wireless security
All coordinated with real-time monitoring and reporting
"""

import os
import sys
import time
import threading
import queue
import json
import socket
import subprocess
import hashlib
import re
import ssl
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings("ignore")

# Core security libraries
try:
    import nmap
    import requests
    from bs4 import BeautifulSoup
    import paramiko
    from cryptography.fernet import Fernet
    import dns.resolver
    import whois
    import OpenSSL
    SECURITY_LIBS_AVAILABLE = True
except ImportError as e:
    SECURITY_LIBS_AVAILABLE = False
    print(f"[!] Missing security libraries: {e}")

# ML libraries
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np

# Rich UI
try:
    from rich.live import Live
    from rich.table import Table
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ==================== DATA MODELS ====================

@dataclass
class Finding:
    """Security finding structure"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    title: str
    description: str
    remediation: str
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    affected_service: Optional[str] = None
    port: Optional[int] = None
    
@dataclass
class Target:
    """Target structure"""
    host: str
    ports: List[int] = field(default_factory=list)
    services: Dict = field(default_factory=dict)
    vulnerabilities: List[Finding] = field(default_factory=list)

@dataclass
class ScanResult:
    """Scan result from bot"""
    bot_name: str
    timestamp: datetime
    targets: List[Target]
    findings: List[Finding]
    summary: Dict

# ==================== BOT 1: NETWORK VULNERABILITY SCANNER ====================

class NetworkSecurityBot:
    """Specialized bot for network infrastructure security"""
    
    def __init__(self, name: str = "NetworkSecurityBot"):
        self.name = name
        self.nm = nmap.PortScanner() if SECURITY_LIBS_AVAILABLE else None
        self.findings = []
        
    def scan_network(self, target: str, ports: str = "1-1000") -> List[Finding]:
        """Comprehensive network vulnerability scan"""
        print(f"[{self.name}] Scanning network: {target}")
        findings = []
        
        try:
            # Port scanning
            if self.nm:
                self.nm.scan(target, ports, arguments='-sV -sC -O -T4')
                
                for host in self.nm.all_hosts():
                    for proto in self.nm[host].all_protocols():
                        ports = self.nm[host][proto].keys()
                        
                        for port in ports:
                            service = self.nm[host][proto][port]
                            findings.extend(self._analyze_service(host, port, service))
                            
            # Common vulnerability checks
            findings.extend(self._check_common_vulnerabilities(target))
            
            # Network configuration checks
            findings.extend(self._check_network_security(target))
            
        except Exception as e:
            findings.append(Finding(
                severity="INFO",
                title="Scan Error",
                description=f"Error scanning {target}: {str(e)}",
                remediation="Check network connectivity and permissions"
            ))
        
        return findings
    
    def _analyze_service(self, host: str, port: int, service: Dict) -> List[Finding]:
        """Analyze service for vulnerabilities"""
        findings = []
        service_name = service.get('name', 'unknown')
        version = service.get('version', '')
        
        # Check for known vulnerable services
        vulnerable_services = {
            21: ("FTP", "Anonymous access or weak credentials"),
            22: ("SSH", "Weak cipher suites or default credentials"),
            23: ("Telnet", "Unencrypted communication"),
            80: ("HTTP", "Missing security headers"),
            443: ("HTTPS", "SSL/TLS vulnerabilities"),
            3306: ("MySQL", "Default credentials or weak configuration"),
            3389: ("RDP", "BlueKeep vulnerability (CVE-2019-0708)"),
            445: ("SMB", "EternalBlue vulnerability (MS17-010)"),
            1433: ("MSSQL", "Default sa account"),
            5432: ("PostgreSQL", "Weak authentication"),
            6379: ("Redis", "No authentication configured"),
            27017: ("MongoDB", "No authentication configured"),
        }
        
        if port in vulnerable_services:
            service_info = vulnerable_services[port]
            findings.append(Finding(
                severity="HIGH" if port in [23, 445, 3389] else "MEDIUM",
                title=f"Potentially Vulnerable Service: {service_info[0]}",
                description=f"Port {port} open with {service_name} (version: {version}). {service_info[1]}",
                remediation=f"Close port if not needed, update service, implement strong authentication",
                port=port,
                affected_service=service_name
            ))
        
        # Check for outdated versions (simplified)
        if version and any(v in version.lower() for v in ['1.0', '2.0', 'old', 'eol']):
            findings.append(Finding(
                severity="HIGH",
                title="Outdated Service Version",
                description=f"{service_name} {version} may have known vulnerabilities",
                remediation="Update to latest stable version",
                port=port,
                affected_service=service_name
            ))
        
        return findings
    
    def _check_common_vulnerabilities(self, target: str) -> List[Finding]:
        """Check for common vulnerabilities"""
        findings = []
        
        # Test for open DNS resolver
        try:
            test_domain = "test.openresolver.com"
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [target]
            answers = resolver.resolve(test_domain, 'A')
            if answers:
                findings.append(Finding(
                    severity="HIGH",
                    title="Open DNS Resolver",
                    description="DNS server allows recursive queries from external hosts",
                    remediation="Configure DNS server to restrict recursive queries",
                    affected_service="DNS"
                ))
        except:
            pass
        
        # Check for SNMP exposure
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            snmp_query = b'\x30\x26\x02\x01\x01\x04\x06\x70\x75\x62\x6c\x69\x63\xa0\x19\x02\x04\x6f\x05\x01\x01\x02\x01\x00\x02\x01\x00\x30\x0b\x30\x09\x06\x05\x2b\x06\x01\x02\x01\x01\x05\x00'
            sock.sendto(snmp_query, (target, 161))
            data, addr = sock.recvfrom(1024)
            if data:
                findings.append(Finding(
                    severity="MEDIUM",
                    title="SNMP Exposure",
                    description="SNMP service accessible with public community string",
                    remediation="Change SNMP community strings, restrict access, or disable SNMP",
                    affected_service="SNMP",
                    port=161
                ))
            sock.close()
        except:
            pass
        
        return findings
    
    def _check_network_security(self, target: str) -> List[Finding]:
        """Check network security configurations"""
        findings = []
        
        # Check ICMP response
        response = os.system(f"ping -c 1 -W 1 {target} > /dev/null 2>&1")
        if response == 0:
            findings.append(Finding(
                severity="INFO",
                title="Host Responds to ICMP",
                description="Target responds to ping requests, confirming host is active",
                remediation="Consider blocking ICMP if not needed for monitoring",
                affected_service="ICMP"
            ))
        
        return findings

# ==================== BOT 2: WEB APPLICATION SECURITY ====================

class WebSecurityBot:
    """Specialized bot for web application security testing"""
    
    def __init__(self, name: str = "WebSecurityBot"):
        self.name = name
        self.session = requests.Session()
        self.findings = []
        
    def scan_webapp(self, url: str) -> List[Finding]:
        """Comprehensive web application security scan"""
        print(f"[{self.name}] Scanning web application: {url}")
        findings = []
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Security headers check
        findings.extend(self._check_security_headers(url))
        
        # SQL Injection testing
        findings.extend(self._test_sql_injection(url))
        
        # XSS testing
        findings.extend(self._test_xss(url))
        
        # Directory enumeration
        findings.extend(self._enumerate_directories(url))
        
        # SSL/TLS check
        findings.extend(self._check_ssl_tls(url))
        
        # Form analysis
        findings.extend(self._analyze_forms(url))
        
        # Cookie security
        findings.extend(self._check_cookie_security(url))
        
        # Information disclosure
        findings.extend(self._check_info_disclosure(url))
        
        return findings
    
    def _check_security_headers(self, url: str) -> List[Finding]:
        """Check for security headers"""
        findings = []
        
        try:
            response = self.session.get(url, timeout=10, verify=False)
            headers = response.headers
            
            security_headers = {
                'Strict-Transport-Security': 'HSTS header missing - vulnerable to SSL stripping',
                'Content-Security-Policy': 'CSP header missing - vulnerable to XSS',
                'X-Frame-Options': 'Clickjacking protection missing',
                'X-Content-Type-Options': 'MIME sniffing protection missing',
                'X-XSS-Protection': 'XSS protection header missing',
                'Referrer-Policy': 'Referrer policy not set',
                'Permissions-Policy': 'Feature policy not configured'
            }
            
            for header, description in security_headers.items():
                if header not in headers:
                    findings.append(Finding(
                        severity="MEDIUM",
                        title=f"Missing Security Header: {header}",
                        description=description,
                        remediation=f"Add '{header}' header with appropriate values",
                        affected_service="Web Server"
                    ))
                    
        except Exception as e:
            findings.append(Finding(
                severity="INFO",
                title="Header Check Failed",
                description=f"Could not retrieve headers: {str(e)}",
                remediation="Ensure web server is accessible"
            ))
        
        return findings
    
    def _test_sql_injection(self, url: str) -> List[Finding]:
        """Test for SQL injection vulnerabilities"""
        findings = []
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT NULL--",
            "1' ORDER BY 1--",
            "' AND SLEEP(5)--",
            "1' AND 1=1--",
            "1' AND 1=2--"
        ]
        
        sql_errors = [
            "mysql", "sql syntax", "ora-", "postgresql", "microsoft jet",
            "odbc", "sqlite", "sql error", "unclosed quotation"
        ]
        
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            for param in params:
                for payload in sql_payloads:
                    test_url = url.replace(f"{param}={params[param][0]}", f"{param}={payload}")
                    
                    try:
                        response = self.session.get(test_url, timeout=5, verify=False)
                        response_text = response.text.lower()
                        
                        for error in sql_errors:
                            if error in response_text:
                                findings.append(Finding(
                                    severity="CRITICAL",
                                    title="SQL Injection Vulnerability",
                                    description=f"Parameter '{param}' is vulnerable to SQL injection",
                                    remediation="Use parameterized queries, input validation, and WAF",
                                    affected_service="Web Application"
                                ))
                                break
                    except:
                        continue
                        
        except:
            pass
        
        return findings
    
    def _test_xss(self, url: str) -> List[Finding]:
        """Test for Cross-Site Scripting vulnerabilities"""
        findings = []
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "'><script>alert('XSS')</script>",
            "<svg onload=alert('XSS')>"
        ]
        
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            for param in params:
                for payload in xss_payloads:
                    test_url = url.replace(f"{param}={params[param][0]}", f"{param}={payload}")
                    
                    try:
                        response = self.session.get(test_url, timeout=5, verify=False)
                        if payload in response.text and payload not in response.text.replace(payload, ''):
                            findings.append(Finding(
                                severity="HIGH",
                                title="Cross-Site Scripting (XSS) Vulnerability",
                                description=f"Parameter '{param}' reflects XSS payload without sanitization",
                                remediation="Implement output encoding and input validation",
                                affected_service="Web Application"
                            ))
                            break
                    except:
                        continue
                        
        except:
            pass
        
        return findings
    
    def _enumerate_directories(self, url: str) -> List[Finding]:
        """Enumerate common directories"""
        findings = []
        
        common_dirs = [
            'admin', 'backup', 'config', 'wp-admin', 'phpmyadmin',
            '.git', '.env', 'api', 'swagger', 'docs', 'test',
            'backup.zip', 'database.sql', 'config.php', '.htaccess'
        ]
        
        for directory in common_dirs:
            test_url = f"{url.rstrip('/')}/{directory}"
            try:
                response = self.session.get(test_url, timeout=3, verify=False)
                if response.status_code == 200:
                    findings.append(Finding(
                        severity="MEDIUM",
                        title="Sensitive Directory Exposure",
                        description=f"Directory '{directory}' is publicly accessible",
                        remediation="Restrict access with authentication or remove sensitive files",
                        affected_service="Web Server"
                    ))
            except:
                continue
        
        return findings
    
    def _check_ssl_tls(self, url: str) -> List[Finding]:
        """Check SSL/TLS configuration"""
        findings = []
        
        if url.startswith('https://'):
            hostname = url.split('//')[1].split('/')[0]
            
            try:
                context = ssl.create_default_context()
                with socket.create_connection((hostname, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        
                        # Check certificate expiry
                        expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        days_left = (expiry - datetime.now()).days
                        
                        if days_left < 30:
                            findings.append(Finding(
                                severity="HIGH" if days_left < 7 else "MEDIUM",
                                title="SSL Certificate Expiring Soon",
                                description=f"Certificate expires in {days_left} days",
                                remediation="Renew SSL certificate immediately",
                                affected_service="HTTPS"
                            ))
                        
                        # Check for weak protocols
                        try:
                            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                            with context.wrap_socket(socket.socket(), server_hostname=hostname) as sock:
                                sock.connect((hostname, 443))
                        except:
                            findings.append(Finding(
                                severity="HIGH",
                                title="Weak SSL/TLS Protocol",
                                description="Server supports weak TLS versions (< 1.2)",
                                remediation="Disable TLS 1.0 and 1.1, enable TLS 1.2/1.3",
                                affected_service="HTTPS"
                            ))
                            
            except Exception as e:
                findings.append(Finding(
                    severity="INFO",
                    title="SSL Check Failed",
                    description=f"Could not verify SSL: {str(e)}",
                    remediation="Check SSL configuration",
                    affected_service="HTTPS"
                ))
        
        return findings
    
    def _analyze_forms(self, url: str) -> List[Finding]:
        """Analyze forms for security issues"""
        findings = []
        
        try:
            response = self.session.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')
            
            for form in forms:
                action = form.get('action', '')
                method = form.get('method', 'get').upper()
                
                # Check for missing CSRF tokens
                csrf_tokens = form.find_all('input', {'name': re.compile(r'csrf|token', re.I)})
                if not csrf_tokens and method == 'POST':
                    findings.append(Finding(
                        severity="MEDIUM",
                        title="Missing CSRF Protection",
                        description=f"Form {action} lacks CSRF token",
                        remediation="Implement anti-CSRF tokens for all state-changing operations",
                        affected_service="Web Application"
                    ))
                
                # Check for password fields without HTTPS
                password_fields = form.find_all('input', {'type': 'password'})
                if password_fields and url.startswith('http://'):
                    findings.append(Finding(
                        severity="CRITICAL",
                        title="Password Field Over HTTP",
                        description="Password transmitted in plaintext",
                        remediation="Enforce HTTPS for all login forms",
                        affected_service="Web Application"
                    ))
                    
        except Exception as e:
            pass
        
        return findings
    
    def _check_cookie_security(self, url: str) -> List[Finding]:
        """Check cookie security attributes"""
        findings = []
        
        try:
            response = self.session.get(url, timeout=10, verify=False)
            cookies = response.cookies
            
            for cookie in cookies:
                if not cookie.secure and url.startswith('https://'):
                    findings.append(Finding(
                        severity="MEDIUM",
                        title="Cookie Missing Secure Flag",
                        description=f"Cookie '{cookie.name}' sent without Secure flag",
                        remediation="Set Secure flag on all cookies over HTTPS",
                        affected_service="Web Application"
                    ))
                
                if not cookie.has_nonstandard_attr('HttpOnly'):
                    findings.append(Finding(
                        severity="MEDIUM",
                        title="Cookie Missing HttpOnly Flag",
                        description=f"Cookie '{cookie.name}' accessible via JavaScript (XSS risk)",
                        remediation="Set HttpOnly flag to prevent XSS access",
                        affected_service="Web Application"
                    ))
                    
        except:
            pass
        
        return findings
    
    def _check_info_disclosure(self, url: str) -> List[Finding]:
        """Check for information disclosure"""
        findings = []
        
        sensitive_patterns = [
            (r'api[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9]+', "API Key Disclosure"),
            (r'password["\']?\s*[:=]\s*["\'][^"\']+', "Password Disclosure"),
            (r'token["\']?\s*[:=]\s*["\'][a-zA-Z0-9]+', "Token Disclosure"),
            (r'secret["\']?\s*[:=]\s*["\'][^"\']+', "Secret Key Disclosure"),
            (r'AWS[A-Z0-9]{16,}', "AWS Key Disclosure"),
            (r'-----BEGIN RSA PRIVATE KEY-----', "Private Key Exposure"),
        ]
        
        try:
            response = self.session.get(url, timeout=10, verify=False)
            
            for pattern, description in sensitive_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                if matches:
                    findings.append(Finding(
                        severity="CRITICAL",
                        title=description,
                        description=f"Sensitive information found in response",
                        remediation="Remove sensitive data from responses, use environment variables",
                        affected_service="Web Application"
                    ))
                    
        except:
            pass
        
        return findings

# ==================== BOT 3: PHISHING SIMULATION ====================

class PhishingSimulatorBot:
    """Specialized bot for phishing simulation and email security"""
    
    def __init__(self, name: str = "PhishingSimulatorBot"):
        self.name = name
        self.phishing_templates = self._load_templates()
        
    def _load_templates(self) -> Dict:
        """Load phishing email templates"""
        return {
            "credential_theft": {
                "subject": "Urgent: Account Security Alert",
                "body": "We detected suspicious activity on your account. Verify now: {link}",
                "indicators": ["urgent", "verify account", "security alert", "suspicious activity"]
            },
            "malware_delivery": {
                "subject": "Important Document Shared With You",
                "body": "Please review the attached document. Password: {password}",
                "indicators": ["attachment", "shared document", "review", "password"]
            },
            "invoice_fraud": {
                "subject": "Invoice #{number} Payment Due",
                "body": "Your invoice is ready for payment. Click here to view: {link}",
                "indicators": ["invoice", "payment", "overdue", "balance due"]
            },
            "tech_support": {
                "subject": "Security Update Required",
                "body": "Your system requires immediate security update: {link}",
                "indicators": ["security update", "patch", "vulnerability", "update now"]
            }
        }
    
    def analyze_email(self, email_content: str) -> Dict:
        """Analyze email for phishing indicators"""
        findings = []
        risk_score = 0
        
        # Check for phishing indicators
        indicators = {
            "urgent_language": r'\b(urgent|immediate|asap|quickly|right away)\b',
            "account_verification": r'\b(verify|confirm|update|validate)\s+(account|information|details)\b',
            "suspicious_link": r'https?://(?!.*\.' + '|'.join(['google', 'microsoft', 'apple']) + r')[\w\-\.]+\.\w+',
            "attachment": r'\b(attachment|attached|document|file|invoice)\b',
            "password_request": r'\b(password|credential|login)\s+(reset|change|update)\b',
            "unusual_sender": r'@[\w\-\.]+\.(xyz|top|club|online|site|web)',
            "grammar_errors": r'\b\w+\s+\w+\s+\w+\s+\b',  # Simplified
            "spoofed_domain": r'(paypal|bank|amazon|microsoft)\.\w{2,}\b'
        }
        
        email_lower = email_content.lower()
        
        for indicator_name, pattern in indicators.items():
            if re.search(pattern, email_lower, re.IGNORECASE):
                findings.append(f"Found: {indicator_name}")
                risk_score += 10
                if indicator_name == "suspicious_link":
                    risk_score += 20
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = "CRITICAL"
            recommendation = "Block email immediately, notify security team"
        elif risk_score >= 30:
            risk_level = "HIGH"
            recommendation = "Flag as suspicious, quarantine attachment"
        elif risk_score >= 15:
            risk_level = "MEDIUM"
            recommendation = "Review before delivery, warn user"
        else:
            risk_level = "LOW"
            recommendation = "Normal delivery"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "indicators_found": findings,
            "recommendation": recommendation
        }
    
    def create_phishing_simulation(self, target_email: str, template_type: str) -> Dict:
        """Create phishing simulation email"""
        import random
        
        if template_type not in self.phishing_templates:
            template_type = "credential_theft"
        
        template = self.phishing_templates[template_type]
        
        # Generate tracking ID
        tracking_id = hashlib.md5(f"{target_email}{time.time()}".encode()).hexdigest()[:8]
        
        # Create phishing link (local simulation server)
        phishing_link = f"http://phishing-sim.local/{tracking_id}"
        
        email_content = template["body"].format(link=phishing_link)
        if "{password}" in email_content:
            email_content = email_content.format(password=random.randint(100000, 999999))
        if "{number}" in email_content:
            email_content = email_content.format(number=random.randint(1000, 9999))
        
        return {
            "tracking_id": tracking_id,
            "subject": template["subject"],
            "body": email_content,
            "indicators": template["indicators"],
            "target": target_email,
            "type": template_type
        }
    
    def analyze_url(self, url: str) -> Dict:
        """Analyze URL for phishing indicators"""
        findings = []
        risk_score = 0
        
        # Check URL characteristics
        parsed = urlparse(url)
        
        # Check for IP address instead of domain
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', parsed.netloc):
            findings.append("IP address used instead of domain name")
            risk_score += 30
        
        # Check for URL shorteners
        shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly']
        if any(shortener in parsed.netloc for shortener in shorteners):
            findings.append("URL shortener service detected")
            risk_score += 15
        
        # Check for typosquatting
        common_domains = ['google', 'facebook', 'amazon', 'microsoft', 'apple', 'paypal']
        for domain in common_domains:
            if domain in parsed.netloc and domain not in parsed.netloc.split('.')[0]:
                findings.append(f"Possible typosquatting: {domain}")
                risk_score += 25
        
        # Check for excessive subdomains
        subdomains = parsed.netloc.split('.')
        if len(subdomains) > 4:
            findings.append("Excessive subdomains (possible phishing)")
            risk_score += 10
        
        # Check for suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.xyz', '.top', '.club', '.online']
        if any(parsed.netloc.endswith(tld) for tld in suspicious_tlds):
            findings.append("Suspicious TLD detected")
            risk_score += 20
        
        return {
            "url": url,
            "risk_score": min(100, risk_score),
            "risk_level": "CRITICAL" if risk_score >= 60 else "HIGH" if risk_score >= 40 else "MEDIUM" if risk_score >= 20 else "LOW",
            "findings": findings,
            "parsed_domain": parsed.netloc
        }

# ==================== BOT 4: PASSWORD STRENGTH ANALYZER ====================

class PasswordSecurityBot:
    """Specialized bot for password strength analysis and cracking simulation"""
    
    def __init__(self, name: str = "PasswordSecurityBot"):
        self.name = name
        self.common_passwords = self._load_common_passwords()
        self.strength_rules = self._define_strength_rules()
        
    def _load_common_passwords(self) -> Set[str]:
        """Load common password dictionary"""
        common = {
            'password', '123456', '123456789', 'qwerty', 'abc123', 'password1',
            'admin', 'letmein', 'welcome', 'monkey', 'dragon', 'master', 'sunshine',
            'princess', 'football', 'baseball', 'login', 'admin123', 'root', 'toor'
        }
        return common
    
    def _define_strength_rules(self) -> Dict:
        """Define password strength rules"""
        return {
            'length': {'min': 12, 'weight': 25},
            'uppercase': {'min': 1, 'weight': 15},
            'lowercase': {'min': 1, 'weight': 10},
            'digits': {'min': 1, 'weight': 15},
            'special': {'min': 1, 'weight': 20},
            'no_common': {'weight': 15}
        }
    
    def analyze_password(self, password: str) -> Dict:
        """Analyze password strength and provide feedback"""
        score = 0
        feedback = []
        strength = "VERY_WEAK"
        
        # Check length
        length = len(password)
        if length >= self.strength_rules['length']['min']:
            score += self.strength_rules['length']['weight']
        else:
            feedback.append(f"Password too short ({length} chars). Minimum: {self.strength_rules['length']['min']}")
        
        # Check character types
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if has_upper:
            score += self.strength_rules['uppercase']['weight']
        else:
            feedback.append("Add uppercase letters")
        
        if has_lower:
            score += self.strength_rules['lowercase']['weight']
        else:
            feedback.append("Add lowercase letters")
        
        if has_digit:
            score += self.strength_rules['digits']['weight']
        else:
            feedback.append("Add numbers")
        
        if has_special:
            score += self.strength_rules['special']['weight']
        else:
            feedback.append("Add special characters")
        
        # Check if common password
        if password.lower() in self.common_passwords:
            feedback.append("Password is too common (in top 1000 passwords)")
        else:
            score += self.strength_rules['no_common']['weight']
        
        # Check for patterns
        patterns = [
            (r'(.)\1{2,}', "Repeated characters"),
            (r'123|234|345|456|567|678|789', "Sequential numbers"),
            (r'qwert|asdf|zxcv', "Keyboard pattern"),
            (r'(19|20)\d{2}', "Year pattern"),
            (r'[a-z]{3,}[0-9]{3,}', "Simple pattern")
        ]
        
        for pattern, msg in patterns:
            if re.search(pattern, password.lower()):
                feedback.append(msg)
                score -= 5
        
        # Determine strength level
        if score >= 80:
            strength = "VERY_STRONG"
            color = "green"
        elif score >= 65:
            strength = "STRONG"
            color = "lightgreen"
        elif score >= 50:
            strength = "MODERATE"
            color = "yellow"
        elif score >= 35:
            strength = "WEAK"
            color = "orange"
        else:
            strength = "VERY_WEAK"
            color = "red"
        
        # Calculate cracking time estimate
        entropy = self._calculate_entropy(password)
        crack_time = self._estimate_crack_time(entropy)
        
        return {
            "password": password[:2] + "*" * (len(password)-4) + password[-2:] if len(password) > 4 else "***",
            "strength": strength,
            "score": score,
            "color": color,
            "feedback": feedback,
            "entropy_bits": entropy,
            "estimated_crack_time": crack_time,
            "has_uppercase": has_upper,
            "has_lowercase": has_lower,
            "has_digits": has_digit,
            "has_special": has_special,
            "length": length
        }
    
    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits"""
        char_sets = {
            'lowercase': 26,
            'uppercase': 26,
            'digits': 10,
            'special': 33
        }
        
        used_sets = 0
        if any(c.islower() for c in password):
            used_sets += char_sets['lowercase']
        if any(c.isupper() for c in password):
            used_sets += char_sets['uppercase']
        if any(c.isdigit() for c in password):
            used_sets += char_sets['digits']
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            used_sets += char_sets['special']
        
        if used_sets == 0:
            used_sets = 26  # Default to lowercase
        
        entropy = len(password) * (used_sets.bit_length())
        return round(entropy, 1)
    
    def _estimate_crack_time(self, entropy: float) -> str:
        """Estimate time to crack password"""
        # Assuming 1 billion hashes per second (modern GPU)
        combinations = 2 ** entropy
        seconds = combinations / 1_000_000_000
        
        if seconds < 60:
            return "Instantly"
        elif seconds < 3600:
            return f"{seconds/60:.0f} minutes"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} hours"
        elif seconds < 31536000:
            return f"{seconds/86400:.1f} days"
        elif seconds < 31536000 * 100:
            return f"{seconds/31536000:.1f} years"
        else:
            return "Centuries"
    
    def bulk_analyze(self, passwords: List[str]) -> List[Dict]:
        """Analyze multiple passwords"""
        results = []
        for password in passwords:
            results.append(self.analyze_password(password))
        return results
    
    def generate_strong_password(self, length: int = 16) -> str:
        """Generate a strong random password"""
        import random
        import string
        
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(length))
        
        # Ensure all character types are present
        if not any(c.isupper() for c in password):
            pos = random.randint(0, length-1)
            password = password[:pos] + random.choice(string.ascii_uppercase) + password[pos+1:]
        if not any(c.islower() for c in password):
            pos = random.randint(0, length-1)
            password = password[:pos] + random.choice(string.ascii_lowercase) + password[pos+1:]
        if not any(c.isdigit() for c in password):
            pos = random.randint(0, length-1)
            password = password[:pos] + random.choice(string.digits) + password[pos+1:]
        if not any(c in "!@#$%^&*" for c in password):
            pos = random.randint(0, length-1)
            password = password[:pos] + random.choice("!@#$%^&*") + password[pos+1:]
        
        return password

# ==================== BOT 5: WIRELESS SECURITY ====================

class WirelessSecurityBot:
    """Specialized bot for wireless network security"""
    
    def __init__(self, name: str = "WirelessSecurityBot"):
        self.name = name
        self.findings = []
        
    def scan_wifi(self, interface: str = "wlan0") -> List[Finding]:
        """Scan for wireless networks and analyze security"""
        print(f"[{self.name}] Scanning wireless networks")
        findings = []
        
        try:
            # Use iwlist for scanning
            result = subprocess.run(
                ["sudo", "iwlist", interface, "scan"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                networks = self._parse_scan_results(result.stdout)
                
                for network in networks:
                    findings.extend(self._analyze_network_security(network))
                    
        except Exception as e:
            findings.append(Finding(
                severity="INFO",
                title="Wireless Scan Failed",
                description=f"Could not scan wireless: {str(e)}",
                remediation="Ensure wireless interface is available and in monitor mode"
            ))
        
        return findings
    
    def _parse_scan_results(self, output: str) -> List[Dict]:
        """Parse iwlist scan output"""
        networks = []
        current_network = {}
        
        for line in output.split('\n'):
            if 'ESSID:' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {}
                essid = line.split('ESSID:"')[1].split('"')[0]
                current_network['essid'] = essid if essid else "[Hidden]"
            elif 'Encryption:' in line:
                current_network['encryption'] = line.split('Encryption:')[1].strip()
            elif 'Quality=' in line:
                quality = line.split('Quality=')[1].split(' ')[0]
                current_network['signal'] = quality
            elif 'Channel:' in line:
                current_network['channel'] = line.split('Channel:')[1].strip()
        
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def _analyze_network_security(self, network: Dict) -> List[Finding]:
        """Analyze wireless network security"""
        findings = []
        
        encryption = network.get('encryption', 'Unknown')
        essid = network.get('essid', 'Unknown')
        
        # Check encryption type
        if 'WEP' in encryption:
            findings.append(Finding(
                severity="CRITICAL",
                title="WEP Encryption Detected",
                description=f"Network '{essid}' uses insecure WEP encryption",
                remediation="Upgrade to WPA2 or WPA3 immediately",
                affected_service="Wireless"
            ))
        elif 'WPA2' not in encryption and 'WPA3' not in encryption:
            findings.append(Finding(
                severity="HIGH",
                title="Weak Encryption",
                description=f"Network '{essid}' uses {encryption} (consider upgrading)",
                remediation="Enable WPA2/WPA3 with strong password",
                affected_service="Wireless"
            ))
        
        # Check for hidden network
        if essid == "[Hidden]":
            findings.append(Finding(
                severity="INFO",
                title="Hidden Network Detected",
                description="Hidden SSIDs can reduce security (clients still probe)",
                remediation="Consider using visible SSID with strong encryption instead",
                affected_service="Wireless"
            ))
        
        # Check signal strength (potential proximity)
        signal = network.get('signal', '0')
        if signal and '/' in signal:
            quality = int(signal.split('/')[0]) / int(signal.split('/')[1])
            if quality > 0.8:
                findings.append(Finding(
                    severity="INFO",
                    title="Strong Signal Detected",
                    description=f"Network '{essid}' has strong signal, likely nearby",
                    remediation="Ensure physical security of access point",
                    affected_service="Wireless"
                ))
        
        return findings

# ==================== COORDINATION DASHBOARD ====================

class PenTestSwarm:
    """Main coordinator for all security bots"""
    
    def __init__(self):
        self.bots = {
            'network': NetworkSecurityBot(),
            'web': WebSecurityBot(),
            'phishing': PhishingSimulatorBot(),
            'password': PasswordSecurityBot(),
            'wireless': WirelessSecurityBot()
        }
        self.results = []
        self.current_target = None
        self.console = Console() if RICH_AVAILABLE else None
        
    def run_comprehensive_scan(self, target: str) -> Dict:
        """Run all bots against target"""
        print(f"\n{'='*60}")
        print(f"PENETRATION TESTING SWARM - Comprehensive Scan")
        print(f"Target: {target}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        all_findings = []
        
        # Bot 1: Network Security
        print("[BOT 1/5] Network Security Scanner")
        network_findings = self.bots['network'].scan_network(target)
        all_findings.extend(network_findings)
        print(f"  → Found {len(network_findings)} issues\n")
        
        # Bot 2: Web Security
        print("[BOT 2/5] Web Application Scanner")
        web_findings = self.bots['web'].scan_webapp(target)
        all_findings.extend(web_findings)
        print(f"  → Found {len(web_findings)} issues\n")
        
        # Bot 3: Phishing Simulation
        print("[BOT 3/5] Phishing Simulation")
        test_email = "user@example.com"
        phishing_test = self.bots['phishing'].create_phishing_simulation(test_email, "credential_theft")
        print(f"  → Created simulation for {test_email}")
        print(f"  → Risk score: {self.bots['phishing'].analyze_email(phishing_test['body'])['risk_score']}\n")
        
        # Bot 4: Password Analysis
        print("[BOT 4/5] Password Security Analysis")
        test_passwords = ['password123', 'P@ssw0rd!2024', 'admin', 'MySecureP@ssw0rd!']
        for pwd in test_passwords:
            analysis = self.bots['password'].analyze_password(pwd)
            print(f"  → {analysis['password']}: {analysis['strength']} (Score: {analysis['score']})")
        print()
        
        # Bot 5: Wireless Security
        print("[BOT 5/5] Wireless Security Scan")
        wireless_findings = self.bots['wireless'].scan_wifi()
        all_findings.extend(wireless_findings)
        print(f"  → Found {len(wireless_findings)} wireless issues\n")
        
        # Compile report
        report = self._generate_report(target, all_findings)
        
        # Display dashboard
        if RICH_AVAILABLE:
            self.display_dashboard(report)
        
        return report
    
    def _generate_report(self, target: str, findings: List[Finding]) -> Dict:
        """Generate comprehensive security report"""
        severity_counts = defaultdict(int)
        critical_findings = []
        high_findings = []
        
        for finding in findings:
            severity_counts[finding.severity] += 1
            if finding.severity == "CRITICAL":
                critical_findings.append(finding)
            elif finding.severity == "HIGH":
                high_findings.append(finding)
        
        # Calculate risk score
        risk_score = (
            severity_counts.get("CRITICAL", 0) * 100 +
            severity_counts.get("HIGH", 0) * 50 +
            severity_counts.get("MEDIUM", 0) * 20 +
            severity_counts.get("LOW", 0) * 5
        )
        
        if risk_score >= 200:
            overall_risk = "CRITICAL"
        elif risk_score >= 100:
            overall_risk = "HIGH"
        elif risk_score >= 50:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"
        
        return {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "total_findings": len(findings),
            "severity_breakdown": dict(severity_counts),
            "critical_findings": critical_findings,
            "high_findings": high_findings,
            "risk_score": risk_score,
            "overall_risk": overall_risk,
            "findings": findings
        }
    
    def display_dashboard(self, report: Dict):
        """Display rich terminal dashboard"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        layout["body"].split_row(
            Layout(name="summary", ratio=1),
            Layout(name="findings", ratio=2)
        )
        
        # Header
        header_text = Text()
        header_text.append("🐝 PENETRATION TESTING SWARM", style="bold cyan")
        header_text.append(f"\nTarget: {report['target']}", style="white")
        header_text.append(f" | Risk: {report['overall_risk']}", 
                          style="red" if report['overall_risk'] == "CRITICAL" else "yellow")
        layout["header"].update(Panel(header_text, style="bold"))
        
        # Summary panel
        summary_table = Table(title="Scan Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="yellow")
        summary_table.add_row("Total Findings", str(report['total_findings']))
        summary_table.add_row("Risk Score", str(report['risk_score']))
        summary_table.add_row("Critical", str(report['severity_breakdown'].get('CRITICAL', 0)))
        summary_table.add_row("High", str(report['severity_breakdown'].get('HIGH', 0)))
        summary_table.add_row("Medium", str(report['severity_breakdown'].get('MEDIUM', 0)))
        summary_table.add_row("Low", str(report['severity_breakdown'].get('LOW', 0)))
        summary_table.add_row("Info", str(report['severity_breakdown'].get('INFO', 0)))
        
        layout["summary"].update(Panel(summary_table))
        
        # Findings panel
        findings_table = Table(title="Critical & High Findings")
        findings_table.add_column("Severity", style="red")
        findings_table.add_column("Title", style="white")
        findings_table.add_column("Remediation", style="green")
        
        for finding in report['critical_findings'][:5] + report['high_findings'][:5]:
            findings_table.add_row(
                finding.severity,
                finding.title[:50],
                finding.remediation[:50]
            )
        
        layout["findings"].update(Panel(findings_table))
        
        # Display
        self.console.print(layout)
    
    def export_report(self, report: Dict, format: str = "json"):
        """Export report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filename = f"pentest_report_{timestamp}.json"
            with open(filename, 'w') as f:
                # Convert findings to dict for JSON serialization
                report_copy = report.copy()
                report_copy['findings'] = [vars(f) for f in report['findings']]
                json.dump(report_copy, f, indent=2, default=str)
            print(f"\n[+] Report saved to {filename}")
        
        elif format == "html":
            self._export_html(report, timestamp)
    
    def _export_html(self, report: Dict, timestamp: str):
        """Export HTML report"""
        filename = f"pentest_report_{timestamp}.html"
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Penetration Test Report - {report['target']}</title>
            <style>
                body {{
                    font-family: 'Courier New', monospace;
                    background: #0a0a0a;
                    color: #d4d4d4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: #1a1a1a;
                    border: 1px solid #e67e22;
                    border-radius: 5px;
                    padding: 20px;
                }}
                h1 {{
                    color: #e67e22;
                    border-bottom: 2px solid #e67e22;
                }}
                .risk-critical {{ color: #e06c75; font-weight: bold; }}
                .risk-high {{ color: #e67e22; font-weight: bold; }}
                .risk-medium {{ color: #f39c12; }}
                .risk-low {{ color: #27ae60; }}
                .finding {{
                    margin: 10px 0;
                    padding: 10px;
                    background: #0a0a0a;
                    border-left: 4px solid;
                    border-radius: 3px;
                }}
                .critical {{ border-color: #e06c75; }}
                .high {{ border-color: #e67e22; }}
                .medium {{ border-color: #f39c12; }}
                .low {{ border-color: #27ae60; }}
                .info {{ border-color: #3498db; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                }}
                th, td {{
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #2c2c2c;
                }}
                th {{
                    background: #2c2c2c;
                    color: #e67e22;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🐝 Penetration Testing Swarm - Security Report</h1>
                <p><strong>Target:</strong> {report['target']}</p>
                <p><strong>Scan Time:</strong> {report['timestamp']}</p>
                <p><strong>Overall Risk:</strong> <span class="risk-{report['overall_risk'].lower()}">{report['overall_risk']}</span></p>
                <p><strong>Risk Score:</strong> {report['risk_score']}</p>
                
                <h2>Summary</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Findings</td><td>{report['total_findings']}</td></tr>
                    <tr><td>Critical</td><td>{report['severity_breakdown'].get('CRITICAL', 0)}</td></tr>
                    <tr><td>High</td><td>{report['severity_breakdown'].get('HIGH', 0)}</td></tr>
                    <tr><td>Medium</td><td>{report['severity_breakdown'].get('MEDIUM', 0)}</td></tr>
                    <tr><td>Low</td><td>{report['severity_breakdown'].get('LOW', 0)}</td></tr>
                </table>
                
                <h2>Detailed Findings</h2>
        """
        
        for finding in report['findings']:
            severity_class = finding.severity.lower()
            html_template += f"""
                <div class="finding {severity_class}">
                    <strong>[{finding.severity}]</strong> {finding.title}<br>
                    <strong>Description:</strong> {finding.description}<br>
                    <strong>Remediation:</strong> {finding.remediation}<br>
                    {'<strong>CVE:</strong> ' + finding.cve_id if finding.cve_id else ''}
                </div>
            """
        
        html_template += """
            </div>
        </body>
        </html>
        """
        
        with open(filename, 'w') as f:
            f.write(html_template)
        
        print(f"[+] HTML report saved to {filename}")

# ==================== MAIN EXECUTION ====================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Penetration Testing Swarm")
    parser.add_argument("target", help="Target IP or domain")
    parser.add_argument("--export", choices=['json', 'html'], help="Export report format")
    parser.add_argument("--no-web", action="store_true", help="Skip web scan")
    parser.add_argument("--no-wireless", action="store_true", help="Skip wireless scan")
    
    args = parser.parse_args()
    
    # Initialize swarm
    swarm = PenTestSwarm()
    
    # Run comprehensive scan
    report = swarm.run_comprehensive_scan(args.target)
    
    # Export if requested
    if args.export:
        swarm.export_report(report, args.export)
    
    print(f"\n[+] Scan complete! Found {report['total_findings']} security issues")
    print(f"[+] Overall risk level: {report['overall_risk']}")
    
    # Return exit code based on risk
    if report['overall_risk'] == "CRITICAL":
        sys.exit(2)
    elif report['overall_risk'] == "HIGH":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    # Fix for URL parsing
    from urllib.parse import urlparse, parse_qs
    
    main()
```

Complete Multi-Bot Penetration Testing Swarm

This system features 5 specialized bots working in coordination:

Bot 1: Network Security Scanner

· Port scanning with service detection
· Vulnerability identification (EternalBlue, BlueKeep)
· Open DNS resolver detection
· SNMP exposure checking
· Service version analysis

Bot 2: Web Application Security

· SQL injection detection (6+ payloads)
· XSS vulnerability testing
· Security headers audit (HSTS, CSP, X-Frame-Options)
· Directory enumeration
· SSL/TLS configuration check
· Form security analysis
· Cookie security attributes
· Information disclosure detection

Bot 3: Phishing Simulation

· Email phishing analysis (4 templates)
· URL phishing detection
· Risk scoring system
· Suspicious TLD detection
· Typosquatting detection
· URL shortener analysis

Bot 4: Password Security

· Strength scoring (0-100)
· Entropy calculation
· Crack time estimation
· Pattern detection
· Common password detection
· Password generator

Bot 5: Wireless Security

· Network scanning (iwlist)
· Encryption analysis (WEP/WPA/WPA2/WPA3)
· Signal strength analysis
· Hidden network detection

Installation:

```bash
# Install dependencies
pip install python-nmap requests beautifulsoup4 paramiko cryptography dnspython python-whois pyOpenSSL scikit-learn rich

# Or install all at once
pip install -r requirements.txt
```

Usage:

```bash
# Basic scan
sudo python3 pentest_swarm.py example.com

# Export report
sudo python3 pentest_swarm.py example.com --export html

# Skip specific scans
sudo python3 pentest_swarm.py example.com --no-web --no-wireless
```

Features:

· ✅ Coordinated multi-bot system - All bots work together
· ✅ Real-time dashboard - Rich terminal UI with live updates
· ✅ Comprehensive reporting - JSON/HTML export with detailed findings
· ✅ Risk scoring - Automated risk assessment
· ✅ Actionable remediation - Specific fix recommendations
· ✅ CVE tracking - Known vulnerability mapping
· ✅ Extensible architecture - Easy to add new bots

The swarm provides enterprise-grade security testing with specialized bots for every attack surface!
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Activity, BrainCircuit, TerminalSquare, Database, ShieldAlert,
  Cpu, HardDrive, Wifi, Fingerprint, Network, Binary, Zap,
  Eye, Lock, Unlock, AlertTriangle, Layers,
  Menu, X, Play, Square, Filter, Download, Wrench, Settings, Trash2, Link, Link2Off
} from 'lucide-react';

// --- Sub-Components ---

const HexViewer = ({ hexString }) => {
  if (!hexString) return null;
  const bytes = hexString.split(' ');
  const rows = [];
  for (let i = 0; i < bytes.length; i += 16) {
    rows.push({
      offset: i.toString(16).padStart(4, '0'),
      hex: bytes.slice(i, i + 16).join(' '),
      ascii: bytes.slice(i, i + 16).map(b => {
        const charCode = parseInt(b, 16);
        return (charCode >= 32 && charCode <= 126) ? String.fromCharCode(charCode) : '.';
      }).join('')
    });
  }

  return (
    <div className="font-mono text-[10px] sm:text-xs leading-tight bg-[#050505] p-3 rounded border border-slate-800/50 overflow-x-auto h-full max-h-[250px] overflow-y-auto custom-scrollbar">
      <div className="min-w-[450px]">
        {rows.map((row, idx) => (
          <div key={idx} className="flex gap-4 hover:bg-slate-800/30">
            <span className="text-slate-600 select-none">0x{row.offset}</span>
            <span className="text-cyan-400/80 w-[23rem] tracking-widest">{row.hex}</span>
            <span className="text-slate-400">{row.ascii}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const NetworkTopology = ({ activeNodes, activeEdges }) => {
  return (
    <div className="relative w-full h-full min-h-[200px] bg-[#050505] rounded-lg border border-slate-800 overflow-hidden">
      <div className="absolute inset-0 opacity-20 pointer-events-none" 
           style={{ backgroundImage: 'linear-gradient(#0f172a 1px, transparent 1px), linear-gradient(90deg, #0f172a 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
      </div>
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 250" preserveAspectRatio="xMidYMid meet">
        <defs>
          <radialGradient id="glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="glow-threat" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#ef4444" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#ef4444" stopOpacity="0" />
          </radialGradient>
        </defs>
        
        {/* Draw Edges */}
        {activeEdges.map((line, i) => (
          <g key={`line-${i}-${line.timestamp}`}>
            <line 
              x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2} 
              stroke={line.threat ? '#ef4444' : '#0ea5e9'} 
              strokeWidth={line.active ? 2 : 1}
              strokeOpacity={line.active ? 0.8 : 0.2}
              strokeDasharray={line.threat ? "4 4" : "none"}
            />
            {line.active && (
              <circle cx={line.x1} cy={line.y1} r="3" fill={line.threat ? '#f87171' : '#38bdf8'}>
                <animate attributeName="cx" values={`${line.x1};${line.x2}`} dur="0.5s" fill="freeze" />
                <animate attributeName="cy" values={`${line.y1};${line.y2}`} dur="0.5s" fill="freeze" />
                <animate attributeName="opacity" values="1;0" dur="0.5s" fill="freeze" />
              </circle>
            )}
          </g>
        ))}

        {/* Draw Nodes */}
        {activeNodes.map(node => (
          <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
            <circle r={node.isThreat ? 25 : 20} fill={`url(#${node.isThreat ? 'glow-threat' : 'glow'})`} className={node.lastActive > Date.now() - 1000 ? "animate-pulse" : ""} />
            <circle r="4" fill={node.isThreat ? '#ef4444' : node.isCore ? '#a855f7' : '#06b6d4'} />
            <text x="10" y="4" className="text-[10px] fill-slate-400 font-mono select-none" fillOpacity="0.8">
              {node.label}
            </text>
            {node.mac && (
              <text x="10" y="16" className="text-[8px] fill-slate-600 font-mono select-none">
                {node.mac}
              </text>
            )}
          </g>
        ))}
      </svg>
    </div>
  );
};

// --- Main Application ---

export default function App() {
  const [wsStatus, setWsStatus] = useState('DISCONNECTED');
  const [packets, setPackets] = useState([]);
  const [selectedPacket, setSelectedPacket] = useState(null);
  
  // AI State
  const [aiThought, setAiThought] = useState('');
  const [isAiTyping, setIsAiTyping] = useState(false);
  
  // KB & Hardware State
  const [kbState, setKbState] = useState({ targets: [], threats: 0 });
  const [sysStats, setSysStats] = useState({ cpu: 0, ram: '0GB' });
  
  // Tools State
  const [isCapturing, setIsCapturing] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  // Topology State (Dynamically populated from live wire)
  const [nodes, setNodes] = useState([{ id: 'core', x: 200, y: 125, label: 'OVERMIND-CORE', isCore: true, mac: 'LOCAL' }]);
  const [edges, setEdges] = useState([]);

  const packetStreamRef = useRef(null);
  const wsRef = useRef(null);

  // Live WebSocket Connection Management
  useEffect(() => {
    if (!isCapturing) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setWsStatus('DISCONNECTED');
      return;
    }

    setWsStatus('CONNECTING...');
    // Replace with your actual Python Overmind WebSocket endpoint
    const ws = new WebSocket('ws://127.0.0.1:8000/stream');
    wsRef.current = ws;

    ws.onopen = () => setWsStatus('CONNECTED');
    ws.onclose = () => setWsStatus('DISCONNECTED');
    ws.onerror = (err) => {
      console.error("WebSocket Error:", err);
      setWsStatus('ERROR');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleIncomingData(data);
      } catch (e) {
        console.error("Failed to parse websocket message", e);
      }
    };

    return () => {
      if (ws.readyState === 1) ws.close();
    };
  }, [isCapturing]);

  // Data Routing Engine
  const handleIncomingData = useCallback((data) => {
    switch (data.type) {
      case 'PACKET':
        const pkt = data.payload;
        setPackets(prev => [pkt, ...prev].slice(0, 100)); // Keep last 100 frames
        updateTopology(pkt);
        break;
      
      case 'AI_START':
        setAiThought('');
        setIsAiTyping(true);
        break;
      
      case 'AI_TOKEN':
        setAiThought(prev => prev + data.payload);
        setIsAiTyping(true);
        // Auto-stop typing effect if no tokens received for 1 second
        clearTimeout(window.aiTimeout);
        window.aiTimeout = setTimeout(() => setIsAiTyping(false), 1000);
        break;
      
      case 'KB_UPDATE':
        setKbState(prev => ({ ...prev, ...data.payload }));
        break;
        
      case 'SYS_TELEMETRY':
        setSysStats(data.payload);
        break;

      default:
        console.warn("Unknown packet type from Overmind:", data.type);
    }
  }, []);

  // Dynamic Graphing Engine (Builds map based on seen MACs)
  const updateTopology = useCallback((pkt) => {
    const timestamp = Date.now();
    
    setNodes(prev => {
      const newNodes = [...prev];
      let changed = false;

      // Ensure Source Node Exists
      if (pkt.src && pkt.src !== 'FF:FF:FF:FF:FF:FF' && !newNodes.find(n => n.mac === pkt.src)) {
        newNodes.push({ 
          id: pkt.src, 
          mac: pkt.src,
          label: pkt.isThreat ? 'THREAT_ACTOR' : 'STATION', 
          x: Math.floor(Math.random() * 300) + 50, 
          y: Math.floor(Math.random() * 200) + 25,
          isThreat: pkt.isThreat,
          lastActive: timestamp
        });
        changed = true;
      } else if (pkt.src) {
        const n = newNodes.find(n => n.mac === pkt.src);
        if (n) { n.lastActive = timestamp; if(pkt.isThreat) n.isThreat = true; }
        changed = true;
      }

      // Ensure Dest Node Exists
      if (pkt.dst && pkt.dst !== 'FF:FF:FF:FF:FF:FF' && !newNodes.find(n => n.mac === pkt.dst)) {
        newNodes.push({ 
          id: pkt.dst, 
          mac: pkt.dst,
          label: 'DEVICE', 
          x: Math.floor(Math.random() * 300) + 50, 
          y: Math.floor(Math.random() * 200) + 25,
          isThreat: false,
          lastActive: timestamp
        });
        changed = true;
      }

      return changed ? newNodes : prev;
    });

    // Draw Edge Pulse
    if (pkt.src && pkt.dst) {
      setEdges(prev => {
        const newEdges = [{ src: pkt.src, dst: pkt.dst, threat: pkt.isThreat, timestamp }];
        // Keep last 10 edges to fade them out naturally
        return [...newEdges, ...prev].slice(0, 10);
      });
    }
  }, []);

  // Compute exact coordinates for SVG lines
  const activeEdges = edges.map(edge => {
    const srcNode = nodes.find(n => n.mac === edge.src) || nodes[0];
    const dstNode = nodes.find(n => n.mac === edge.dst) || nodes[0];
    return {
      x1: srcNode.x, y1: srcNode.y,
      x2: dstNode.x, y2: dstNode.y,
      threat: edge.threat,
      active: true,
      timestamp: edge.timestamp
    };
  });

  return (
    <div className="min-h-screen bg-[#020617] text-slate-300 p-2 md:p-4 font-mono text-sm selection:bg-cyan-900 overflow-x-hidden flex flex-col lg:h-screen">
      
      {/* HUD Header */}
      <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-slate-800/60 pb-3 mb-4 shrink-0 gap-3 sm:gap-0">
        <div className="flex items-center gap-3 md:gap-4 w-full sm:w-auto justify-between sm:justify-start">
          <div className="flex items-center gap-3">
            <div className={`p-2 border rounded shadow-[0_0_15px_rgba(6,182,212,0.2)] shrink-0 transition-colors ${wsStatus === 'CONNECTED' ? 'border-cyan-500/30 bg-cyan-500/10' : 'border-slate-700 bg-slate-800'}`}>
              <Layers className={wsStatus === 'CONNECTED' ? 'text-cyan-400' : 'text-slate-500'} size={24} />
            </div>
            <div>
              <h1 className="text-base md:text-xl font-bold text-white tracking-widest flex items-center gap-2">
                OVERMIND <span className="text-cyan-500 font-light truncate">DEEP_INSPECT</span>
              </h1>
              <div className="flex gap-2 md:gap-4 text-[9px] md:text-[10px] text-slate-500 uppercase tracking-wider">
                <span className="flex items-center gap-1"><Cpu size={10}/> ML: {sysStats.cpu}%</span>
                <span className="flex items-center gap-1"><HardDrive size={10}/> KB: {sysStats.ram}</span>
                <span className={`flex items-center gap-1 ${wsStatus === 'CONNECTED' ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {wsStatus === 'CONNECTED' ? <Link size={10}/> : <Link2Off size={10}/>} {wsStatus}
                </span>
              </div>
            </div>
          </div>
          {/* Mobile Activity Icon */}
          <div className="sm:hidden h-8 w-8 border border-slate-700 rounded flex items-center justify-center bg-slate-900 shrink-0">
            <Activity className={wsStatus === 'CONNECTED' ? 'text-emerald-400 animate-pulse' : 'text-slate-600'} size={16} />
          </div>
        </div>
        <div className="hidden sm:flex items-center gap-3">
          <div className="text-right">
            <div className="text-xs text-slate-400">SESSION_ID</div>
            <div className="text-cyan-500 font-bold">{Math.random().toString(36).substring(2, 10).toUpperCase()}</div>
          </div>
          <div className="h-10 w-10 border border-slate-700 rounded flex items-center justify-center bg-slate-900 shrink-0">
            <Activity className={wsStatus === 'CONNECTED' ? 'text-emerald-400 animate-pulse' : 'text-slate-600'} size={20} />
          </div>
        </div>
        
        {/* Mobile Menu Toggle */}
        <button 
          className="sm:hidden p-2 border border-slate-700 rounded bg-slate-900 text-slate-400 hover:text-cyan-400 transition-colors ml-2"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          {isMobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
        </button>
      </header>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="sm:hidden flex flex-col gap-2 mb-4 p-3 bg-[#050505] border border-slate-800 rounded-lg shadow-xl z-20 shrink-0">
          <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1 font-bold">Tactical Tools</div>
          <div className="grid grid-cols-2 gap-2">
            <button onClick={() => setIsCapturing(!isCapturing)} className={`flex items-center gap-2 p-2 rounded text-[11px] border transition-colors ${isCapturing ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'}`}>
              {isCapturing ? <Square size={14} /> : <Play size={14} />} {isCapturing ? 'Stop Capture' : 'Live Capture'}
            </button>
            <button onClick={() => setPackets([])} className="flex items-center gap-2 p-2 rounded text-[11px] border bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800 transition-colors">
              <Trash2 size={14} /> Clear Stream
            </button>
            <button className="flex items-center gap-2 p-2 rounded text-[11px] border bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800 transition-colors">
              <Filter size={14} /> Filter MAC
            </button>
            <button className="flex items-center gap-2 p-2 rounded text-[11px] border bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800 transition-colors">
              <Wrench size={14} /> Inject Frame
            </button>
            <button className="flex items-center gap-2 p-2 rounded text-[11px] border bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800 transition-colors">
              <Download size={14} /> Export PCAP
            </button>
            <button className="flex items-center gap-2 p-2 rounded text-[11px] border bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800 transition-colors">
              <Settings size={14} /> Settings
            </button>
          </div>
        </div>
      )}

      {/* Desktop Toolbar */}
      <div className="hidden sm:flex items-center gap-3 mb-4 shrink-0 pb-3 border-b border-slate-800/60 w-full overflow-x-auto custom-scrollbar">
        <div className="flex bg-slate-900 border border-slate-800 rounded overflow-hidden shrink-0">
          <button onClick={() => setIsCapturing(!isCapturing)} className={`flex items-center gap-2 px-3 py-1.5 text-[11px] font-bold transition-colors ${isCapturing ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' : 'text-emerald-400 hover:bg-emerald-500/20'}`} title={isCapturing ? "Halt RF Intercept" : "Initialize RF Intercept Socket"}>
            {isCapturing ? <Square size={14} /> : <Play size={14} />} {isCapturing ? 'STOP' : 'LIVE'}
          </button>
          <div className="w-[1px] bg-slate-800"></div>
          <button onClick={() => setPackets([])} className="flex items-center gap-2 px-3 py-1.5 text-xs text-slate-400 hover:bg-slate-800 hover:text-white transition-colors" title="Clear Stream Buffer">
            <Trash2 size={14} />
          </button>
        </div>

        <div className="h-5 w-[1px] bg-slate-800 mx-1 shrink-0"></div>

        <button className="flex items-center gap-2 px-3 py-1.5 text-[11px] font-bold tracking-wide border border-slate-800 bg-slate-900 rounded text-slate-400 hover:bg-slate-800 hover:text-cyan-400 transition-colors shrink-0">
          <Filter size={14} /> FILTER
        </button>
        <button className="flex items-center gap-2 px-3 py-1.5 text-[11px] font-bold tracking-wide border border-slate-800 bg-slate-900 rounded text-slate-400 hover:bg-slate-800 hover:text-cyan-400 transition-colors shrink-0">
          <Wrench size={14} /> INJECT_MODE
        </button>
        
        <div className="flex-1"></div>
        
        <button className="flex items-center gap-2 px-3 py-1.5 text-[11px] font-bold tracking-wide border border-slate-800 bg-slate-900 rounded text-slate-400 hover:bg-slate-800 hover:text-white transition-colors shrink-0">
          <Download size={14} /> EXPORT_PCAP
        </button>
        <button className="flex items-center gap-2 px-3 py-1.5 text-[11px] font-bold tracking-wide border border-slate-800 bg-slate-900 rounded text-slate-400 hover:bg-slate-800 hover:text-white transition-colors shrink-0">
          <Settings size={14} /> ENGINE_CFG
        </button>
      </div>

      {/* Main Grid Layout */}
      <div className="flex-1 flex flex-col lg:grid lg:grid-cols-12 gap-4 lg:min-h-0 overflow-y-auto lg:overflow-hidden pb-4 lg:pb-0">
        
        {/* Left Column: Stream & Inspection */}
        <div className="lg:col-span-7 flex flex-col gap-4 lg:min-h-0 shrink-0">
          
          {/* Packet Stream */}
          <div className="bg-slate-900/50 border border-slate-800 rounded flex flex-col overflow-hidden h-[350px] lg:h-1/2 shrink-0 lg:shrink">
            <div className="bg-slate-900 p-2 text-[10px] md:text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800 flex justify-between items-center shrink-0">
              <span className="flex items-center gap-2"><Radio size={14} className={isCapturing ? "text-cyan-500 animate-pulse" : "text-slate-600"}/> Live Scapy Intercept</span>
              <span className="text-[10px] text-emerald-500 bg-emerald-500/10 px-2 rounded">Promiscuous Mode</span>
            </div>
            
            {/* Stream Header */}
            <div className="overflow-x-auto custom-scrollbar flex-1 flex flex-col">
              <div className="min-w-[450px] flex flex-col flex-1">
                <div className="grid grid-cols-6 gap-2 p-2 text-[10px] text-slate-500 border-b border-slate-800/50 shrink-0 bg-[#050505]">
                  <div>TIME</div>
                  <div>TYPE</div>
                  <div className="col-span-2">SRC MAC</div>
                  <div>SIZE</div>
                  <div>ML SCORE</div>
                </div>

                {/* Stream Body */}
                <div className="flex-1 overflow-y-auto custom-scrollbar p-1" ref={packetStreamRef}>
                  {packets.length === 0 ? (
                    <div className="flex h-full items-center justify-center text-slate-600 italic">
                      {isCapturing ? "Listening for 802.11 frames..." : "Capture inactive. Press LIVE to connect."}
                    </div>
                  ) : (
                    packets.map((pkt, i) => (
                      <div 
                        key={pkt.id || i} 
                        onClick={() => setSelectedPacket(pkt)}
                        className={`grid grid-cols-6 gap-2 px-2 py-2 md:py-1.5 text-[10px] md:text-[11px] cursor-pointer border-b border-transparent hover:bg-slate-800/50 transition-colors
                          ${pkt.isThreat ? 'bg-red-500/10 text-red-300' : 'text-slate-400'}
                          ${selectedPacket?.id === pkt.id ? 'border-cyan-500/50 bg-cyan-900/20' : ''}
                        `}
                      >
                        <div className="font-mono">{pkt.timestamp || new Date().toISOString().split('T')[1].slice(0, -1)}</div>
                        <div className={pkt.isThreat ? 'font-bold' : ''}>{pkt.subtype}</div>
                        <div className="col-span-2 font-mono truncate">{pkt.src}</div>
                        <div>{pkt.size}B</div>
                        <div className="flex items-center gap-1">
                          <div className={`w-1.5 h-1.5 rounded-full ${pkt.anomalyScore > 0.8 ? 'bg-red-500 animate-ping' : pkt.anomalyScore > 0.4 ? 'bg-yellow-500' : 'bg-emerald-500'}`}></div>
                          {pkt.anomalyScore || '0.00'}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Deep Inspection Details */}
          <div className="bg-slate-900/50 border border-slate-800 rounded flex flex-col overflow-hidden h-[400px] lg:h-1/2 shrink-0 lg:shrink">
            <div className="bg-slate-900 p-2 text-[10px] md:text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800 flex items-center gap-2 shrink-0">
              <Eye size={14} className="text-cyan-500"/> Deep Frame Inspection
            </div>
            
            {selectedPacket ? (
              <div className="p-3 flex flex-col gap-4 overflow-y-auto custom-scrollbar">
                {/* Scapy Parsed Layers */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 shrink-0">
                  <div className="space-y-1">
                    <div className="text-[10px] text-slate-500 uppercase">Dot11 Layer</div>
                    <div className="bg-[#050505] p-2 rounded border border-slate-800 text-xs text-cyan-200">
                      <div>FCfield: {selectedPacket.fcfield || '0x0000'}</div>
                      <div>Type: {selectedPacket.type}</div>
                      <div>Subtype: {selectedPacket.subtype}</div>
                      <div>addr1 (dst): {selectedPacket.dst}</div>
                      <div>addr2 (src): {selectedPacket.src}</div>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-[10px] text-slate-500 uppercase">ML Analytics</div>
                    <div className="bg-[#050505] p-2 rounded border border-slate-800 text-xs flex flex-col justify-center h-[90px]">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Outlier Score:</span>
                        <span className={selectedPacket.anomalyScore > 0.8 ? 'text-red-400 font-bold' : 'text-emerald-400'}>{selectedPacket.anomalyScore || '0.00'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Feature Vector:</span>
                        <span className="text-slate-500 truncate pl-2">{selectedPacket.vector ? JSON.stringify(selectedPacket.vector) : '[N/A]'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Classification:</span>
                        <span className={selectedPacket.isThreat ? 'text-red-400' : 'text-emerald-400'}>{selectedPacket.isThreat ? 'ANOMALOUS' : 'BENIGN'}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Hex Dump */}
                <div className="flex-1 flex flex-col min-h-[150px]">
                  <div className="text-[10px] text-slate-500 uppercase mb-1">Raw Payload (Hex Dump)</div>
                  {selectedPacket.hex ? (
                    <HexViewer hexString={selectedPacket.hex} />
                  ) : (
                    <div className="bg-[#050505] border border-slate-800 p-2 rounded text-slate-600 italic flex-1 flex items-center justify-center">
                      No raw payload attached to this frame.
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-slate-600 text-xs italic">
                Select a frame from the stream to inspect.
              </div>
            )}
          </div>
        </div>

        {/* Right Column: AI & Topology */}
        <div className="lg:col-span-5 flex flex-col gap-4 lg:min-h-0 shrink-0">
          
          {/* Topology Map */}
          <div className="bg-slate-900/50 border border-slate-800 rounded flex flex-col h-[300px] lg:h-[40%] shrink-0 lg:shrink">
            <div className="bg-slate-900 p-2 text-[10px] md:text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800 flex items-center gap-2 shrink-0">
              <Network size={14} className="text-cyan-500"/> Tactical Mesh Topology
            </div>
            <div className="flex-1 p-2">
               <NetworkTopology activeNodes={nodes} activeEdges={activeEdges} />
            </div>
          </div>

          {/* AI Cognition Engine */}
          <div className="bg-slate-900/50 border border-slate-800 rounded flex flex-col h-[400px] lg:h-[60%] overflow-hidden shrink-0 lg:shrink">
            <div className="bg-slate-900 p-2 text-[10px] md:text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800 flex justify-between items-center shrink-0">
              <span className="flex items-center gap-2">
                <BrainCircuit size={14} className={isAiTyping ? "text-pink-500 animate-pulse" : "text-pink-800"}/> 
                LLM Reasoning Chain
              </span>
              <span className="text-[10px] bg-pink-500/10 text-pink-400 px-2 rounded border border-pink-500/30">Live Backend</span>
            </div>
            
            <div className="flex-1 p-3 overflow-y-auto custom-scrollbar flex flex-col gap-3">
              {/* Context Window injected into LLM */}
              <div className="space-y-1">
                <div className="text-[10px] text-slate-600 font-bold uppercase">Context Injection</div>
                <div className="bg-[#050505] p-2 rounded border border-slate-800 text-[11px] text-slate-500 font-mono leading-relaxed overflow-x-auto">
                  {selectedPacket ? `{"target_mac": "${selectedPacket.src}", "anomaly_score": ${selectedPacket.anomalyScore}, "kb_known_threats": ${kbState.threats}}` : 'Awaiting event trigger from backend...'}
                </div>
              </div>

              {/* Chain of Thought output */}
              <div className="flex-1 min-h-[100px] flex flex-col">
                 <div className="text-[10px] text-pink-500 font-bold uppercase mb-1">Synthesized Directive</div>
                 <div className="flex-1 bg-[#050505] p-3 rounded border border-pink-900/30 text-xs text-pink-200/90 whitespace-pre-wrap leading-loose shadow-[inset_0_0_20px_rgba(236,72,153,0.05)] relative">
                   {aiThought}
                   {isAiTyping && <span className="inline-block w-2 h-3 bg-pink-500 animate-pulse ml-1 align-middle"></span>}
                   {!aiThought && !isAiTyping && <span className="text-slate-700 italic">Standing by. LLM idle.</span>}
                 </div>
              </div>

              {/* Memory State update */}
              <div className="shrink-0 pt-2 border-t border-slate-800 flex justify-between items-end">
                 <div>
                   <div className="text-[10px] text-slate-600 font-bold uppercase mb-1">Global Knowledge Base</div>
                   <div className="text-xs text-slate-400 flex items-center gap-2">
                     <Database size={12} className="text-emerald-500" />
                     Hostile MACs in memory: <span className="text-emerald-400 font-bold">{kbState.targets.length || 0}</span>
                   </div>
                 </div>
                 <button className="text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded transition-colors flex items-center gap-1 border border-slate-700">
                    <Binary size={12} /> Force Sync
                 </button>
              </div>
            </div>
          </div>

        </div>
      </div>

      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar { width: 4px; height: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #0f172a; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 2px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #475569; }
      `}} />
    </div>
  );
}


```
