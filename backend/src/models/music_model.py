class MusicModel:
    def __init__(self):
        self._music = "none"

    def set_music(self, music: str) -> None:
        """Set the music type.

        Args:
            music: The music type. If empty or falsy,
                the method does nothing.

        Side effects:
            Updates `_music` with the music type.
        """
        # Focus mainly depends on beta waves
        if not music:
            return
        self._music = music

    def get_value(self) -> str:
        """Return the last-computed music type.

        Returns:
            str: The music type.
        """

        return self._music


music_service = MusicModel()
