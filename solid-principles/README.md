# 📜 S.O.L.I.D. Principles

> 📅 Last updated: 2026-02-07 11:47 UTC
> 🔗 [View in Notion](https://www.notion.so/S-O-L-I-D-Principles-2fe6249cbbe280d39866cf3c995bdf32)

---

---

### Overview

This document outlines the SOLID principles.

---

### Table of Contents

1. What is Secure Shell (SSH)?
2. Why SSH is Important?
3. How SSH Works & Versions?
4. Use Cases & Real-Life Examples?
5. Installation Guide (Mac, Windows, Linux)?
6. SSH Commands in Action?
  7. Key Generation
  8. Copy Key to Server
  9. Connecting to Server
  10. Port Forwarding & Tunneling
11. CLI vs GUI Tools
12. Best Practices & Security

---

### 1. What are S.O.L.I.D. principle?

[Explain what SOLID is, what it stands for, and its main purpose.]

- Set of five design principles, that help guide object oriented software development.
- SSH stands for “Secure SHell” and was developed as a safer alternative to older, unencrypted protocols like Telnet and FTP.
- Note: Don't mix it up with "SSL".
- SSH ensures that all data transmitted between client and server is encrypted, maintaining confidentiality, integrity and authenticity.

### 2. Single Responsibility Principle (SRP)

[Explain what SOLID is, what it stands for, and its main purpose.]

-  basically, the idea is
 a class should have only one reason to change
 in another words, each class should be responsible for a single part of the software functionality
- Suppose there is any employee class, which have multiple responsibilities
 it is source. The employee information such as name salary etc.
 It contains the logic to determine the employee paycheck.
 It handles saving the employee data into the database.
 It also generate a report based on employ data.
- Class employee { private string name; private double salary; public double calculate pay(){} public void, safe to database(){} public string generate report(){}  }
- The issue here is that this class has too many reasons to change
 it, business logic for calculating the changes
- SSH stands for “Secure SHell” and was developed as a safer alternative to older, unencrypted protocols like Telnet and FTP.
- Note: Don't mix it up with "SSL".
- SSH ensures that all data transmitted between client and server is encrypted, maintaining confidentiality, integrity and authenticity.

---

### 2. Single Responsibility Principle (SRP)?

[Detail the significance of SRP.]
<details>
<summary>**2.1) SSH is the backbone of secure remote system management.**</summary>

- Enables remote command-line access.
- Protects against eavesdropping, password sniffing, & data tampering during communication.
- Server administration – manage and deploy applications, databases, services, and perform troubleshooting.
- Secure file transfers (SCP and SFTP).
- Tunneling of traffic (port forwarding).
- Passwordless login – essential for automation and scripting in DevOps workflows.
</details>
<details>
<summary>**2.2) Supported across all major platforms.**</summary>

- Linux,
- macOS,
- Windows,
- Android,
- iOS.
</details>

---

### 3. How SSH Works & Versions?

[Describe the underlying principles, SSH protocols (SSH-1 vs SSH-2), and how the connection is established.]
> 📌 SSH is a ***”cryptographic”*** network protocol used to securely access and manage remote computers over an ***”unsecured network”***.
<details>
<summary>**3.1) What is an Unsecured Network?**</summary>

Ans) A network where data is transmitted without encryption, meaning the information being exchanged between devices can be read, intercepted, or modified by anyone who has access to that network.
- This means data, such as login credentials and financial details, is transmitted in plain text and can be easily read by malicious users on the same network.
- In simple terms, it is like speaking in a crowded room where anyone can overhear.
- Example :
  - Public Wi-Fi in cafés, malls, airports.
  - Home Wi-Fi without a password
  - Old protocols like Telnet or FTP.
</details>
<details>
<summary>**3.2) What is Cryptography?**</summary>

Ans) Cryptography is the technique of securing data, by converting plain text into cipher text, (using mathematical algorithms and cryptographic keys), so that only the intended person can read and understand it.
- In simple terms, Encryption + Decryption = Cryptography.
- Encryption = (hiding the message).
- Decryption = (revealing the message).
</details>
<details>
<summary>**3.3) Type of Cryptography?**</summary>

Ans) Two kinds - Symmetric Key and Asymmetric Key.
- Symmetric Key 🔑: Same secret key is used for both encryption and decryption. Example: AES encryption (used in Wi-Fi).
- Asymmetric Key 🔑🗝️: Public key for encryption, private key for decryption (key pair). Example: SSH, SSL (HTTPS), Digital Signatures.
</details>
<details>
<summary>**3.4) Why Cryptography is Important?**</summary>

Ans) It protects:
- Your passwords when you log into websites.
- Your messages in apps like WhatsApp.
- Your financial transactions during online banking.
- Remote connections via SSH, VPN, and HTTPS
</details>
<details>
<summary>**3.5) Main Goals of Cryptography?**</summary>

Ans) Four main goals:
- Confidentiality – Keep data private (Encryption).
- Integrity – Ensure data isn’t changed.
- Authentication – Verify user identity.
- Non-repudiation – Prevent denial of actions (e.g. signed emails)
</details>

---

