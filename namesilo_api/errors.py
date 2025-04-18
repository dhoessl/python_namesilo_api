class RecordError(Exception):
    generic_message = "Generic Record Error"

    def __init__(self, *args) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = RecordError.generic_message

    def __str__(self) -> str:
        return self.message


class NamesiloAPIError(Exception):
    generic_message = "Generic Namesilo API Error"

    def __init__(self, *args) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = NamesiloAPIError.generic_message

    def __str__(self) -> str:
        return self.message


# NOTE: currently not in use. might be used later and move
# to the acutall file
# class NamesiloAPIConnectionError(NamesiloAPIError):
#     def __init__(self, *args) -> None:
#         if args:
#             self.message = args[0]
#         else:
#             self.message = NamesiloAPIError.generic_message
#
#     def __str__(self) -> str:
#         return self.message
