
from . import active_directory_get_computer_info as ad_get_computer_info


def get_computer_info(computer_name):
    return {"computer_name": computer_name}, None


def run():
    computer_info, message = get_computer_info("DTU-CND1363SBJ")
    if message:
        print(message)
    else:
        print(computer_info)




# if main 
if __name__ == "__main__":
    run()
