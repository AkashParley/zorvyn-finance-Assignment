import pytest
from app.core.roles import UserRole, has_permission, ROLE_PERMISSIONS


class TestRolePermissions:

    def test_viewer_can_read_records(self):
        assert has_permission(UserRole.VIEWER, "read:records") is True

    def test_viewer_cannot_create_records(self):
        assert has_permission(UserRole.VIEWER, "create:records") is False

    def test_viewer_cannot_manage_users(self):
        assert has_permission(UserRole.VIEWER, "manage:users") is False

    def test_analyst_can_read_insights(self):
        assert has_permission(UserRole.ANALYST, "read:insights") is True

    def test_analyst_cannot_create_records(self):
        assert has_permission(UserRole.ANALYST, "create:records") is False

    def test_admin_has_all_permissions(self):
        all_perms = set().union(*ROLE_PERMISSIONS.values())
        for perm in all_perms:
            assert has_permission(UserRole.ADMIN, perm) is True, f"Admin missing: {perm}"

    def test_unknown_permission_returns_false(self):
        assert has_permission(UserRole.ADMIN, "destroy:everything") is False

    def test_role_hierarchy_is_additive(self):
        viewer_perms = ROLE_PERMISSIONS[UserRole.VIEWER]
        analyst_perms = ROLE_PERMISSIONS[UserRole.ANALYST]
        admin_perms = ROLE_PERMISSIONS[UserRole.ADMIN]
        assert viewer_perms.issubset(analyst_perms)
        assert analyst_perms.issubset(admin_perms)
