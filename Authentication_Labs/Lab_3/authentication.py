class AuthenticationBruteForce:
    """Reusable code to solve Portswigger Authentication labs"""

    def __init__(
        self,
        endpoint: str,
        username_file: str,
        password_file: str,
        error_message: str = "Invalid username",
    ):
        """Initialize attributes to initiate requests"""
        self.endpoint = endpoint
        self.username_list = username_file
        self.password_file = password_file
        self.error_message = error_message

    def _read_wordfile(self, wordfile: str) -> list[str]:
        """Initialize attributes needed to complete requests"""
        try:
            