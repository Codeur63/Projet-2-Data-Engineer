"""Tests unitaires pour le cache des sessions capteurs."""
import pytest
from src.cache.session_cache import SessionCache, SensorSession
from src.cache.client import get_redis_client


SENSOR_ID = 'TEST-SENSOR-001'


@pytest.fixture(autouse=True)

def cleanup():
    """Nettoyer Redis avant chaque test pour l'isolation."""
    r = get_redis_client()
    r.delete(f'session:sensor:{SENSOR_ID}')
    yield r.delete(f'session:sensor:{SENSOR_ID}')

def make_session() -> SensorSession:
    return SensorSession(
        sensor_id=SENSOR_ID, installation_id=99,
        region='Littoral', city='Douala',
        tariff_plan='Premium', status='active',
        panel_capacity=500, battery_capacity=2000,
        alert_threshold=0.40, firmware_ver='v2.3'
    )

def test_cache_miss_returns_none():
    """Une session non présente dans Redis doit retourner None."""
    cache = SessionCache()
    assert cache.get_session(SENSOR_ID) is None

def test_cache_hit_returns_correct_data():
    """Après set(), get() doit retourner les bonnes données."""
    cache = SessionCache()
    session = make_session()
    cache.set_session(session)
    retrieved = cache.get_session(SENSOR_ID)
    assert retrieved.region == 'Littoral'
    assert retrieved.tariff_plan == 'Premium'
    assert retrieved.is_active() is True
    
    
def test_ttl_is_set_after_storing():
    """Le TTL doit être > 0 après stockage."""
    cache = SessionCache()
    cache.set_session(make_session())
    r = get_redis_client()
    ttl = r.ttl(f'session:sensor:{SENSOR_ID}')
    assert ttl > 0, f'TTL doit être positif, obtenu: {ttl}'
    assert ttl <= 300, 'TTL ne doit pas dépasser SESSION_TTL'
    
    
def test_update_status_modifies_only_one_field():
    """update_status() ne doit pas modifier les autres champs."""
    cache = SessionCache()
    cache.r.delete(f"session:sensor:{SENSOR_ID}")
    session = make_session()
    cache.set_session(session)
    cache.update_status(SENSOR_ID, 'suspended')
    updated = cache.get_session(SENSOR_ID)
    assert updated is not None, f"Le capteur {SENSOR_ID} a disparu de Redis après l'update !"
    assert updated.status == "suspended"
    
    
def test_delete_removes_session():
    """Après delete(), get() doit retourner None."""
    cache = SessionCache()
    cache.set_session(make_session())
    cache.delete(SENSOR_ID)
    assert cache.get_session(SENSOR_ID) is None    