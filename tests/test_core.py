"""Tests for Contractiq."""
from src.core import Contractiq
def test_init(): assert Contractiq().get_stats()["ops"] == 0
def test_op(): c = Contractiq(); c.manage(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Contractiq(); [c.manage() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Contractiq(); c.manage(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Contractiq(); r = c.manage(); assert r["service"] == "contractiq"
