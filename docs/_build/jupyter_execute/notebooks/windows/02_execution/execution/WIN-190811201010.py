# WMI Module Load

## Metadata


|               |    |
|:--------------|:---|
| id            | WIN-190811201010 |
| author        | Roberto Rodriguez @Cyb3rWard0g |
| creation date | 2019/08/11 |
| platform      | Windows |
| playbook link |  |
        

## Technical Description
WMI is the Microsoft implementation of the Web-Based Enterprise Management (WBEM) and Common Information Model (CIM).
Both standards aim to provide an industry-agnostic means of collecting and transmitting information related to any managed component in an enterprise. An example of a managed component in WMI would be a running process, registry key, installed service, file information, etc.
At a high level, Microsoft’s implementation of these standards can be summarized as follows > Managed Components Managed components are represented as WMI objects — class instances representing highly structured operating system data. Microsoft provides a wealth of WMI objects that communicate information related to the operating system. E.g. Win32_Process, Win32_Service, AntiVirusProduct, Win32_StartupCommand, etc.
WMI modules loaded by legit processes such as wmiprvse.exe or wmiapsrv.exe are the following

C:\Windows\System32\wmiclnt.dll
C:\Windows\System32\wbem\WmiApRpl.dll
C:\Windows\System32\wbem\wmiprov.dll
C:\Windows\System32\wbem\wmiutils.dll
Adversaries could leverage the WMI modules above to execute WMI tasks bypassing controls looking for wmiprvse.exe or wmiapsrv.exe activity.

## Hypothesis
Adversaries might be leveraging WMI modules to execute WMI tasks bypassing controls monitoring for wmiprvse.exe or wmiapsrv.exe activity

## Analytics

### Initialize Analytics Engine

from openhunt.mordorutils import *
spark = get_spark()

### Download & Process Mordor File

mordor_file = "https://raw.githubusercontent.com/hunters-forge/mordor/master/datasets/small/windows/defense_evasion/empire_psinject.tar.gz"
registerMordorSQLTable(spark, mordor_file, "mordorTable")

### Analytic I


| FP Rate  | Log Channel | Description   |
| :--------| :-----------| :-------------|
| Low       | ['Microsoft-Windows-Sysmon/Operational']          | Look for processes (non wmiprvse.exe or WmiApSrv.exe) loading wmi modules            |
            

df = spark.sql(
    '''
SELECT `@timestamp`, computer_name, Image, ImageLoaded
FROM mordorTable
WHERE channel = "Microsoft-Windows-Sysmon/Operational"
    AND event_id = 7
    AND (
        lower(ImageLoaded) LIKE "%wmiclnt.dll"
        OR lower(ImageLoaded) LIKE "%WmiApRpl.dll"
        OR lower(ImageLoaded) LIKE "%wmiprov.dll"
        OR lower(ImageLoaded) LIKE "%wmiutils.dll"
        OR lower(ImageLoaded) LIKE "%wbemcomn.dll"
        OR lower(ImageLoaded) LIKE "%WMINet_Utils.dll"
        OR lower(ImageLoaded) LIKE "%wbemsvc.dll"
        OR lower(ImageLoaded) LIKE "%fastprox.dll"
        OR lower(Description) LIKE "%wmi%"
    )
    AND NOT (
        lower(Image) LIKE "%wmiprvse.exe"
        OR lower(Image) LIKE "%wmiapsrv.exe"
        OR lower(Image) LIKE "%svchost.exe"
    )
    '''
)
df.show(10,False)

## Detection Blindspots


## Hunter Notes
* Stack the processes loading WMI modules and document the activity in your environment.
* Stack child processes (if any) of non wmiprvse.exe loading wmi modules

## Hunt Output

| Category | Type | Name     |
| :--------| :----| :--------|
| signature | SIGMA | [sysmon_wmi_module_load](https://github.com/hunters-forge/ThreatHunter-Playbook/blob/master/signatures/sigma/sysmon_wmi_module_load.yml) |

## References
* https://posts.specterops.io/threat-hunting-with-jupyter-notebooks-part-4-sql-join-via-apache-sparksql-6630928c931e
* https://posts.specterops.io/real-time-sysmon-processing-via-ksql-and-helk-part-3-basic-use-case-8fbf383cb54f