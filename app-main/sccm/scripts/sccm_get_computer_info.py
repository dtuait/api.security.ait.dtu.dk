import pyodbc
import os
import json

# Load .env file
# Import load_dotenv
from dotenv import load_dotenv
load_dotenv()


def get_computer_info(computer_name):
    # load env variables SCCM_USERNAME and SCCM_PASSWORD
    sccm_username = os.getenv("SCCM_USERNAME")
    sccm_password = os.getenv("SCCM_PASSWORD")


    # Check if computer_name is under a OU that the user's token has permission two

    final_dict = {
        "v_r_system": {},
        "v_add_remove_programs": [],
        "v_gs_computer_system": [],

    }
    row_dict = {}

    # Connection string
    connection_string = (
        r'DRIVER=/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.3.so.1.1;'
        'SERVER=ait-pcmdb01.win.dtu.dk,1433;'
        'TrustServerCertificate=yes;'
        f'UID={sccm_username};'
        f'PWD={sccm_password}'
    )

    # Connect to the SCCM database
    try:
        sccmdbh = pyodbc.connect(connection_string)
    except pyodbc.Error as e:
        print(f"Error connecting to the SCCM database: {e}")
        exit()

    # Execute the USE statement
    try:
        sccmdbh.execute("USE CM_P01")
    except pyodbc.Error as e:
        print(f"Error executing USE statement: {e}")
        return None, f"Internal server error"        


    # Find the resourceID of the computer
    try:
        sql = "SELECT ResourceID FROM v_R_System WHERE Netbios_Name0=?"
        cursor = sccmdbh.execute(sql, computer_name)
        row = cursor.fetchone()
        if row is None:
            return None, f"No computer found with name {computer_name}"
        resource_id = row[0]
    except pyodbc.Error as e:
        print(f"Error: executing SQL statement: {e}")
        return None, f"Internal server error"
    







    sql_statement_1 = """
SELECT DISTINCT TOP 1

    VRS.Netbios_Name0, 
    VRS.Last_Logon_Timestamp0,
    VRS.CPUType0,
    VRS.Operating_System_Name_and0, 
    VRS.Build01,
    VRS.User_Name0,
    VRS.description0, 

    VCS.Model0,	
    VCS.ResourceID,  

    LDisk.Size0, 
    LDisk.FreeSpace0, 

    -- sccm agent status	
    ws.LastHWScan,

    -- TPM 
    v_GS_TPM.SpecVersion0,
    v_GS_TPM.IsActivated_InitialValue0,
    v_GS_TPM.IsEnabled_InitialValue0,
    v_GS_TPM.IsOwned_InitialValue0,

    SecureBoot0,
    UEFI0,
        
    OS.LastBootUpTime0,

    VENCVOL.DriveLetter0, 
    VENCVOL.ProtectionStatus0, 

    VENCL.ChassisTypes0,

    VUMR.UniqueUserName

FROM 
    V_R_System VRS 

    LEFT JOIN v_GS_COMPUTER_SYSTEM VCS on VCS.ResourceID=VRS.ResourceID
    LEFT JOIN v_GS_Logical_Disk LDisk on LDisk.ResourceID = VRS.ResourceID

    -- sccm agent status
    LEFT JOIN v_GS_WORKSTATION_STATUS as ws ON VRS.ResourceID = ws.ResourceID

    -- TPM 
    LEFT JOIN v_GS_TPM ON VRS.ResourceID = v_GS_TPM.ResourceID

    -- UEFI
    LEFT JOIN v_GS_FIRMWARE AS fw ON VRS.ResourceID = fw.ResourceID

    -- last boot time
    LEFT JOIN v_GS_OPERATING_SYSTEM OS ON OS.ResourceID = VRS.ResourceID

    LEFT JOIN v_GS_ENCRYPTABLE_VOLUME VENCVOL ON VENCVOL.ResourceID = VRS.ResourceID
    LEFT JOIN v_GS_SYSTEM_ENCLOSURE VENCL on VENCL.ResourceID = VRS.ResourceID
    LEFT JOIN v_UserMachineRelationship VUMR on VRS.ResourceID=VUMR.MachineResourceID 
   
WHERE
    VRS.ResourceID=?
"""

    # Execute the SQL statement1
    try:

        
        cursor = sccmdbh.execute(sql_statement_1, resource_id)
        row = cursor.fetchone()
        
        columns = [column[0] for column in cursor.description]

        # Check if the row is None and return an appropriate error message
        if row is None:
            return None, f"No computer found with name {resource_id}"


    except pyodbc.Error as e:
        print(f"Error: executing SQL statement: {e}")
        return None, f"Internal server error"

    row_dict = dict(zip(columns, row))
    final_dict["v_r_system"] = row_dict
    




    



































    sql_statement_2 = """

    -- v_Add_Remove_Programs: This view contains information about software that has been discovered from the "Add or Remove Programs" data on a client computer.
    SELECT
        ARP.ResourceID,
        ARP.GroupID,
        ARP.RevisionID,
        ARP.AgentID,
        ARP.TimeStamp,
        ARP.ProdID0,
        ARP.DisplayName0,
        ARP.InstallDate0,
        ARP.Publisher0,
        ARP.Version0

    FROM 
        V_R_System VRS 
        LEFT JOIN v_Add_Remove_Programs AS ARP ON ARP.ResourceID=VRS.ResourceID
        

    WHERE
        VRS.ResourceID=?



    """


    # Execute the SQL statement2
    try:

        cursor2 = sccmdbh.execute(sql_statement_2, resource_id)
        
        
        columns2 = [column[0] for column in cursor2.description]

        rows2 = cursor2.fetchall()

        # Check if the row is None and return an appropriate error message
        if rows2 is None:
            return None, f"No computer found with resource_id {resource_id}"
        
        # Convert each row to dictionary and append to the list
        for row2 in rows2:
            row_dict2 = dict(zip(columns2, row2))
            final_dict["v_add_remove_programs"].append(row_dict2)


        

    
    except pyodbc.Error as e:
        print(f"Error: executing SQL statement: {e}")
        return None, f"Internal server error"









































































    sql_statement_3 = """

    -- v_GS_INSTALLED_SOFTWARE: This view provides details about installed software discovered by the hardware inventory client agent.

SELECT
GIS.ResourceID,
GIS.GroupID,
GIS.RevisionID,
GIS.AgentID,
GIS.TimeStamp,
GIS.ARPDisplayName0,
GIS.ChannelCode0,
GIS.ChannelID0,
GIS.CM_DSLID0,
GIS.EvidenceSource0,
GIS.InstallDate0,
GIS.InstallDirectoryValidation0,
GIS.InstalledLocation0,
GIS.InstallSource0,
GIS.InstallType0,
GIS.LocalPackage0,
GIS.MPC0,
GIS.OsComponent0,
GIS.PackageCode0,
GIS.ProductID0,
GIS.ProductName0,
GIS.ProductVersion0,
GIS.Publisher0,
GIS.RegisteredUser0,
GIS.Publisher0,
GIS.RegisteredUser0,
GIS.ServicePack0,
GIS.SoftwareCode0,
GIS.SoftwarePropertiesHash0,
GIS.UninstallString0,
GIS.UpgradeCode0,
GIS.VersionMajor0,
GIS.VersionMinor0
FROM 
V_R_System VRS 
LEFT JOIN v_GS_INSTALLED_SOFTWARE AS GIS ON GIS.ResourceID=VRS.ResourceID
WHERE 
	VRS.ResourceID=?





    """


    # Execute the SQL statement3
    try:

        cursor3 = sccmdbh.execute(sql_statement_3, resource_id)
        
        
        columns3 = [column[0] for column in cursor3.description]

        rows3 = cursor3.fetchall()

        # Check if the row is None and return an appropriate error message
        if rows3 is None:
            return None, f"No computer found with resource_id {resource_id}"
        
        # Convert each row to dictionary and append to the list
        for row3 in rows3:
            row_dict3 = dict(zip(columns3, row3))
            final_dict["v_gs_computer_system"].append(row_dict3)


        

    
    except pyodbc.Error as e:
        print(f"Error: executing SQL statement: {e}")
        return None, f"Internal server error"



























































    return final_dict, None








































































def run():
    computer_info, message = get_computer_info("MEK-425-222-02P")
    if message:
        print(message)
    else:
        print(computer_info)




# if main 
if __name__ == "__main__":
    run()
