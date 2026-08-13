import unittest
from services.auth_service import hash_password, verify_password, is_admin, is_manager, authenticate_user
from database.seed import seed_database

class TestAuthService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_database()

    def test_password_hashing_and_verification(self):
        password = "SecurePassword123"
        pwd_hash, salt = hash_password(password)
        self.assertTrue(verify_password(password, pwd_hash, salt))
        self.assertFalse(verify_password("WrongPassword", pwd_hash, salt))

    def test_role_permissions(self):
        admin_user = {"username": "admin", "role": "admin"}
        manager_user = {"username": "mgr", "role": "manager"}
        
        self.assertTrue(is_admin(admin_user))
        self.assertFalse(is_admin(manager_user))
        self.assertTrue(is_manager(manager_user))
        self.assertFalse(is_manager(admin_user))

    def test_role_specific_authentication(self):
        # Admin authentication test
        admin_user, msg = authenticate_user("admin", "admin123", required_role="admin")
        self.assertIsNotNone(admin_user)
        self.assertEqual(admin_user['role'], "admin")
        
        # Trying to log in admin as manager on manager portal should fail role check
        wrong_role_user, msg = authenticate_user("admin", "admin123", required_role="manager")
        self.assertIsNone(wrong_role_user)
        self.assertIn("Access denied", msg)

if __name__ == "__main__":
    unittest.main()
