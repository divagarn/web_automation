import paramiko
import sqlite3
from django.shortcuts import render

def connect_to_device(ip):
    try:
        default_password = "haystack"
        default_uname = "haystack"
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=default_uname, password=default_password)

        # Download the SQLite database file from the remote device
        with ssh_client.open_sftp() as sftp:
            remote_path = '/haystack_disinfect_report/database/disinfect_status_report.db'
            local_path = '/tmp/disinfect_status_report.db'  # Temporary local file
            sftp.get(remote_path, local_path)

        # Connect to the SQLite database and retrieve table names
        conn = sqlite3.connect(local_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [row[0] for row in cursor.fetchall()]

        # Close the SQLite connection and remove the temporary local file
        conn.close()
        ssh_client.close()

        return table_names
    except Exception as e:
        return str(e)

def get_table_data(ip, table_name="HAYSTACK_DISINFECT_REPORT"):
    try:
        default_password = "haystack"
        default_uname = "haystack"
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=default_uname, password=default_password)

        # Download the SQLite database file from the remote device
        with ssh_client.open_sftp() as sftp:
            remote_path = '/haystack_disinfect_report/database/disinfect_status_report.db'
            local_path = '/tmp/disinfect_status_report.db'  # Temporary local file
            sftp.get(remote_path, local_path)

        # Connect to the SQLite database and retrieve columns and all rows of the selected table
        conn = sqlite3.connect(local_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in cursor.fetchall()]

        # Retrieve all rows from the selected table
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()

        # Close the SQLite connection and remove the temporary local file
        conn.close()
        ssh_client.close()

        return columns, rows
    except Exception as e:
        return str(e)

def home(request):
    if request.method == 'POST':
        ip = request.POST.get('ip')
        table_name = request.POST.get('table_name')
        table_names = connect_to_device(ip)
        columns = []
        table_data = []
        date_filter = request.POST.get('date_filter')

        if table_name:
            columns, table_data = get_table_data(ip, table_name)

        # Apply the date filter if provided in "YYYY_MM_DD" format
        if date_filter and date_filter.strip():
            filtered_data = []
            for row in table_data:
                if date_filter == row[10]:  # Assuming "DATE" is the 11th column
                    filtered_data.append(row)
            table_data = filtered_data

        return render(request, 'home.html', {'table_names': table_names, 'columns': columns, 'table_data': table_data})
    else:
        return render(request, 'home.html')
