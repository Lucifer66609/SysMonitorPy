import platform
import psutil
import socket
from datetime import datetime
import win32evtlog
import win32evtlogutil
import pywintypes
import winreg

# Funktion, um Systeminformationen zu sammeln
def get_system_info():
    info = {}

    # Systeminformationen
    info['System'] = platform.system()
    info['Rechnername'] = socket.gethostname()
    info['Rechner-IP'] = socket.gethostbyname(socket.gethostname())
    info['Release'] = platform.release()
    info['Version'] = platform.version()
    info['Architektur'] = platform.machine()

    # CPU-Informationen
    info['CPU'] = platform.processor()
    info['CPU-Kerne (Physisch)'] = psutil.cpu_count(logical=False)
    info['CPU-Kerne (Logisch)'] = psutil.cpu_count(logical=True)
    info['Aktuelle CPU-Auslastung (%)'] = psutil.cpu_percent(interval=1)

    # RAM-Informationen
    virtual_memory = psutil.virtual_memory()
    info['Gesamter RAM (GB)'] = round(virtual_memory.total / (1024**3), 2)
    info['Verwendeter RAM (GB)'] = round(virtual_memory.used / (1024**3), 2)
    info['Verfügbarer RAM (GB)'] = round(virtual_memory.available / (1024**3), 2)

    # Festplatteninformationen
    disk_usage = psutil.disk_usage('/')
    info['Gesamter Speicher (GB)'] = round(disk_usage.total / (1024**3), 2)
    info['Verwendeter Speicher (GB)'] = round(disk_usage.used / (1024**3), 2)
    info['Verfügbarer Speicher (GB)'] = round(disk_usage.free / (1024**3), 2)
    info['Speicher-Auslastung (%)'] = disk_usage.percent

    # Netzwerkinformationen
    net_info = psutil.net_if_addrs()
    interfaces = {}
    for interface_name, addresses in net_info.items():
        for address in addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                interfaces[interface_name] = address.address

    info['Netzwerk Interfaces'] = interfaces

    # Batterieinformationen (falls vorhanden)
    try:
        battery = psutil.sensors_battery()
        if battery:
            info['Batterie-Prozent'] = battery.percent
            info['Netzbetrieb'] = battery.power_plugged
    except AttributeError:
        info['Batterie'] = "Keine Batterieinformationen verfügbar"

    return info

# Funktion, um Windows-Ereignisprotokolle zu sammeln
def get_windows_event_logs(log_type='System', event_types=[win32evtlog.EVENTLOG_ERROR_TYPE, win32evtlog.EVENTLOG_WARNING_TYPE]):
    logs = []
    server = 'localhost'
    log_handle = win32evtlog.OpenEventLog(server, log_type)

    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    total = win32evtlog.GetNumberOfEventLogRecords(log_handle)

    while True:
        events = win32evtlog.ReadEventLog(log_handle, flags, 0)
        if not events:
            break

        for event in events:
            if event.EventType in event_types:
                # Konvertierung von pywintypes.datetime zu datetime
                try:
                    event_time = datetime.fromtimestamp(event.TimeGenerated.timestamp())
                except AttributeError:
                    # Fallback für pywintypes.datetime
                    event_time = event.TimeGenerated

                logs.append({
                    'Zeit': event_time,
                    'Quelle': event.SourceName,
                    'Ereignistyp': 'Fehler' if event.EventType == win32evtlog.EVENTLOG_ERROR_TYPE else 'Warnung',
                    'Ereignisbeschreibung': win32evtlogutil.SafeFormatMessage(event, log_type)
                })

    win32evtlog.CloseEventLog(log_handle)
    return logs

# Funktion, um laufende Prozesse zu sammeln
def get_running_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            processes.append({
                'PID': proc.info['pid'],
                'Name': proc.info['name'],
                'CPU-Auslastung (%)': proc.info['cpu_percent'],
                'RAM-Auslastung (%)': proc.info['memory_percent'],
                'Status': proc.info['status']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes

# Funktion, um installierte Programme zu sammeln (nur Windows)
def get_installed_programs():
    programs = []
    reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
    except FileNotFoundError:
        return programs

    for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
        try:
            sub_key_name = winreg.EnumKey(reg_key, i)
            sub_key = winreg.OpenKey(reg_key, sub_key_name)
            name, version = None, None
            try:
                name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                version = winreg.QueryValueEx(sub_key, "DisplayVersion")[0]
            except FileNotFoundError:
                pass
            if name:
                programs.append({
                    'Programmname': name,
                    'Version': version
                })
        except FileNotFoundError:
            continue
    return programs

# Funktion, um die gesammelten Informationen in eine Datei zu schreiben
def write_diagnosis_to_file(info, logs, processes, programs):
    with open("system_diagnose.txt", "w", encoding="utf-8") as file:
        file.write(f"Systemdiagnosebericht - {datetime.now()}\n")
        file.write("="*40 + "\n")
        for key, value in info.items():
            if isinstance(value, dict):
                file.write(f"{key}:\n")
                for sub_key, sub_value in value.items():
                    file.write(f"  {sub_key}: {sub_value}\n")
            else:
                file.write(f"{key}: {value}\n")
            file.write("="*40 + "\n")

        # Fehler- und Warnungsprotokolle
        file.write("\nFehler- und Warnungsprotokolle:\n")
        file.write("="*40 + "\n")
        if logs:
            for log in logs:
                file.write(f"Zeit: {log['Zeit']}\n")
                file.write(f"Quelle: {log['Quelle']}\n")
                file.write(f"Ereignistyp: {log['Ereignistyp']}\n")
                file.write(f"Ereignisbeschreibung: {log['Ereignisbeschreibung']}\n")
                file.write("="*40 + "\n")
        else:
            file.write("Keine Fehler oder Warnungen gefunden.\n")

        # Laufende Prozesse
        file.write("\nLaufende Prozesse:\n")
        file.write("="*40 + "\n")
        for process in processes:
            file.write(f"Name: {process['Name']}, PID: {process['PID']}, CPU-Auslastung: {process['CPU-Auslastung (%)']}%, RAM-Auslastung: {process['RAM-Auslastung (%)']}%, Status: {process['Status']}\n")
        file.write("="*40 + "\n")

        # Installierte Programme
        file.write("\nInstallierte Programme:\n")
        file.write("="*40 + "\n")
        for program in programs:
            file.write(f"Programmname: {program['Programmname']}, Version: {program['Version']}\n")
        file.write("="*40 + "\n")

if __name__ == "__main__":
    # Systeminformationen sammeln
    system_info = get_system_info()

    # Fehler und Warnungen aus dem Windows-Ereignisprotokoll sammeln
    event_logs = get_windows_event_logs()

    # Laufende Prozesse sammeln
    running_processes = get_running_processes()

    # Installierte Programme sammeln
    installed_programs = get_installed_programs()

    # Diagnoseinformationen in eine Datei schreiben
    write_diagnosis_to_file(system_info, event_logs, running_processes, installed_programs)

    print("Systemdiagnose abgeschlossen. Informationen wurden in 'system_diagnose.txt' gespeichert.")