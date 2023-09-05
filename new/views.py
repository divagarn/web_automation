import paramiko
import sqlite3
import datetime
from django.shortcuts import render

def connect_to_device(ip):
    try:
        default_password = "haystack"
        default_uname = "haystack"
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=default_uname, password=default_password)

        with ssh_client.open_sftp() as sftp:
            remote_path = '/haystack_disinfect_report/database/disinfect_status_report.db'
            local_path = '/tmp/disinfect_status_report.db'  
            sftp.get(remote_path, local_path)

        conn = sqlite3.connect(local_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [row[0] for row in cursor.fetchall()]

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

        with ssh_client.open_sftp() as sftp:
            remote_path = '/haystack_disinfect_report/database/disinfect_status_report.db'
            local_path = '/tmp/disinfect_status_report.db'  
            sftp.get(remote_path, local_path)

        conn = sqlite3.connect(local_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in cursor.fetchall()]

        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()

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

        if table_name:
            columns, table_data = get_table_data(ip, table_name)

        # date filter
        today = datetime.date.today()
        today_date = today.strftime("%Y_%-m_%-d")
        filtered_data = []
        for row in table_data:
            if today_date == row[10]: 
                filtered_data.append(row)
        table_data = filtered_data
        print(table_data)
        print("f", filtered_data)

        return render(request, 'home.html', {'table_names': table_names, 'columns': columns, 'table_data': table_data})
    else:
        return render(request, 'home.html')