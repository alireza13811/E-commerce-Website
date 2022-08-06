from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsCustomerOfThisUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.customer.id == view.kwargs['pk'])


class IsCartOfThisUser(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            pk = int(view.kwargs['pk'])
        except KeyError:
            pk = int(view.kwargs['cart_pk'])
        return bool(request.user and
                    (request.user.customer.cart.id == pk or
                     request.user.customer.cart.id == pk))
