"""
Configuration globale des tests pour le projet.
"""
import pytest
import asyncio

# Remarque: ne pas définir la fixture event_loop, car elle est gérée par pytest-asyncio
# et configurée dans pytest.ini avec asyncio_default_fixture_loop_scope = function

# Autres fixtures utiles pour les tests peuvent être ajoutées ci-dessous 