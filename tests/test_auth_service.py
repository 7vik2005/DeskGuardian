from pathlib import Path
import logging

from modules.auth.auth_service import AuthService


logger = logging.getLogger(__name__)


def test_auth_signup_duplicate_and_login(monkeypatch, tmp_path: Path):
    logger.info("TC05 Step 1: Configure temporary database for isolated auth testing")
    temp_db = tmp_path / "auth_test.db"
    monkeypatch.setattr("database.db_manager.DATABASE_NAME", str(temp_db))

    auth = AuthService()
    logger.info("TC05 Temp DB Path: %s", temp_db)

    logger.info("TC05 Step 2: Sign up a new user")
    user_id, err = auth.signup("alice", "pass1234", 24, "Engineer")
    assert err is None
    assert isinstance(user_id, int)
    logger.info("TC05 Signup Output: user_id=%s, err=%s", user_id, err)

    logger.info("TC05 Step 3: Attempt duplicate signup")
    dup_user_id, dup_err = auth.signup("alice", "newpass", 24, "Engineer")
    assert dup_user_id is None
    assert "exists" in dup_err.lower()
    logger.info("TC05 Duplicate Signup Output: user_id=%s, err=%s", dup_user_id, dup_err)

    logger.info("TC05 Step 4: Login with correct password")
    ok_user_id, ok_err = auth.login("alice", "pass1234")
    assert ok_err is None
    assert ok_user_id == user_id
    logger.info("TC05 Valid Login Output: user_id=%s, err=%s", ok_user_id, ok_err)

    logger.info("TC05 Step 5: Login with incorrect password")
    bad_user_id, bad_err = auth.login("alice", "wrongpass")
    assert bad_user_id is None
    assert "incorrect password" in bad_err.lower()
    logger.info("TC05 Invalid Login Output: user_id=%s, err=%s", bad_user_id, bad_err)

    auth.db.close()
    logger.info("TC05 Result: PASS")
