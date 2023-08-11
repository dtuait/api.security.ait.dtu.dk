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
    sccmdbh.execute("USE CM_P01")


    sql_statement = """
SELECT DISTINCT TOP 1

    VRS.Netbios_Name0 as 'MachineName', 
    VRS.Last_Logon_Timestamp0 as 'LastLogon',
    VRS.CPUType0 as 'CPUType',
    VRS.Operating_System_Name_and0 as 'OperatingSystem', 
    VRS.Build01 as 'OSVesionBuild',
    VRS.User_Name0 as 'LastLogonUser',
    VRS.description0 as 'Description', 

    VCS.Model0 as 'Model',	
    VCS.ResourceID,  

    LDisk.Size0 as 'SystemDriveSize', 
    LDisk.FreeSpace0 as 'SystemDriveFree', 

    -- sccm agent status	
    ws.LastHWScan as 'LastTimeAgentTalkedToServer',

    -- TPM 
    v_GS_TPM.SpecVersion0 as 'TPMVersion',
    v_GS_TPM.IsActivated_InitialValue0 as 'TPMActivated',
    v_GS_TPM.IsEnabled_InitialValue0 as 'TPMEnabled',
    v_GS_TPM.IsOwned_InitialValue0 as 'TPMOwned',

    SecureBoot0 AS 'SecureBoot',
    UEFI0 AS 'UEFI',
        
    OS.LastBootUpTime0 AS 'LastBootTime',

    VENCVOL.DriveLetter0 as 'SystemDrive', 
    VENCVOL.ProtectionStatus0 as 'SystemDriveEncryption', 

    VENCL.ChassisTypes0 as 'ComputerType',

    VUMR.UniqueUserName as 'PrimaryUser'

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
    VRS.Netbios_Name0=?
"""

    # Execute the SQL statement
    try:

        
        cursor = sccmdbh.execute(sql_statement, computer_name)
        row = cursor.fetchone()
        
        columns = [column[0] for column in cursor.description]

        # Check if the row is None and return an appropriate error message
        if row is None:
            return None, f"No computer found with name {computer_name}"

        row_dict = dict(zip(columns, row))
        return row_dict, None


    except pyodbc.Error as e:
        print(f"Error: executing SQL statement: {e}")
        return None, f"Internal server error"
        




def run():
    computer_info = get_computer_info("MEK-425-222-02P")
    print(computer_info)




# if main 
if __name__ == "__main__":
    run()
