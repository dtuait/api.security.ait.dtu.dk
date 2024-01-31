from .scripts.active_directory_get_inactive_computers import get_inactive_computers as _get_inactive_computers


def get_inactive_computers(days=30, base_dn='DC=win,DC=dtu,DC=dk'):
    return _get_inactive_computers(days=days, base_dn=base_dn)
    
