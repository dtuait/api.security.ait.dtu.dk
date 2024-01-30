from scripts.active_directory_get_soon_disabled_computers import get_soon_disabled_computers


def get_soon_disabled_computers(days=30, base_dn='DC=win,DC=dtu,DC=dk'):
    soon_disabled_computers = get_soon_disabled_computers(days=days, base_dn=base_dn)
    print(soon_disabled_computers)