from common.django_utils.api_router_creator import ApiRouterCreator
from users.views.users_views.admin_users_pagination_view import AdminUsersPaginationView
from users.views.users_views.my_user_view import MyUserItemView
from users.views.users_views.update_my_timezone_view import UpdateMyTimezoneView
from users.views.users_views.update_my_user_view import UpdateMyUserView
from users.views.users_views.update_user_permissions_view import UpdateUserPermissionsView
from users.views.users_views.upload_user_profile_image_view import UploadUserProfileImageView

api, router = ApiRouterCreator.create_api_and_router('users')

MyUserItemView.register_get(router, 'my/')
AdminUsersPaginationView.register_get(router, 'by-admin/')
UpdateUserPermissionsView.register_post(router, 'by-admin/update-permissions/')
UpdateMyUserView.register_post(router, 'update-my-user/')
UpdateMyTimezoneView.register_post(router, 'update-my-timezone/')
UploadUserProfileImageView.register_post(router, 'upload-profile-image/')
