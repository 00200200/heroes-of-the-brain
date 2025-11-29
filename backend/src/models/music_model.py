"""Music model for managing the recommended music type based on computed metrics.
"""

import logging


class MusicModel:
    """Model for managing the recommended music type based on computed metrics.
    """

    def __init__(self):
        self._music = "none"

    def set_music(self, music: str) -> None:
        """Set the music type.

        Args:
            music (str): The music type. If empty or falsy, the method does nothing.

        Side effects:
            Updates _music with the music type.
            Logs the change if a new music type is set.

        """
        if not music:
            return
        self._music = music
        logging.getLogger(__name__).info("Music type set to: %s", music)

    def get_value(self) -> str:
        """Return the last-computed music type.

        Returns:
            str: The music type.

        """
        return self._music

music_service = MusicModel()
