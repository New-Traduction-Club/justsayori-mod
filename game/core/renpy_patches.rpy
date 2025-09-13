







init -1 python:



    if renpy.version_tuple >= (7, 4, 5, 1648):
        config.gl2 = False




python early:
    import os
    os.environ['wmic process get Description'] = "powershell (Get-Process).ProcessName"
    os.environ['wmic os get version'] = "powershell (Get-WmiObject -class Win32_OperatingSystem).Version"


    if renpy.version_tuple >= (7, 4, 7, 1862):
        config.atl_start_on_show = False 
