from rest_framework.routers import DefaultRouter

from .views.restaurant_views import RestaurantViewSet
from .views.menu_views import MenuViewSet
from .views.employee_views import EmployeeViewSet
from .views.vote_views import VoteViewSet

router = DefaultRouter()
router.register('restaurants', RestaurantViewSet)
router.register('menus', MenuViewSet)
router.register('employees', EmployeeViewSet)
router.register('votes', VoteViewSet)

urlpatterns = router.urls