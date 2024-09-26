# mypy: disable-error-code="misc"
from rest_framework import permissions

class HasPermission(permissions.BasePermission):
    permission_name: str = ''

    def has_permission(self, request, view):
        return request.user.has_perm(self.permission_name)


#Employee Permission
class CanAddEmployee(HasPermission):
    permission_name = 'api.add_employee'

class CanChangeEmployee(HasPermission):
    permission_name = 'api.change_employee'

class CanDeleteEmployee(HasPermission):
    permission_name = 'api.delete_employee'

class CanViewEmployee(HasPermission):
    permission_name = 'api.view_employee'

#Restaurant  Permission
class CanAddRestaurant(HasPermission):
    permission_name = 'api.add_restaurant'

class CanChangeRestaurant(HasPermission):
    permission_name = 'api.change_restaurant'

class CanDeleteRestaurant(HasPermission):
    permission_name = 'api.delete_restaurant'

class CanViewRestaurant(HasPermission):
    permission_name = 'api.view_restaurant'

#Menu Permission
class CanAddMenu(HasPermission):
    permission_name = 'api.add_menu'

class CanChangeMenu(HasPermission):
    permission_name = 'api.change_menu'

class CanDeleteMenu(HasPermission):
    permission_name = 'api.delete_menu'

class CanViewMenu(HasPermission):
    permission_name = 'api.view_menu'

class CanGetCurrentDayMenu(HasPermission):
    permission_name = 'api.get_current_day_menu'

class CanUploadMenu(HasPermission):
    permission_name = 'api.upload_menu'

#Vote Permission
class CanAddVote(HasPermission):
    permission_name = 'api.add_vote'

class CanChangeVote(HasPermission):
    permission_name = 'api.change_vote'

class CanDeleteVote(HasPermission):
    permission_name = 'api.delete_vote'

class CanViewVote(HasPermission):
    permission_name = 'api.view_vote'

class CanCastVote(HasPermission):
    permission_name = 'api.cast_vote'

class CanGetMyVote(HasPermission):
    permission_name = 'api.get_my_vote'

class CanGetAllVotesResults(HasPermission):
    permission_name = 'api.get_all_votes_results'