### 4. Use Cases & Real-Life Examples?

[List and describe where SSH is used, with practical examples relevant to different user groups.]

- It’s the go-to tool for system administrators, developers, and DevOps professionals to remotely manage systems without compromising security.

---

### 5. Installation Guide (Mac, Windows, Linux)?

[Instructions for SSH setup on macOS]
<details>
<summary>**5.1) macOS (All versions, Intel & Apple Silicon)**</summary>

<details>
<summary>**5.1.1) Overview**</summary>

1. OpenSSH Client and Server, are pre-installed on macOS by default.
  - However, only the OpenSSH Client is active and available for immediate use.
  - The OpenSSH Server is present but disabled by default and must be manually enabled to accept incoming connections.
2. If OpenSSH is missing or outdated, you can install or update it manually using the steps below.
</details>
<details>
<summary>**5.1.2) How to check if OpenSSH is already installed?**</summary>

- Open Terminal (or you can press Cmd + Space, type Terminal, and press Enter).
- Run this command:
  ```bash
  ssh -V
  ```
- If OpenSSH is installed, you’ll see something like:
  ```bash
  OpenSSH_9.4p1, LibreSSL 3.3.6
  ```
</details>
<details>
<summary>**5.1.3) How to setup OpenSSH manually on macOS?**</summary>

<details>
<summary><u>Method 1: Install via Homebrew</u> [CLI-based]</summary>

<details>
<summary>How to install Homebrew (if not already installed):</summary>

3. Open Terminal.
4. Run this command, to install Homebrew:
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
  *(It automatically detects Apple Silicon vs Intel)
  Note: Installs Homebrew in:
  1) Apple Silicon → /opt/homebrew
  2) Intel → /usr/local*
5. Add Homebrew to Shell Profile:
  - Check Homebrew version:
      ```bash
      brew -v
      ```
      *(Displays the installed Homebrew version)*
6. Verify installation:
  - Check Homebrew version:
      ```bash
      brew -v
      ```
      *(Displays the installed Homebrew version)*
  - Run a diagnostic test:
      ```bash
      brew doctor
      ```
      *(Runs health checks on your Homebrew setup and suggests any fixes if needed)*
  - Verify installation path:
      ```bash
      which brew
      ```
      *(Shows the exact path of the brew binary)*
</details>
<details>
<summary>How to install OpenSSH Client & Server:</summary>

7. Open Terminal.
8. Run this command, to install OpenSSH (includes both Client & Server):
  ```bash
  brew install openssh
  ```
9. Verify installation:
  - Using Homebrew command:
      ```bash
      brew list openssh
      ```
      *(Lists all files, paths, and versions installed by the OpenSSH package via Homebrew)*
  - Using classic SSH command:
      ```bash
      ssh -V
      ```
      *(Shows installed OpenSSH client version to confirm setup)*
10. (Optional Step): You can use Homebrew to upgrade, uninstall, and reinstall OpenSSH Client & Server:
  - Run this command, to upgrade OpenSSH:
      ```bash
      brew upgrade openssh
      ```
      *(Updates both OpenSSH Client & Server, to the latest version, available in the Homebrew repository)*
  - Run this command, to uninstall OpenSSH:
      ```bash
      brew uninstall openssh
      ```
      *(Completely removes OpenSSH Client & Server, which was installed via Homebrew)*
  - Run this command, to reinstall OpenSSH:
      ```bash
      brew reinstall openssh
      ```
      *(Performs a clean reinstall, it is useful if the installation was corrupted or misconfigured)*
</details>
<details>
<summary>(Optional Step): How to manage OpenSSH Server:</summary>

- Open Terminal.
</details>
</details>
</details>
</details>
[Instructions for SSH setup on Windows]
<details>
<summary>**5.2) Windows (Versions 10 & 11)**</summary>

<details>
<summary>**5.2.1) Overview**</summary>

1. OpenSSH Client and Server, come as an optional feature on Windows 10 and 11.
2. If OpenSSH is missing or outdated, you can install or update it manually using the steps below.
</details>
<details>
<summary>**5.2.2) How to check if OpenSSH is already installed?**</summary>

- Open PowerShell or Command Prompt (or you can press Win + R, type cmd, press Enter).
- Run this command:
```powershell
ssh -V
```
- If OpenSSH is installed, you’ll see something like:
```powershell
OpenSSH_for_Windows_8.6p1, LibreSSL 3.4.3
```
</details>
<details>
<summary>**5.2.3) How to setup OpenSSH manually on Windows?**</summary>

<details>
<summary><u>Method 1: Install via Windows Settings</u> [GUI-based, for Beginners]</summary>

<details>
<summary>To install SSH Client:</summary>

3. Open Settings → Apps → Optional Features.
4. Scroll down and check if OpenSSH Client is already listed.
  - If yes: SSH Client is already installed.
5. If not:
  - Click “Add a feature”.
  - Search for OpenSSH Client.
  - Click Install.
6. After installation, restart the terminal and verify:
  ```powershell
  ssh -V
  ```
</details>
<details>
<summary>(Optional Step): To install SSH Server:</summary>

