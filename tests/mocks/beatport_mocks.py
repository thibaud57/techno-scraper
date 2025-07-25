from pathlib import Path

import pytest
from httpx import Response

# Chemin vers les mocks de Beatport
BEATPORT_MOCKS_DIR = Path(__file__).parent / "responses" / "beatport"

# Réponse HTML de recherche améliorée au format attendu par le SearchScraper
BEATPORT_SEARCH_RESPONSE = """
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "dehydratedState": {
        "queries": [
          {
            "state": {
              "data": {
                "artists": {
                  "data": [
                    {
                      "id": 123456,
                      "name": "Test Artist",
                      "slug": "test-artist",
                      "url": "https://api-internal.beatportprod.com/v4/catalog/artists/123456/",
                      "image": {
                        "id": 789012,
                        "uri": "https://geo-media.beatport.com/image_size/590x404/test-artist-image.jpg",
                        "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-artist-image.jpg"
                      }
                    }
                  ]
                },
                "labels": {
                  "data": [
                    {
                      "id": 789012,
                      "name": "Test Label",
                      "slug": "test-label",
                      "url": "https://api-internal.beatportprod.com/v4/catalog/labels/789012/",
                      "image": {
                        "id": 345678,
                        "uri": "https://geo-media.beatport.com/image_size/500x500/test-label-image.jpg",
                        "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-label-image.jpg"
                      }
                    }
                  ]
                },
                "tracks": {
                  "data": [
                    {
                      "id": 555555,
                      "name": "Test Track",
                      "slug": "test-track",
                      "url": "https://api-internal.beatportprod.com/v4/catalog/tracks/555555/",
                      "release_date": "2025-03-15",
                      "artists": [
                        {
                          "id": 123456,
                          "name": "Test Artist",
                          "slug": "test-artist",
                          "url": "https://api-internal.beatportprod.com/v4/catalog/artists/123456/"
                        }
                      ],
                      "label": {
                        "id": 789012,
                        "name": "Test Label",
                        "slug": "test-label",
                        "url": "https://api-internal.beatportprod.com/v4/catalog/labels/789012/"
                      }
                    }
                  ]
                },
                "releases": {
                  "data": [
                    {
                      "id": 123456,
                      "name": "Test Release 1",
                      "slug": "test-release-1",
                      "url": "https://api-internal.beatportprod.com/v4/catalog/releases/123456/",
                      "publish_date": "2025-01-15",
                      "track_count": 3,
                      "image": {
                        "id": 111222,
                        "uri": "https://geo-media.beatport.com/image_size/1400x1400/test-release-image.jpg",
                        "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-release-image.jpg"
                      },
                      "artists": [
                        {
                          "id": 123456,
                          "name": "Test Artist",
                          "slug": "test-artist",
                          "url": "https://api-internal.beatportprod.com/v4/catalog/artists/123456/"
                        }
                      ],
                      "label": {
                        "id": 789012,
                        "name": "Test Label",
                        "slug": "test-label",
                        "url": "https://api-internal.beatportprod.com/v4/catalog/labels/789012/"
                      }
                    }
                  ]
                }
              }
            },
            "queryKey": ["search"]
          }
        ]
      }
    }
  }
}
</script>
"""

BEATPORT_ARTIST_RELEASES_RESPONSE = """
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "dehydratedState": {
        "queries": [
          {
            "state": {
              "data": {
                "results": [
                  {
                    "id": 123456,
                    "name": "Test Release 1",
                    "slug": "test-release-1",
                    "url": "https://api-internal.beatportprod.com/v4/catalog/releases/123456/",
                    "publish_date": "2025-01-15",
                    "track_count": 3,
                    "image": {
                      "id": 111222,
                      "uri": "https://geo-media.beatport.com/image_size/1400x1400/test-release-image.jpg",
                      "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-release-image.jpg"
                    },
                    "artists": [
                      {
                        "id": 654321,
                        "name": "Test Artist",
                        "slug": "test-artist",
                        "url": "https://api-internal.beatportprod.com/v4/catalog/artists/654321/",
                        "image": {
                          "id": 333444,
                          "uri": "https://geo-media.beatport.com/image_size/590x404/test-artist-image.jpg",
                          "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-artist-image.jpg"
                        }
                      }
                    ],
                    "label": {
                      "id": 555666,
                      "name": "Test Label",
                      "slug": "test-label",
                      "url": "https://api-internal.beatportprod.com/v4/catalog/labels/555666/",
                      "image": {
                        "id": 777888,
                        "uri": "https://geo-media.beatport.com/image_size/500x500/test-label-image.jpg",
                        "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-label-image.jpg"
                      }
                    }
                  }
                ]
              }
            },
            "queryKey": ["releases-page=1"]
          }
        ]
      }
    }
  }
}
</script>
"""

