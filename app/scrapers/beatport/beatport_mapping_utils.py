import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from app.models import Release, Track
from app.models.artist_profile import ArtistProfile
from app.models.beatport_models import BeatportEntityType

logger = logging.getLogger(__name__)

# Constantes pour Beatport
BEATPORT_BASE_URL = "https://www.beatport.com"


class BeatportMappingUtils:
    """Utilitaires pour mapper les données Beatport vers nos modèles"""

    @staticmethod
    def build_url(entity_type: BeatportEntityType, slug: str, entity_id: Optional[int] = None) -> str:
        if entity_type == BeatportEntityType.SEARCH:
            encoded_query = quote(slug)
            return f"{BEATPORT_BASE_URL}/search?q={encoded_query}"
        elif entity_id is not None:
            return f"{BEATPORT_BASE_URL}/{entity_type.value}/{slug}/{entity_id}"
        else:
            return f"{BEATPORT_BASE_URL}/{entity_type.value}/{slug}"

    @staticmethod
    def extract_artist(artist_data: Dict[str, Any]) -> ArtistProfile:
        """Extrait les données d'un profil d'artiste depuis les données JSON"""
        try:
            # Deux formats: id/name ou artist_id/artist_name suivant la recherche ou release
            artist_id = artist_data.get("id", artist_data.get("artist_id", 0))
            name = artist_data.get("name", artist_data.get("artist_name", ""))
            slug = BeatportMappingUtils._build_slug(artist_data, name)
            url = BeatportMappingUtils.build_url(BeatportEntityType.ARTIST, slug, artist_id)

            avatar_url = BeatportMappingUtils._extract_image_url(artist_data, "artist")

            return ArtistProfile(
                id=artist_id,
                name=name,
                url=url,
                avatar_url=avatar_url
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du profil d'artiste: {str(e)}")
            raise

    @staticmethod
    def extract_track(track_data: Dict[str, Any]) -> Track:
        """Extrait les données d'un track depuis les données JSON"""
        try:
            # Support des deux formats: id/name ou track_id/track_name
            track_id = track_data.get("id", track_data.get("track_id", 0))
            title = track_data.get("name", track_data.get("track_name", ""))
            slug = BeatportMappingUtils._build_slug(track_data, title)
            url = BeatportMappingUtils.build_url(BeatportEntityType.TRACK, slug, track_id)
            release_date = BeatportMappingUtils._extract_date(track_data)
            genre = BeatportMappingUtils._extract_genre(track_data)
            bpm = track_data.get("bpm", None)
            play_count = track_data.get("plays", None)
            download_count = track_data.get("downloads", None)

            artwork_url = BeatportMappingUtils._extract_image_url(track_data, "track")
            # Si pas d'image de track, essayer l'image de la release associée
            if not artwork_url and "release" in track_data:
                artwork_url = BeatportMappingUtils._extract_image_url(track_data["release"], "release")

            artists, _ = BeatportMappingUtils._extract_artists_and_remixers(track_data)

            labels = []
            if "label" in track_data and isinstance(track_data["label"], dict):
                label_data = track_data["label"]
                labels = [BeatportMappingUtils.extract_label(label_data)]

            key = BeatportMappingUtils._extract_key(track_data)

            return Track(
                id=track_id,
                title=title,
                url=url,
                artwork_url=artwork_url,
                play_count=play_count,
                download_count=download_count,
                release_date=release_date,
                genre=genre,
                bpm=bpm,
                key=key,
                labels=labels,
                artists=artists,
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du track: {str(e)}")
            raise


    @staticmethod
    def extract_release(release_data: Dict[str, Any]) -> Release:
        """Extrait les données d'une release depuis les données JSON"""
        try:
            # Deux formats: id/name ou release_id/release_name suivant la recherche ou release
            release_id = release_data.get("id", release_data.get("release_id", 0))
            title = release_data.get("name", release_data.get("release_name", ""))
            slug = BeatportMappingUtils._build_slug(release_data, title)
            url = BeatportMappingUtils.build_url(BeatportEntityType.RELEASE, slug, release_id)
            release_date = BeatportMappingUtils._extract_date(release_data)
            track_count = release_data.get("track_count", 0)
            catalog_code = release_data.get("catalog_number", None)

            artwork_url = BeatportMappingUtils._extract_image_url(release_data, "release")

            artists, remixers = BeatportMappingUtils._extract_artists_and_remixers(release_data)

            if "label" in release_data:
                label = BeatportMappingUtils.extract_label(release_data["label"])

            return Release(
                id=release_id,
                title=title,
                url=url,
                artwork_url=artwork_url,
                release_date=release_date,
                track_count=track_count,
                catalog_code=catalog_code,
                label=label,
                artists=artists,
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de la release: {str(e)}")
            raise

    @staticmethod
    def extract_label(label_data: Dict[str, Any]) -> ArtistProfile:
        """Extrait les données d'un label depuis les données JSON"""
        try:
            # Deux formats: id/name ou label_id/label_name suivant la recherche ou release
            label_id = label_data.get("id", label_data.get("label_id", 0))
            name = label_data.get("name", label_data.get("label_name", ""))
            slug = BeatportMappingUtils._build_slug(label_data, name)
            url = BeatportMappingUtils.build_url(BeatportEntityType.LABEL, slug, label_id)

            avatar_url = BeatportMappingUtils._extract_image_url(label_data, "label")

            return ArtistProfile(
                id=label_id,
                name=name,
                url=url,
                avatar_url=avatar_url
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du label: {str(e)}")
            raise

    @staticmethod
    def _build_slug(data: Dict[str, Any], name: str) -> str:
        # Le slug est le nom de l'artiste ou du label en minuscule avec des espaces remplacés par des tirets
        slug = data.get("slug", "")
        if not slug and name:
            slug = name.lower().replace(" ", "-")
        return slug

    @staticmethod
    def _extract_image_url(data: Dict[str, Any], prefix: str) -> Optional[str]:
        # Fonction utilitaire pour remplacer les placeholders
        def replace_placeholders(url: str) -> str:
            return url.replace("{w}", "500").replace("{h}", "500")
            
        # Vérifier d'abord la structure avec "image"
        if "image" in data and isinstance(data["image"], dict):
            if "dynamic_uri" in data["image"]:
                return replace_placeholders(data["image"]["dynamic_uri"])
            elif "uri" in data["image"]:
                return data["image"]["uri"]
        
        # Sinon chercher l'URL statique
        image_key = f"{prefix}_image_uri"
        if image_key in data:
            return data.get(image_key)

        # Sinon chercher l'URL dynamique
        dynamic_key = f"{prefix}_image_dynamic_uri"
        if dynamic_key in data:
            return replace_placeholders(data.get(dynamic_key))

        return None

    @staticmethod
    def _extract_date(data: Dict[str, Any]) -> Optional[str]:
        if "release_date" in data:
            return data.get("release_date")
        elif "publish_date" in data:
            return data.get("publish_date")
        return None

    @staticmethod
    def _extract_genre(data: Dict[str, Any]) -> Optional[str]:
        if "genre" in data and isinstance(data["genre"], list) and len(data["genre"]) > 0:
            return data["genre"][0].get("genre_name")
        return None

    @staticmethod
    def _extract_artists_and_remixers(data: Dict[str, Any]) -> tuple[List[ArtistProfile], List[ArtistProfile]]:
        artists: List[ArtistProfile] = []
        remixers: List[ArtistProfile] = []

        if "artists" in data and isinstance(data["artists"], list):
            for artist_data in data["artists"]:
                # Vérifier si c'est un remixer
                is_remixer = "artist_type_name" in artist_data and artist_data.get("artist_type_name") == "Remixer"

                artist_obj = BeatportMappingUtils.extract_artist(artist_data)
                if is_remixer:
                    remixers.append(artist_obj)
                else:
                    artists.append(artist_obj)

        return artists, remixers
    
    @staticmethod
    def _extract_key(track_data):
        key = None
        if "key_name" in track_data:
            key = track_data.get("key_name", None)
        elif "key" in track_data and "key_name" in track_data["key"]:
            key = track_data["key"].get("key_name", None)
        return key