7. In Settings → Apps → Optional Features.
8. Scroll down and check if OpenSSH Server is already listed.
  - If yes: SSH Server is already installed.
9. If not:
  - Click “Add a feature”.
  - Search for OpenSSH Server.
  - Click Install.
10. To enable and start SSH Server:
  - Open Services (or you can press Win + R, type services.msc, press Enter).
  - Find SSH Server (Service name: sshd).
  - Right-click → Select Properties → Set Startup Type to “Automatic”.
  - Click Start.
  - Click Apply, then click OK.
11. To stop and disable SSH Server:
  - Open Services (or you can press Win + R, type services.msc, press Enter).
  - Find SSH Server (Service name: sshd).
  - Click Stop.
  - Right-click → Select Properties → Set Startup Type to “Disabled”.
  - Click Apply, then click OK.
</details>
</details>
<details>
<summary><u>Method 2: Install via PowerShell</u> [CLI-based, for System Admins]</summary>

<details>
<summary>To install SSH Client:</summary>

12. Open PowerShell as Administrator.
13. Run this command, to install SSH Client:
  ```powershell
  Add-WindowsCapability -Online -Name OpenSSH.Client*
  ```
14. Verify installation:
  ```powershell
  ssh -V
  ```
</details>
<details>
<summary>(Optional Step): To install SSH Server:</summary>

15. Open PowerShell as Administrator.
16. Run this command, to install SSH Server:
  ```powershell
  Add-WindowsCapability -Online -Name OpenSSH.Server*
  ```
17. To check status of SSH Server:
  ```powershell
  Get-Service sshd
  ```
18. To enable and start SSH Server:
  ```powershell
  Set-Service -Name sshd -StartupType 'Automatic'
  Start-Service sshd
  ```
  *(Best practice: enable first, then start)*
19. To stop and disable SSH Server:
  ```powershell
  Stop-Service sshd
  Set-Service -Name sshd -StartupType 'Disabled'
  ```
  *(Best practice: stop first, then disable)*
</details>
</details>
<details>
<summary><u>Method 3: Install via Winget</u> [CLI-based, for DevOps Professionals]</summary>

<details>
<summary>To install, upgrade, uninstall, and reinstall SSH Client & SSH Server:</summary>

20. Open PowerShell or Command Prompt.
21. Run this command, to install OpenSSH (it includes both SSH Client & SSH Server):
  ```powershell
  winget install OpenSSH
  ```
22. Verify installation:
  - Using Winget command:
      ```powershell
      winget list OpenSSH
      ```
      *(Shows installed OpenSSH packages and versions to confirm installation)*
  - Using classic SSH command:
      ```powershell
      ssh -V
      ```
      *(Displays current OpenSSH client version to verify setup)*
23. (Optional Step): You can use Winget to upgrade, uninstall, and reinstall SSH Client & SSH Server:
  - Run this command, to upgrade OpenSSH:
      ```powershell
      winget upgrade OpenSSH
      ```
      *(Updates both SSH Client & SSH Server, to the latest version)*
  - Run this command, to uninstall OpenSSH:
      ```powershell
      winget uninstall OpenSSH
      ```
      *(Completely removes the SSH Client and SSH Server from your system)*
  - Run this command, to reinstall OpenSSH:
      ```powershell
      winget install OpenSSH --force
      ```
      *(Useful if the installation was corrupted or misconfigured)*
</details>
<details>
<summary>(Optional Step): To manage SSH Server:</summary>

24. Open PowerShell as Administrator.
25. Run this command, to install SSH Server:
  - You can skip this step, if you have already run this command above.
      ```powershell
      winget install OpenSSH
      ```
  - Winget installs both SSH Client & SSH Server together, so there’s no need to run this command again.
  - But after installation, only the SSH Client is active by default. The SSH Server (sshd) needs to be manually started and enabled.
26. To check status of SSH Server:
  ```powershell
  Get-Service sshd
  ```
27. To enable and start SSH Server:
  ```powershell
  Set-Service -Name sshd -StartupType 'Automatic'
  Start-Service sshd
  ```
  *(Best practice: enable first, then start)*
28. To stop and disable SSH Server:
  ```powershell
  Stop-Service sshd
  Set-Service -Name sshd -StartupType 'Disabled'
  ```
  *(Best practice: stop first, then disable)*
</details>
</details>
</details>
</details>
[Instructions for SSH setup on Linux]

---

### 6. SSH Commands in Action?

Key Generation:
[Steps and explanation for generating SSH keys.]
Copy Key to Server:
[How to copy a public key to a remote server for passwordless login.]
Connecting to Server:
[Basic commands and options for connecting to a remote server.]
Port Forwarding & Tunneling:
[Examples and use-cases for SSH port forwarding and tunneling.]

---

### 7. CLI vs GUI Tools?

[Compare command-line tools (e.g., ssh, ssh-keygen) with graphical tools (e.g., PuTTY, Termius) and when to use each.]

---

### 8. Best Practices & Security?

[Explain]

- Use strong cryptographic keys.
- Avoid password authentication.
- Regularly update SSH software.
- Use multi-factor authentication.
- [Add more best practices as needed]

---
