# SystemDiagPy

A Python-based tool for diagnosing system hardware, processes, and logs on Windows. This tool provides insights into system performance, installed software, and error logs, helping users troubleshoot and optimize their systems.

## Features

- Collect system information (CPU, RAM, disk space, etc.)
- Gather error and warning logs from the Windows Event Viewer
- List currently running processes with resource usage details
- Retrieve installed programs and their versions
- Save the diagnostic report to a text file

## Requirements

- Python 3.x
- Required Python packages:
  - `psutil`
  - `pywin32`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/SystemDiagPy.git
   cd SystemDiagPy
2. Install the required packages:
   ```bash
   pip install psutil pywin32
   
## Usage 
  ```bash
  pyton Diagnose.py
  ```
  After execution, the diagnostics report will be saved as 'system_diagnose.txt' in the same directory
  
##Contributing
  Contributions are welcome! Please open an issue or submit a pull request for any enhancements, bug fixes, or feature requests.

##License

This project is licensed under the MIT License. See the [LICENSE](License) file for details.

## Acknowledgments

- Special thanks to the contributors and the open-source community for providing the resources that made this project possible.
- Thanks to the maintainers of the following libraries that are used in this project:
  - [psutil](https://github.com/giampaolo/psutil) - Cross-platform library for retrieving information on running processes and system utilization (CPU, memory, disks, network, sensors).
  - [pywin32](https://github.com/mhammond/pywin32) - Python extensions for Windows.
