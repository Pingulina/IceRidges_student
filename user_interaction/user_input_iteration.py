# function to get the user input defining interation over year/season/location/week/etc

def get_user_input_iteration(index, max_index):
    user_input = input()
    success = 1
    if user_input == 'f':
        index += 1
    elif user_input == 'd':
        index == index
    elif user_input == 's':
        index -= 1
    elif user_input == 'x':
        success = -1
        return success, index
    # if the week number is entered directly, set the week to the entered number
    elif user_input.isdigit():
        index = int(user_input)
    else:
        print("Invalid input.")
        success = 0
        return success, index

    if index < 0:
        # week is negative, set it to the last week
        index = max_index-1
    elif index >= max_index:
        # week is too large, set it to the first week
        index = 0

    return success, index