BEATPORT_ARTIST_RELEASES_WITH_FACETS_RESPONSE = """
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "dehydratedState": {
        "queries": [
          {
            "state": {
              "data": {
                "results": [
                  {
                    "id": 123456,
                    "name": "Test Release 1",
                    "slug": "test-release-1",
                    "url": "https://api-internal.beatportprod.com/v4/catalog/releases/123456/",
                    "publish_date": "2025-01-15",
                    "track_count": 3,
                    "image": {
                      "id": 111222,
                      "uri": "https://geo-media.beatport.com/image_size/1400x1400/test-release-image.jpg",
                      "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-release-image.jpg"
                    },
                    "artists": [
                      {
                        "id": 654321,
                        "name": "Test Artist",
                        "slug": "test-artist",
                        "url": "https://api-internal.beatportprod.com/v4/catalog/artists/654321/",
                        "image": {
                          "id": 333444,
                          "uri": "https://geo-media.beatport.com/image_size/590x404/test-artist-image.jpg",
                          "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-artist-image.jpg"
                        }
                      }
                    ],
                    "label": {
                      "id": 555666,
                      "name": "Test Label",
                      "slug": "test-label",
                      "url": "https://api-internal.beatportprod.com/v4/catalog/labels/555666/",
                      "image": {
                        "id": 777888,
                        "uri": "https://geo-media.beatport.com/image_size/500x500/test-label-image.jpg",
                        "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-label-image.jpg"
                      }
                    }
                  }
                ],
                "facets": {
                  "fields": {
                    "genre": [
                      {
                        "id": 5,
                        "name": "House",
                        "count": 70
                      },
                      {
                        "id": 12,
                        "name": "Deep House",
                        "count": 19
                      },
                      {
                        "id": 11,
                        "name": "Tech House",
                        "count": 21
                      }
                    ]
                  }
                }
              }
            },
            "queryKey": ["releases-page=1"]
          }
        ]
      }
    }
  }
}
</script>
"""

BEATPORT_LABEL_RELEASES_RESPONSE = """
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "dehydratedState": {
        "queries": [
          {
            "state": {
              "data": {
                "results": [
                  {
                    "id": 654321,
                    "name": "Test Release 2",
                    "slug": "test-release-2",
                    "url": "https://api-internal.beatportprod.com/v4/catalog/releases/654321/",
                    "publish_date": "2025-02-20",
                    "track_count": 2,
                    "image": {
                      "id": 999888,
                      "uri": "https://geo-media.beatport.com/image_size/1400x1400/test-release2-image.jpg",
                      "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-release2-image.jpg"
                    },
                    "artists": [
                      {
                        "id": 123789,
                        "name": "Another Artist",
                        "slug": "another-artist",
                        "url": "https://api-internal.beatportprod.com/v4/catalog/artists/123789/",
                        "image": {
                          "id": 456789,
                          "uri": "https://geo-media.beatport.com/image_size/590x404/another-artist-image.jpg",
                          "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/another-artist-image.jpg"
                        }
                      }
                    ],
                    "label": {
                      "id": 555666,
                      "name": "Test Label",
                      "slug": "test-label",
                      "url": "https://api-internal.beatportprod.com/v4/catalog/labels/555666/",
                      "image": {
                        "id": 777888,
                        "uri": "https://geo-media.beatport.com/image_size/500x500/test-label-image.jpg",
                        "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-label-image.jpg"
                      }
                    }
                  }
                ]
              }
            },
            "queryKey": ["releases-page=1"]
          }
        ]
      }
    }
  }
}
</script>
"""

# Réponse 404 pour tests d'erreurs
BEATPORT_404_RESPONSE = "Not Found"


@pytest.fixture
def mock_beatport_response_factory():
    """Factory pour créer des réponses HTTPX mock pour les tests Beatport"""

    def _create_response(status_code=200, text=None, html=None):
        if html:
            return Response(status_code, text=html)
        return Response(status_code, text=text or "")

    return _create_response


@pytest.fixture
def mock_beatport_release_data():
    """Données de release Beatport pour les tests"""
    return {
        "id": 123456,
        "name": "Test Release 1",
        "slug": "test-release-1",
        "publish_date": "2025-01-15",
        "track_count": 3,
        "image": {
            "uri": "https://geo-media.beatport.com/image_size/1400x1400/test-release-image.jpg",
            "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-release-image.jpg"
        },
        "artists": [
            {
                "id": 654321,
                "name": "Test Artist",
                "slug": "test-artist",
                "image": {
                    "uri": "https://geo-media.beatport.com/image_size/590x404/test-artist-image.jpg",
                    "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-artist-image.jpg"
                }
            }
        ],
        "label": {
            "id": 555666,
            "name": "Test Label",
            "slug": "test-label",
            "image": {
                "uri": "https://geo-media.beatport.com/image_size/500x500/test-label-image.jpg",
                "dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-label-image.jpg"
            }
        }
    }


@pytest.fixture
def mock_beatport_specific_format_release_data():
    """
        Données de release Beatport spécifique pour les tests
        Par ex: "release_id" à la place de "id"
    """
    return {
        "release_id": 123456,
        "release_name": "Test Release 1",
        "slug": "test-release-1",
        "release_date": "2025-01-15",
        "track_count": 3,
        "release_image_uri": "https://geo-media.beatport.com/image_size/1400x1400/test-release-image.jpg",
        "release_image_dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-release-image.jpg",
        "artists": [
            {
                "artist_id": 654321,
                "artist_name": "Test Artist",
                "slug": "test-artist",
                "artist_image_uri": "https://geo-media.beatport.com/image_size/590x404/test-artist-image.jpg",
                "artist_image_dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-artist-image.jpg"
            }
        ],
        "label": {
            "label_id": 555666,
            "label_name": "Test Label",
            "slug": "test-label",
            "label_image_uri": "https://geo-media.beatport.com/image_size/500x500/test-label-image.jpg",
            "label_image_dynamic_uri": "https://geo-media.beatport.com/image_size/{w}x{h}/test-label-image.jpg"
        }
    }
