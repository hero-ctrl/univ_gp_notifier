Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Visastore\Downloads\Compressed\univ_gp_notifier"
WshShell.Run "python monitor.py", 0, False
