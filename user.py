class User:
    def __init__(self, username, name, email, favorites):
        self.username = username
        self.name = name
        self.email = email
        self.favorites = favorites

    def add_favorites(self, club):
        if club in self.favorites:
            return False
        self.favorites.append(club)
        return True
