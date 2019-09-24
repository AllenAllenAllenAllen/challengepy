class User:
    """
    This class is for modelling a user
    """
    def __init__(self, username, name, email, favorites):
        self.username = username
        self.name = name
        self.email = email
        self.favorites = favorites # courses that a user likes

    def add_favorites(self, club):
        """
        Add a club into user's profile
        :param club: club name
        :return: true if successfully added; false if already added
        """
        if club in self.favorites:
            return False
        self.favorites.append(club)
        return True
